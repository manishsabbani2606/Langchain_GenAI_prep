from flask import Flask, render_template, request, jsonify
import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
import shutil

load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'docs'

# Initialize variables
vector_store = None
persist_directory = "db/chroma_dbvector_store"
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
model = ChatOpenAI(model="gpt-4o", temperature=0)

def init_vector_store():
    """Initialize the vector store from existing data."""
    global vector_store
    if os.path.exists(persist_directory):
        try:
            vector_store = Chroma(
                persist_directory=persist_directory,
                embedding_function=embedding_model,
                collection_metadata={"hnsw:space": "cosine"}
            )
            return True
        except Exception as e:
            print(f"Error initializing vector store: {e}")
            return False
    return False

def load_and_index_documents():
    """Load documents from the docs directory and create vector store."""
    global vector_store
    
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        return False
    
    try:
        # Load documents
        loader = DirectoryLoader(
            app.config['UPLOAD_FOLDER'],
            glob="**/*.txt",
            loader_cls=TextLoader
        )
        documents = loader.load()
        
        if not documents:
            return False
        
        # Split documents
        text_splitter = CharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )
        chunks = text_splitter.split_documents(documents)
        
        # Create vector store
        if os.path.exists(persist_directory):
            shutil.rmtree(persist_directory)
        
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embedding_model,
            persist_directory=persist_directory,
            collection_metadata={"hnsw:space": "cosine"}
        )
        
        return True
    except Exception as e:
        print(f"Error loading and indexing documents: {e}")
        return False

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def status():
    """Check if vector store is initialized."""
    has_docs = vector_store is not None
    doc_count = 0
    
    if has_docs:
        try:
            doc_count = vector_store._collection.count()
        except:
            pass
    
    return jsonify({
        'initialized': has_docs,
        'document_count': doc_count
    })

@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Handle file upload."""
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    
    if not files:
        return jsonify({'error': 'No files selected'}), 400
    
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        for file in files:
            if file.filename.endswith('.txt'):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)
        
        # Re-index documents
        success = load_and_index_documents()
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Successfully uploaded and indexed {len(files)} file(s)'
            })
        else:
            return jsonify({
                'error': 'Failed to index documents'
            }), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/query', methods=['POST'])
def query():
    """Handle user query against the RAG."""
    if vector_store is None:
        return jsonify({'error': 'No documents indexed. Please upload documents first.'}), 400
    
    data = request.json
    user_query = data.get('query', '').strip()
    
    if not user_query:
        return jsonify({'error': 'Query cannot be empty'}), 400
    
    try:
        # Retrieve similar documents
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )
        
        docs = retriever.invoke(user_query)
        
        # Prepare context
        doc_contents = "\n\n".join([doc.page_content for doc in docs])
        
        combined_input = f"""Based on the following documents, answer the query: {user_query}

Documents:
{doc_contents}

Please provide a concise and informative answer. If the answer cannot be found in the documents, say "The information is not available in the provided documents."""

        messages = [
            SystemMessage(content="You are a helpful assistant that provides concise and informative answers based on the provided documents."),
            HumanMessage(content=combined_input)
        ]
        
        response = model.invoke(messages)
        
        return jsonify({
            'success': True,
            'answer': response.content,
            'sources': [
                {
                    'content': doc.page_content[:200] + '...',
                    'source': doc.metadata.get('source', 'Unknown')
                }
                for doc in docs
            ]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear_index():
    """Clear the vector store and docs."""
    global vector_store
    
    try:
        vector_store = None
        
        if os.path.exists(persist_directory):
            shutil.rmtree(persist_directory)
        
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            shutil.rmtree(app.config['UPLOAD_FOLDER'])
        
        return jsonify({'success': True, 'message': 'Index cleared successfully'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Initialize vector store on startup
    init_vector_store()
    app.run(debug=True, port=5000)
