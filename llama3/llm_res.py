from langchain_ollama import OllamaLLM


def setup_model():
    model =OllamaLLM(model='llama3')
    return model

# async def llm_response(query, model):
   
#     #print(session_memory)
#     return f'response to {query}'

    # return f'response to {query}'

def llm_response(query: str) -> str:
    # Placeholder logic for generating a response
    return f"Response to '{query}'"


from huggingface_hub import login
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq


HUGGINGFACE_TOKEN = "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"
GROQ_API_KEY = "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"

MAX_CONTENT_TOKENS = 4000
TOKENIZER_MODEL_NAME = "meta-llama/Llama-3.1-8B"
GROQ_MODEL_NAME = "llama3-8b-8192"

SYSTEM = "You are a helpful AI Assistant. Your name is {bot_name}. Respond to the query politely"

HUMAN = "{text}"

# async def llm_response(query: str):
#     login(HUGGINGFACE_TOKEN)

#     chat = ChatGroq(temperature=0, groq_api_key=GROQ_API_KEY, model_name=GROQ_MODEL_NAME, max_tokens=MAX_CONTENT_TOKENS, max_retries=2)
#     prompt = ChatPromptTemplate.from_messages([("system", SYSTEM), ("human", HUMAN)])


#     chain = prompt | chat
#     response = chain.invoke({"bot_name": "Emma", "text": query})

#     return response.content


#create_chunk_headers('explain lol')
