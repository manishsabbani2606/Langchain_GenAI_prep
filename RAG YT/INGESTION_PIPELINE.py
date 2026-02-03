import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
load_dotenv()




def load_documents(docs_path="docs"):
    """Load documents from the specified directory."""
    print(f"Loading documents from {docs_path}...")
    if not os.path.exists(docs_path):
        raise FileNotFoundError(f"The specified path {docs_path} does not exist.")
    
    loader = DirectoryLoader(docs_path, glob="**/*.txt", loader_cls=TextLoader)
    documents = loader.load()
    print(f"Loaded {len(documents)} documents.")
    
    if len(documents) == 0:
        raise ValueError("No documents found in the specified directory.")
    
    for i,doc in enumerate(documents[:2]):
        print(f"Document {i+1} content preview: {doc.page_content[:100]}...")
        
    return documents

def split_documents(documents, chunk_size=1000, chunk_overlap=200):
    "Splitting the documents into smaller chunks."
    print("Splitting documents into chunks...")
    
    text_splitter = CharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")
    
    for i, chunk in enumerate(chunks[:2]):
        print(f"\n ==== Chunk {i+1} content preview: {chunk.page_content[:100]}...")
    
    return chunks

def create_vector_store(chunks, persist_directory="db/chroma_dbvector_store"):
    "Creating the persistent vector store."
    print("Creating vector store...")
    embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
    
    print("Initializing Chroma vector store...")
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=persist_directory,
        collection_metadata={"hnsw:space":"cosine"}
    )
    
    print("Persisting vector store to disk...")
    return vector_store


def main():
    print("Starting ingestion pipeline...")
    
    # Load documents from the specified directory
    documents = load_documents(docs_path="docs")
    
    #Splitting the documents into chunks
    chunks = split_documents(documents)
    
    # Create and persist the vector store
    vector_store = create_vector_store(chunks)
    
    
    
    
    
    




if __name__ == "__main__":
    main()

