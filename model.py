import asyncio
from ocr import extract_text
from langchain.text_splitter import RecursiveCharacterTextSplitter
from cch import add_chunk_header
from vector_db import VectorDatabase

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq



MAX_CONTENT_TOKENS = 4000
GROQ_MODEL_NAME = "llama3-8b-8192"

BADWORDS = ", ".join(["vacuous", "moron", "idiot", "ridiculous", "brainless"])

SYSTEM = '''
You are a helpful AI Assistant for the employees of Gas Authority of India Limited (GAIL).
Answer the user query to the best of your abilities. Keep the answer under 100 words.
Strictly avoid the use of unprofessional words like {bad_words}.
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


GROQ_API_KEY = "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"



def get_text_chunks(text: str):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return text_splitter.split_text(text)


async def add_document(file_path: str, file_name: str):
    print("extracting text...")
    text = extract_text(file_path)

    print("creating chunks...")
    chunks = get_text_chunks(text=text)
    chunks_with_headers = []
    print(f'created {len(chunks)} chunks...')


    print("creating chunk headers...")
    for i, chunk in enumerate(chunks):
        chunks_with_headers.append(add_chunk_header(doc_title=file_name, content=chunk, GROQ_API_KEY=GROQ_API_KEY))
        print("created chunk header", i+1)
    print("created chunk headers")


    print("creating embeddings...")
    chroma_db = VectorDatabase()
    await chroma_db.add_to_vector_store(chunks=chunks_with_headers)
    


async def llm_response(query: str):
    chroma_db = VectorDatabase()
    similar_chunks = await chroma_db.query_vector_store(query=query, n_results=3)

    relevant_data = similar_chunks["documents"][0]

    print("number of similar chunks found:", len(relevant_data))

    for data in relevant_data:
        print(data)

    while len(relevant_data) < 3:
        relevant_data.append("No more relevant data found.")


    chat = ChatGroq(temperature=0, groq_api_key=GROQ_API_KEY, model_name=GROQ_MODEL_NAME, max_tokens=MAX_CONTENT_TOKENS, max_retries=2)

    prompt = ChatPromptTemplate.from_messages([("system", SYSTEM), ("human", HUMAN)])


    chain = prompt | chat
    response = chain.invoke({"bad_words": BADWORDS, "context_1": relevant_data[0], "context_2": relevant_data[1], "context_3": relevant_data[2], "text":query})
    
    print(response)

    return response.content
    # return "hiiiiiiiiii"



async def main():
    await add_document("Compendium_Book.pdf", "Systemic improvements for GAIL suggested by Vigilance 2020")
    
    # print("generating response...")
    # response = await llm_response(input("Enter your query: "))
    # print("RESPONSE GENERATED")

    # print()

    # print(response)


if __name__ == "__main__":
    asyncio.run(main())