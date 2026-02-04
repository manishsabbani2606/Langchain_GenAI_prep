from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

persist_directory = "db/chroma_dbvector_store"

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

db = Chroma(
    persist_directory=persist_directory,
    embedding_function=embedding_model,
    collection_metadata={"hnsw:space": "cosine"}
)

query = "How much did Microsoft pay to acquire GitHub?"

retriever = db.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)

docs = retriever.invoke(query)

print(f"\nTop {len(docs)} most similar documents to the query:\n")

for i, doc in enumerate(docs, 1):
    print(f"--- Document {i} ---")
    print(doc.page_content)
    print("Metadata:", doc.metadata)
    print()
    
    
combined_input = f""" Based on the following documents, answer the query: {query}\n\n

Documents:
{chr(10).join([doc.page_content for doc in docs])}

Please provide a concise and informative answer.
"""

#creating the model

model = ChatOpenAI(model="gpt-4o", temperature=0)

messages = [
    SystemMessage(content="You are a helpful assistant that provides concise and informative answers based on the provided documents."),
    HumanMessage(content=combined_input)
]

final_response = model.invoke(messages)

print("Final Response:\n")
print(final_response.content)



