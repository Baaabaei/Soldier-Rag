# Soldier RAG - Military Document Retrieval System

A Retrieval-Augmented Generation (RAG) system designed for military and defense document processing, providing intelligent question-answering capabilities for classified and sensitive military documentation.

## 🎯 Overview

Soldier RAG is a specialized RAG pipeline built for military environments, enabling secure and efficient retrieval of information from military documents, field reports, and technical manuals. The system combines state-of-the-art embedding models with a robust retrieval architecture to deliver accurate, context-aware responses.

## 🚀 Features

- **Military-Grade Document Processing**: Handles PDFs, Word documents, and text files with military-specific formatting
- **Multi-Stage Retrieval**: Combines dense retrieval with re-ranking for superior accuracy
- **Memory Management**: Maintains conversation context and document relevance
- **Vector Search**: Uses FAISS for efficient similarity search at scale
- **REST API**: Full-featured FastAPI backend for integration
- **Streamlit Interface**: User-friendly web interface for interactive queries
- **Security Features**: Environment-based configuration for secure deployment
- **Optimized Reranking**: Cross-encoder models for precision retrieval

## 📁 Project Structure

```
dadrah_rag/
├── api.py                 # FastAPI REST endpoints
├── chat.py               # Chat interaction module
├── config.py             # Configuration management
├── embeddings.py         # Embedding generation
├── ingest.py            # Document ingestion pipeline
├── memory.py            # Conversation memory management
├── rag_pipeline.py      # Core RAG pipeline implementation
├── reranker.py          # Cross-encoder reranking
├── vector_store.py      # FAISS vector store operations
├── streamlit_app.py     # Streamlit web interface
├── static/              # Static assets for web interface
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── README.md           # This file
```

## 🛠️ Technology Stack

- **Python 3.9+**
- **LangChain**: Framework for LLM application development
- **FAISS**: Facebook AI Similarity Search
- **Sentence Transformers**: Embedding models
- **HuggingFace Transformers**: Cross-encoder rerankers
- **FastAPI**: REST API framework
- **Streamlit**: Web interface
- **Qdrant/Chroma**: Vector database options
- **PyPDF2 & pdfplumber**: PDF processing
- **python-docx**: Word document processing

## 📋 Prerequisites

- Python 3.9 or higher
- 8GB+ RAM (16GB recommended for military document processing)
- CUDA-capable GPU (optional but recommended)
- 10GB+ storage space for document indexing

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Baaabaei/Soldier-Rag.git
cd Soldier-Rag
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configurations
```

## ⚙️ Configuration

Edit the `.env` file with your settings:

```env
# Model Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2
LLM_MODEL=mistralai/Mistral-7B-Instruct-v0.1

# Vector Store
VECTOR_STORE_PATH=./vector_store
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Security
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=.pdf,.docx,.txt,.md
```

## 🚀 Usage

### Starting the API Server

```bash
python api.py
```

The API will be available at `http://localhost:8000`

### Running the Streamlit Interface

```bash
streamlit run streamlit_app.py
```

Access the web interface at `http://localhost:8501`

### Document Ingestion

```bash
python ingest.py --directory ./documents
```

### Interactive Chat

```bash
python chat.py
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/query` | POST | Submit a query to the RAG system |
| `/ingest` | POST | Ingest new documents |
| `/search` | POST | Direct document search |
| `/history` | GET | Retrieve chat history |
| `/clear` | DELETE | Clear conversation memory |

### Example API Usage

```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={
        "query": "What are the standard operating procedures for field communications?",
        "top_k": 5,
        "use_reranker": True
    }
)
print(response.json())
```

## 🏗️ Architecture

1. **Document Ingestion Pipeline**
   - Document parsing and text extraction
   - Text chunking with overlap
   - Embedding generation
   - Vector store indexing

2. **Retrieval Pipeline**
   - Query embedding generation
   - Similarity search in vector store
   - Cross-encoder reranking
   - Context preparation for LLM

3. **Generation Pipeline**
   - Context + query formatting
   - LLM inference
   - Response validation and formatting

4. **Memory Management**
   - Conversation history tracking
   - Context window management
   - Relevance scoring for memory

## 🔒 Security Considerations

- All environment variables are stored in `.env` (not in version control)
- File upload validation and sanitization
- Rate limiting for API endpoints
- Input validation and injection prevention
- Secure token handling for API authentication

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```

## 📈 Performance Optimization

- **Batch Processing**: Process documents in batches for efficiency
- **Caching**: Frequently accessed embeddings are cached
- **GPU Acceleration**: CUDA support for faster inference
- **Asynchronous Processing**: Non-blocking API operations

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- HuggingFace for transformer models
- LangChain team for the RAG framework
- Military document processing guidelines and best practices

## 📞 Support

For support, please open an issue in the GitHub repository or contact the development team.

## 🔮 Future Enhancements

- Multi-modal document processing (images, diagrams)
- Real-time document update streaming
- Advanced security features (encryption, access control)
- Support for additional document formats
- Automated document classification
- Multi-language support
- Custom model fine-tuning for military terminology

---

**Disclaimer**: This system is designed for demonstration and educational purposes. Deployment in production military environments requires additional security assessments and compliance with applicable regulations.
