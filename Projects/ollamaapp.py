import os
import streamlit as st
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------
load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Q&A Chatbot with Ollama and Streamlit"

# --------------------------------------------------
# Prompt Template
# --------------------------------------------------
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant answering questions about the user's project. "
               "Please respond in a concise manner."),
    ("user", "Question: {question}")
])

# --------------------------------------------------
# LLM Response Function (Ollama)
# --------------------------------------------------
def generate_response(question, model, temperature, max_tokens):
    llm = Ollama(
        model=model,
        temperature=temperature,
        num_predict=max_tokens
    )

    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser

    return chain.invoke({"question": question})

# --------------------------------------------------
# Streamlit UI
# --------------------------------------------------
st.set_page_config(page_title="Q&A Chatbot (Ollama)", page_icon="🦙", layout="centered")

st.title("🦙 Q&A Chatbot with Ollama + LangChain")
st.markdown("Ask questions about your project using **local LLMs powered by Ollama**.")

# Sidebar configuration
st.sidebar.header("⚙️ Ollama Model Configuration")

ollama_model = st.sidebar.selectbox(
    "Choose Ollama Model",
    [
        
        "gemma:2b",
        "llama3:8b",
        "mistral",
        "mixtral",
        "phi3"
    ]
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
    max_value=2000,
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
                    model=ollama_model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                st.success("Answer:")
                st.write(response)
            except Exception as e:
                st.error(f"Error: {e}")

# Footer
st.markdown("---")
st.caption("Built with ❤️ using Streamlit, LangChain, and Ollama")