import asyncio
import chromadb
from chromadb.utils import embedding_functions
from chromadb.config import Settings


PERSIST_DIRECTORY = "test_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class VectorDatabase:
    def __init__(self) -> None:
        self.chroma_client = None
        self.collection = None
    

    async def connect(self) -> None:
        self.chroma_client = await chromadb.AsyncHttpClient(
                    settings=Settings(chroma_api_impl="rest",
                            chroma_server_host="localhost",
                            chroma_server_http_port=8000)
                    )
        
        self.collection = await self.chroma_client.get_or_create_collection(name="prod")
        

    

    async def add_to_vector_store(self, chunks: list, metadatas: list=[]) -> None:
        if not self.chroma_client:
            await self.connect()
        
        with open("embedding_id.txt", "r") as f:
            last_used_id = int(f.readline())
        
        with open("embedding_id.txt", "w") as f:
            f.write(str(last_used_id+len(chunks)))


        ids = list(range(last_used_id, last_used_id+len(chunks)))
        ids = list(map(str, ids))

        if not metadatas:
            metadatas = [{"test":True}]*len(chunks)

        
        await self.collection.add(documents=chunks, metadatas=metadatas, ids=ids)



    async def query_vector_store(self, query: str, metadata=None, n_results=3) -> list:
        if not self.chroma_client:
            await self.connect()

        result = await self.collection.query(query_texts=[query], where=metadata, n_results=n_results)
        
        return result
    



    async def delete_from_vector_store(self, doc_name: str, ids: list) -> None:
        if not self.chroma_client:
            await self.connect()


        if doc_name:
            await self.collection.delete(where={"doc_name": doc_name})
        
        elif ids:
            await self.collection.delete(ids=ids)
        
    


# Example Usage
async def main():
    DB = VectorDatabase()
    await DB.connect()

    print("connected to database...")
    chunks = ["A journey of a thousand miles begins with a single step.",
"Actions speak louder than words.",
"The pen is mightier than the sword.",
"Rome wasn’t built in a day.",
"When in Rome, do as the Romans do.",
"The only limit to our realization of tomorrow is our doubts of today.",
"In the middle of every difficulty lies opportunity.",
"Success is not final, failure is not fatal: It is the courage to continue that counts.",
"Do what you can, with what you have, where you are.",
"Happiness is not something ready made. It comes from your own actions.",
]
    
    # await DB.add_to_vector_store(chunks=chunks)
    # print("added docs to vector store")
    
    # Query the vector store
    query_text = input("enter query: ")
    results = await DB.query_vector_store(query=query_text)
    
    print("Query Results:")
    for result in results:
        print(result)


if __name__ == "__main__":
    asyncio.run(main())