from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from langchain_pinecone import Pinecone
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings


#Extracting the data from the PDF File

def load_pdf(data):
    loader = DirectoryLoader(data,glob="*.pdf",loader_cls=PyPDFLoader)
    documents = loader.load()
    
    return documents


#Split the data into text chunks

def text_split(extracted_data):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=20)
    text_chunks=text_splitter.split_documents(extracted_data)
    return text_chunks

#Embedding the chunks 

def download_huggingface_embeddings():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return embeddings