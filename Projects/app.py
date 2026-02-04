import streamlit as st
import openai
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate

import os
from dotenv import load_dotenv
load_dotenv()

#IMPLEMENT LANGSMITH TRACKING

os.environ["LangChain_API_KEY"]= os.getenv("LangChain_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] ="Q&A Chatbot with openAI and Streamlit"

#Define the Prompt Template

prompt = ChatPromptTemplate.from_messages([
    ("system","You are a helpful AI assistant answering questions about the user's project. Please respond to the user's questions in a concise manner."),
    ("user","Question: {question}")
])


def generate_response(question,api_key,llm,temperature,max_tokens):    
    openai.api_key = api_key
    llm=ChatOpenAI(model=llm,temperature=temperature,max_tokens=max_tokens)
    output = StrOutputParser()
    chain = prompt|llm|output
    
    answer = chain.invoke({"question": question}) #keypair should same as in the prompt template
    return answer

### Streamlit code


# --------------------------------------------------
# Streamlit UI
# --------------------------------------------------
st.set_page_config(page_title="Q&A Chatbot", page_icon="🤖", layout="centered")

st.title("🤖 Q&A Chatbot with OpenAI + LangChain")
st.markdown("Ask questions about your project and get concise AI-powered answers.")

# Sidebar configuration
st.sidebar.header("⚙️ Model Configuration")

llm_model = st.sidebar.selectbox(
    "Choose OpenAI Model",
    ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
)

temperature = st.sidebar.slider(
    "Temperature",
    min_value=0.0,
    max_value=1.0,
    value=0.2,
    step=0.1
)

max_tokens = st.sidebar.slider(
    "Max Tokens",
    min_value=50,
    max_value=1000,
    value=300,
    step=50
)

# User input

question = st.text_area(
    "💬 Enter your question:",
    placeholder="e.g., Explain my LangChain ingestion pipeline..."
)

# Submit button
if st.button("🚀 Get Answer"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            try:
                response = generate_response(
                    question=question,
                    api_key=os.getenv("OPENAI_API_KEY"),
                    llm=llm_model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                st.success("Answer:")
                st.write(response)
            except Exception as e:
                st.error(f"Error: {e}")

# Footer
st.markdown("---")
st.caption("Built with ❤️ using Streamlit, LangChain, and OpenAI")