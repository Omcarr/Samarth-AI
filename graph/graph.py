import os
from langchain_community.document_loaders import PDFPlumberLoader
import pdfplumber
from pathlib import Path
import tempfile
import subprocess
import uuid 
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

groq_api = os.getenv("GROQ_API_KEY1")

def generate_async(messages):
    client = Groq(api_key = groq_api)
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.4,
        max_tokens=1024,
        top_p=0.9,
        stream=False,
        stop=None,
    )
    return completion.choices[0].message.content

desc_prompt = """
Summarize the following response in 3 sentences, highlighting key insights from the graph data. 
Ensure there is no mention of "The graph is saved as an image file named 'output_graph.png' in the 'graph_img' directory." is excluded.
This is the input text: {pdf_text}
This is the Response: {response}
"""

system_prompt = """You are a Python data visualization expert. Your task is to create matplotlib code based on provided data and queries. 
Do not try to read any files - only use the data directly provided in the prompt."""

userprompt = """
Given the following data:
{data}
Based on the user's query: '{question}', provide executable Python code using matplotlib to generate the graph requested.
Requirements for the code:
1. Load the data provided in pandas dataframe in the format
   data = column:[rows], column2:[rows]
2. Do not attempt to read any files
3. Create the visualization with:
   - Figure size: figsize=(12, 8)
   - DPI: 150 or higher
   - Rotated labels: plt.xticks(rotation=45, ha='right')
   - Proper layout: plt.tight_layout()
4. Save the graph to: {save_path}
5. Do not include plt.show()

Return only the executable Python code without any explanations.
"""

def generate_graph(data, user_query):
    save_dir = "graph/output.png"
    prompt1 = userprompt.format(data=data, question=user_query, save_path=save_dir)
    messages=[
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": prompt1,
        }
    ]
    response = generate_async(messages)

    instructions = response.replace('```python', '').replace('```', '').strip()
    print(instructions)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
        temp_file.write(instructions.encode('utf-8'))
        temp_file_path = temp_file.name
        try:
            result = subprocess.run(['python', temp_file_path], capture_output=True, text=True)

            if result.returncode != 0:
                print(f"Error executing the code:\n{result.stderr}")
        except Exception as e:
            print(f"Error generating the graph: {e}")
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                

    prompt = desc_prompt.format(pdf_text=prompt1, response=instructions)
    message=[
        {
            "role": "system",
            "content": "You are a Data Analyst. With the provided contexts give conclusions"
        },
        {
            "role": "user",
            "content": prompt,
        }
    ]
    return generate_async(message)