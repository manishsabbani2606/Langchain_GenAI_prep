from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_chroma import Chroma

# --------------------------------------------------
# Vector DB setup
# --------------------------------------------------
persist_directory = "db/chroma_dbvector_store"

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

db = Chroma(
    persist_directory=persist_directory,
    embedding_function=embedding_model
)

# --------------------------------------------------
# LLM setup
# --------------------------------------------------
model = ChatOpenAI(model="gpt-4o", temperature=0)

# --------------------------------------------------
# Chat history
# --------------------------------------------------
chat_history = []

# --------------------------------------------------
# Main QA function
# --------------------------------------------------
def ask_question(user_question):
    global chat_history

    print(f"\nUser Question: {user_question}\n")

    # ---------- Step 1: Generate search question ----------
    if chat_history:
        messages = (
            [SystemMessage(
                content="You are a helpful assistant that reformulates a search query based on chat history."
            )]
            + chat_history
            + [HumanMessage(content=f"User question: {user_question}")]
        )

        result = model.invoke(messages)
        search_question = result.content.strip()
        print(f"Search Question from chat history: {search_question}\n")
    else:
        search_question = user_question

    # ---------- Step 2: Retrieve documents ----------
    retriever = db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )

    docs = retriever.invoke(search_question)

    print(f"Top {len(docs)} most similar documents:\n")

    for i, doc in enumerate(docs, 1):
        print(f"--- Document {i} ---")
        print(doc.page_content)
        print("Metadata:", doc.metadata)
        print()

    # ---------- Step 3: Create final prompt ----------
    combined_input = f"""
Based on the following documents, answer the query:

User Question:
{user_question}

Documents:
{chr(10).join([doc.page_content for doc in docs])}

Please provide a concise and informative answer.
"""

    messages = (
        [SystemMessage(
            content="You are a helpful assistant that provides concise and informative answers based on the provided documents."
        )]
        + chat_history
        + [HumanMessage(content=combined_input)]
    )

    # ---------- Step 4: Generate final answer ----------
    result = model.invoke(messages)
    answer = result.content

    print("Final Response:\n")
    print(answer)

    # ---------- Step 5: Update chat history ----------
    chat_history.append(HumanMessage(content=user_question))
    chat_history.append(AIMessage(content=answer))

    print("\nUpdated Chat History:\n")
    print(answer)

    return answer

# --------------------------------------------------
def start_chat():
    print("Welcome to the History-Aware QA System! Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Exiting the chat. Goodbye!")
            break
        ask_question(user_input)
        
        
        
# --------------------------------------------------
if __name__ == "__main__":
    start_chat()