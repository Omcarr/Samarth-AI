from langchain_ollama import OllamaLLM


def setup_model():
    model =OllamaLLM(model='llama3')
    return model


def llm_response(query: str) -> str:
    # Placeholder logic for generating a response
    return f"Response to '{query}'"
