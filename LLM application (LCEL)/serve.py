from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
load_dotenv()
from langserve import add_routes

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")


model=ChatGroq(model="openai/gpt-oss-120b",groq_api_key=groq_api_key)

#1. Create a prompt Template


generictemplate = "Transalate the following from {source_language} to {target_language}: {text}"
prompt = ChatPromptTemplate.from_messages([
    ("system",generictemplate),
    ("user","{text}")
])


parser = StrOutputParser()

# Create the chain
chain=prompt|model|parser


#App Definition

app=FastAPI(
    title="This is my Langchain Server for language transalation",
    version="1.0",
    description="A simple API server using Langchain and Langserve"
)

#adding the chain routes
add_routes(
    app,
    chain,
    path="/chain"
)


if __name__=="__main__":
    import uvicorn
    uvicorn.run(app,host="localhost",port=8000)