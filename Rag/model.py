import asyncio
from Rag.ocr import extract_text
from langchain.text_splitter import RecursiveCharacterTextSplitter
from cch import add_chunk_header
from vector_db import VectorDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from concurrent.futures import ThreadPoolExecutor
from itertools import cycle
import os
from dotenv import load_dotenv

load_dotenv()
GROQ_MODEL_NAME = "llama3-8b-8192"# os.getenv("GROQ_MODEL_NAME")
MAX_CONTENT_TOKENS = 4000

GROQ_API_KEYS = os.environ["GROQ_API_KEYS_str"]
# os.getenv("GROQ_API_KEYS_str")

# print(GROQ_API_KEYS)
GROQ_API_KEY_CYCLE = cycle(GROQ_API_KEYS)
SYSTEM_DICT_FILE='system_dict.txt'

def get_all_words(file_path):
    try:
        with open(file_path, "r") as file:
            # Read all lines, strip whitespace, and return as a list
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []

# Get all words from the dictionary
all_words = get_all_words(SYSTEM_DICT_FILE)[-7:]
# BADWORDS = ", ".join(["vacuous", "moron", "idiot", "ridiculous", "brainless"])


BADWORDS=','.join(all_words)
print(BADWORDS)

SYSTEM = '''
You are a helpful AI Assistant for the employees of Gas Authority of India Limited (GAIL).
Answer the user query to the best of your abilities. Keep the answer under 100 words.
Strictly avoid the use of unprofessional words like {bad_words}. Instead use words of similar meaning that can be used professionally.
You are given with three chunks of text related to the query. Use the chunks to give the answer.
If the chunks are not related to the query, say that you did not find any relevant documents. Do not make any assumptions.
Do not give any information not in the chunks. Also do not mention chunks in the answer.


CHUNK 1:
{context_1}


CHUNK 2:
{context_2}


CHUNK 3:
{context_3}
'''.strip()

HUMAN = "{text}"


SUMMARY_SYSTEM = '''You are an AI Assistant that summarizes large texts to make it short and concise. 
Keep the summary easy to read.'''

SUMMARY_HUMAN = '''Summarize this text for me:
Title: {filename}
{text}'''





def get_text_chunks(text: str):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return text_splitter.split_text(text)


async def summarize(file_path: str, file_name: str, text: str) -> None:
    chat = ChatGroq(temperature=0, groq_api_key=next(GROQ_API_KEY_CYCLE), model_name=GROQ_MODEL_NAME, max_tokens=MAX_CONTENT_TOKENS, max_retries=2)

    prompt = ChatPromptTemplate.from_messages([("system", SUMMARY_SYSTEM), ("human", SUMMARY_HUMAN)])

    
    chain = prompt | chat
    response = chain.invoke({"filename": file_name, "text":text[:8000]})
    print(response)

    with open(f'summaries/{file_name[:-3]}txt', 'w') as f:
        f.write(response.content)


async def add_document(file_path: str, file_name: str):
    print("extracting text...")
    text = extract_text(file_path)
    await summarize(file_path=file_path, file_name=file_name, text=text)

    print("creating chunks...")
    chunks = get_text_chunks(text=text)
    chunks_with_headers = []
    print(f'created {len(chunks)} chunks...')


    file_name=file_name

    print("creating chunk headers...")
    
    li = list(range(len(chunks)))

    def process_chunk(chunk, i):
        print("creating chunk", i+1)
        return add_chunk_header(doc_title=file_name, content=chunk, GROQ_API_KEY=next(GROQ_API_KEY_CYCLE))
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(process_chunk, chunks, li)
    
    chunks_with_headers.extend(results)    

    print("created chunk headers")
    print(chunks_with_headers[:5])


    print("creating embeddings...")
    chroma_db = VectorDatabase()
    await chroma_db.add_to_vector_store(chunks=chunks_with_headers)
    print("embeddings created")
    


async def llm_response(query: str):
    chroma_db = VectorDatabase()
    similar_chunks = await chroma_db.query_vector_store(query=query, n_results=3)

    relevant_data = similar_chunks["documents"][0]

    print("number of similar chunks found:", len(relevant_data))

    for data in relevant_data:
        print(data)

    while len(relevant_data) < 3:
        relevant_data.append("No more relevant data found.")


    chat = ChatGroq(temperature=0, groq_api_key=next(GROQ_API_KEY_CYCLE), model_name=GROQ_MODEL_NAME, max_tokens=MAX_CONTENT_TOKENS, max_retries=2)

    prompt = ChatPromptTemplate.from_messages([("system", SYSTEM), ("human", HUMAN)])


    chain = prompt | chat
    response = chain.invoke({"bad_words": BADWORDS, "context_1": relevant_data[0], "context_2": relevant_data[1], "context_3": relevant_data[2], "text":query})
    
    print(response)

    return response.content
    # return "hiiiiiiiiii"



async def main():
    await add_document("CCMP_DOC_1.pdf", "An o")
    
    # print("generating response...")
    # response = await llm_response(input("Enter your query: "))
    # print("RESPONSE GENERATED")

    # print()

    # print(response)


if __name__ == "__main__":
    asyncio.run(main())