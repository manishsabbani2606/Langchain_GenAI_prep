#Creating the EndPoint

from flask import Flask, render_template, jsonify, request
from src.helper import download_huggingface_embeddings
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
load_dotenv()
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.prompt import *
from langchain_pinecone import PineconeVectorStore



#intialize the flask

app = Flask(__name__)

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

embeddings = download_huggingface_embeddings()

index_name = "medicalchatbot"

#we can also load the existing index as well
existing_index = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)

retriver = existing_index.as_retriever(search_type="similarity",search_kwargs={"k":3})

#define the model

model_llm=OpenAI(temperature=0.4,max_tokens=500)

#define the prompt

prompt = ChatPromptTemplate.from_messages(
    [
        ("system",system_prompt),
        ("human","{input}"),
    ]
)

#creating the LCEL Chain
rag_chain = (
    {
        "context": retriver,
        "input": RunnablePassthrough()
    }
    | prompt
    | model_llm
    | StrOutputParser() )

@app.route("/")
def index():
    return render_template('index.html')


@app.route("/get", methods=["GET","POST"])
def chat():
    msg = request.form["msg"]

    response = rag_chain.invoke(msg)

    # Print safely
    try:
        print("Response:", response.content)
        return response.content
    except AttributeError:
        print("Response:", response)
        return str(response)


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8080, debug=True)
    