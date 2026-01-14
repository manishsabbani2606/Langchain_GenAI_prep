import os
from dotenv import load_dotenv
load_dotenv()

#Langsmith traching
os.environ["LangChain_API_KEY"] = os.getenv("LangChain_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"]=os.getenv("LANGCHAIN_PROJECT")



from langchain_community.llms import Ollama
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
st.set_page_config(page_title="LangChain + Ollama Demo", layout="centered")

st.title("LangChain Demo with Ollama")
st.write("Ask any question and get answers from a local Ollama model.")

input_text = st.text_input("Enter the question you have in your mind:")

# --------------------------------------------------
# Initialize Ollama LLM
# --------------------------------------------------
llm = Ollama(model="gemma:2b")  # make sure ollama serve is running

# --------------------------------------------------
# Prompt Template
# --------------------------------------------------
prompt = ChatPromptTemplate.from_messages(
 [
    ("system","You are an AI assistant that helps people find information."),
    ("human","Enter the question you have in your mind:{question}")
 
    
 ])

# --------------------------------------------------
# Run LLM on button click
# --------------------------------------------------
if st.button("Get Answer"):
    if input_text.strip() == "":
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            chain = prompt | llm
            response = chain.invoke({"question": input_text})

        st.subheader("Answer")
        st.write(response)

