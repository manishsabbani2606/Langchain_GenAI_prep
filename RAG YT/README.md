# RAG Pipeline UI

A modern, user-friendly web interface for your Retrieval-Augmented Generation (RAG) pipeline built with Flask, LangChain, and OpenAI.

## Features

✨ **Document Management**
- Upload multiple `.txt` files via drag-and-drop or file browser
- Automatic document indexing with Chroma vector store
- Real-time status indicator

💬 **Interactive Q&A**
- Ask questions about your documents
- Get accurate answers with source citations
- View retrieved documents for transparency
- Clean, modern chat interface

🎨 **User-Friendly Interface**
- Responsive design (works on desktop, tablet, mobile)
- Real-time status updates
- Loading indicators and notifications
- Beautiful gradient header and intuitive layout

## Prerequisites

- Python 3.8+
- OpenAI API key (set in `.env` file)

## Installation

1. **Clone or navigate to the project directory:**
```bash
cd RAG\ YT
```

2. **Create a virtual environment (optional but recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
Create a `.env` file in the RAG YT directory:
```
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

1. **Start the application:**
```bash
python app.py
```

2. **Open your browser and navigate to:**
```
http://localhost:5000
```

3. **Upload Documents:**
   - Click the upload area or drag & drop `.txt` files
   - The system will automatically process and index your documents
   - Status will show "Ready" when documents are indexed

4. **Ask Questions:**
   - Type your question in the input field
   - Click "Send" or press Enter
   - The system will retrieve relevant documents and generate an answer
   - View source documents for verification

5. **Clear Data:**
   - Click "Clear All" to remove all documents and start fresh

## File Structure

```
RAG YT/
├── app.py                 # Flask application and RAG logic
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── docs/                 # Document storage (created on upload)
├── db/                   # Vector store storage
├── templates/
│   └── index.html        # Web interface
└── static/
    ├── style.css         # Styling
    └── script.js         # Frontend logic
```

## API Endpoints

### `GET /`
Returns the main web interface

### `GET /api/status`
Returns the current status of the RAG system
```json
{
  "initialized": true,
  "document_count": 5
}
```

### `POST /api/upload`
Upload and index documents
- **Form Data:** files (multipart/form-data)
- **Response:** Success message or error

### `POST /api/query`
Ask a question about the documents
- **Body:** `{ "query": "your question here" }`
- **Response:**
```json
{
  "success": true,
  "answer": "The answer to your question...",
  "sources": [
    {
      "content": "Relevant excerpt...",
      "source": "Document name"
    }
  ]
}
```

### `POST /api/clear`
Clear all indexed documents and start fresh
- **Response:** Success message or error

## Configuration

**Vector Store Settings:**
- Embedding Model: `text-embedding-3-small` (OpenAI)
- Chunk Size: 1000 tokens
- Chunk Overlap: 200 tokens
- Similarity Search: Top 3 results
- LLM Model: `gpt-4o`

You can modify these in `app.py`:

```python
# Line 29: Embedding model
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

# Line 31: Vector store settings
vector_store = Chroma(
    ...
    collection_metadata={"hnsw:space":"cosine"}
)

# Line 76: LLM model
model = ChatOpenAI(model="gpt-4o", temperature=0)
```

## Troubleshooting

**No documents appear after upload:**
- Ensure you're uploading `.txt` files
- Check that the `docs/` directory is created
- Check Flask console for error messages

**OPENAI_API_KEY error:**
- Make sure `.env` file exists in the RAG YT directory
- Verify your API key is correct
- Ensure `python-dotenv` is installed

**Port 5000 already in use:**
```bash
python app.py
# Or change port in app.py, line 170
```

**Memory issues with large documents:**
- Reduce `chunk_size` parameter in `app.py`
- Split very large files into smaller chunks

## Performance Tips

- For faster responses, upload smaller, focused documents
- Use specific, detailed questions for better results
- The first query after startup may take longer (model loading)

## License

MIT License - Feel free to modify and use as needed.

## Support

For issues or questions about the RAG pipeline, refer to:
- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Chroma Documentation](https://docs.trychroma.com/)
