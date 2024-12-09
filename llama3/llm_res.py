from langchain_ollama import OllamaLLM


def setup_model():
    model =OllamaLLM(model='llama3')
    return model

async def llm_response(query, model):
    # try:
    #     print(query)
    #     model_response = model.invoke(query)

    #     return model_response
    # except Exception as e:
    #     return f"Error: {str(e)}"

    return f'response to {query}'

# def llm_response(query: str) -> str:
#     # Placeholder logic for generating a response
#     return f"Response to '{query}'"


