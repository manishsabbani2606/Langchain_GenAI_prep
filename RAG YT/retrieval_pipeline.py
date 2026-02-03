from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
load_dotenv()


persist_directory="db/chroma_dbvector_store"

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

db = Chroma(persist_directory=persist_directory,
            embedding_function=embedding_model,collection_metadata={"hnsw:space":"cosine"})


query = "How much did Microsoft pay to acquire GitHub?"

retriever = db.as_retriever(search_type="similarity", search_kwargs={"k":3})

docs = retriever.invoke(query)

print(f"Top 3 most similar documents to the query '{query}':\n")

for i, doc in enumerate(docs,1):
    print(f"Document {i+1} content preview: {doc.page_content}...\n")
    