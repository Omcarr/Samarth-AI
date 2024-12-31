# from huggingface_hub import login
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import os


HUGGINGFACE_TOKEN = os.environ["HUGGINGFACE_TOKEN"]

MAX_CONTENT_TOKENS = 4000
TOKENIZER_MODEL_NAME =  os.environ["TOKENIZER_MODEL_NAME"]

GROQ_MODEL_NAME = os.environ["GROQ_MODEL_NAME"]

SYSTEM = '''
You are given a chunk of text from a document named {doc_title}.
Give an appropriate title to the chunk and a brief summary of it under 10 words to enhance vector embeddings.
Your response MUST be the title and summary and nothing else. DO NOT respond with anything else.
'''.strip()

TRUNCATION_MESSAGE = "Also note that the document text provided below is just the first ~{num_words} words of the document. That should be plenty for this task. Your response should still pertain to the entire document, not just the text provided below."

HUMAN = "{text}"

def add_chunk_header(doc_title: str, content: str, GROQ_API_KEY: str):
    # login(HUGGINGFACE_TOKEN)

    # tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_MODEL_NAME)
    # tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B")

    chat = ChatGroq(temperature=0, groq_api_key=GROQ_API_KEY, model_name=GROQ_MODEL_NAME, max_tokens=MAX_CONTENT_TOKENS, max_retries=2)

    # system_message = truncate_content(content=content, max_tokens=MAX_CONTENT_TOKENS)

    prompt = ChatPromptTemplate.from_messages([("system", SYSTEM), ("human", HUMAN)])


    chain = prompt | chat
    response = chain.invoke({"doc_title": doc_title, "text": content})
    return response.content + content
    
# content = '''
# SECURITIES REGISTERED PURSUANT TO SECTION 12(B) OF THE ACT:\nClass B Common Stock NKE New York Stock Exchange\n(Title of each class) (Trading symbol) (Name of each exchange on which registered)\nSECURITIES REGISTERED PURSUANT TO SECTION 12(G) OF THE ACT:\nNONE\nIndicate by check mark: Yes No\n•if the registrant is a well-known seasoned issuer, as defined in Rule 405 of the Securities Act. þ ¨\n•if the registrant is not required to file reports pursuant to Section 13 or Section 15(d) of the Act. ¨ þ\n•whether the registrant (1) has filed all reports required to be filed by Section 13 or 15(d) of the Securities \nExchange Act of 1934 during the preceding 12 months (or for such shorter period that the registrant was required \nto file such reports), and (2) has been subject to such filing requirements for the past 90 days.þ ¨\n•whether the registrant has submitted electronically every Interactive Data File required to be submitted pursuant to', '•whether the registrant has submitted electronically every Interactive Data File required to be submitted pursuant to \nRule 405 of Regulation S-T (§232.405 of this chapter) during the preceding 12 months (or for such shorter period \nthat the registrant was required to submit such files).þ ¨\n•whether the registrant is a large accelerated filer, an accelerated filer, a non-accelerated filer, a smaller reporting company or an emerging growth \ncompany. See the definitions of “large accelerated filer,” “accelerated filer,” “smaller reporting company,” and “emerging growth company” in Rule 12b-2 of \nthe Exchange Act.\nLarge accelerated filer þ Accelerated filer ☐ Non-accelerated filer ☐ Smaller reporting company ☐ Emerging growth company ☐\n•if an emerging growth company, if the registrant has elected not to use the extended transition period for \ncomplying with any new or revised financial accounting standards provided pursuant to Section 13(a) of the \nExchange Act.¨
# '''
# print(add_chunk_header(doc_title="nike financial statementf", content=content, GROQ_API_KEY="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"))

# def truncate_content(content: str, max_tokens: int) -> tuple[str, int]:
#     """
#     Truncate the content to a specified maximum number of tokens.

#     Args:
#         content (str): The input text to be truncated.
#         max_tokens (int): The maximum number of tokens to keep.

#     Returns:
#         tuple[str, int]: A tuple containing the truncated content and the number of tokens.
#     """

#     tokens = tokenizer.encode(content)
#     truncated_tokens = tokens[:max_tokens]
#     num_tokens = tokenizer.decode(truncated_tokens)

    
#     truncation_message = TRUNCATION_MESSAGE.format(num_words=1500) if num_tokens >= MAX_CONTENT_TOKENS else ""


#     # Prepare the prompt for title extraction
#     if truncation_message:
#         system_message = SYSTEM + "\n" + truncation_message

#     else:
#         system_message = SYSTEM

#     return system_message

#     # return tokenizer.decode(truncated_tokens), min(len(tokens), max_tokens)




# def get_document_title(document_text: str) -> str:
#     """
#     Extract the title of a document using a language model.

#     Args:
#         document_text (str): The text of the document.

#     Returns:
#         str: The extracted document title.
#     """
#     # Truncate the content if it's too long
#     document_text, num_tokens = truncate_content(document_text, MAX_CONTENT_TOKENS)
#     truncation_message = TRUNCATION_MESSAGE.format(num_words=4000) if num_tokens >= MAX_CONTENT_TOKENS else ""


#     # Prepare the prompt for title extraction
#     if truncation_message:
#         system_message = system + "\n" + truncation_message

#     else:
#         system_message = system

#     return system_message