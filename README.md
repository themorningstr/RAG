# Retrieval-Augmented Generation (RAG) System

A complete end-to-end RAG system that reads documents from multiple formats (PDF, DOCX, XLSX, CSV), stores them in a vector database, and generates answers using a Large Language Model.

## Features

✅ **Multi-format Document Support**

- PDF files
- Microsoft Word documents (DOCX)
- Excel spreadsheets (XLSX, XLS)
- CSV files
- Plain text files (TXT)

✅ **Vector Database Integration**

- Open-source Chroma vector database
- Persistent storage
- Efficient similarity search

✅ **Advanced NLP Pipeline**

- Automatic text chunking with overlap
- Sentence transformer embeddings (sentence-transformers/all-MiniLM-L6-v2)
- Support for multiple LLM backends

✅ **Multiple LLM Backends**

- Ollama (mistral, llama2, and other models)
- HuggingFace transformers

✅ **REST API**

- FastAPI with interactive documentation
- CORS enabled for web integration
- Health checks and statistics endpoints

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd RAG
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Ollama (Optional, for Ollama LLM)

Download and install from: [https://ollama.ai](https://ollama.ai)

Then pull a model:

```bash
ollama pull mistral
```

Or other models:

```bash
ollama pull llama2
ollama pull neural-chat
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings (optional, defaults are provided)
```

## Quick Start

### 1. Add Documents

Place your documents in the `./data/source/` folder:

```
data/
├── source/
│   ├── document1.pdf
│   ├── document2.docx
│   ├── spreadsheet.xlsx
│   └── data.csv
```

### 2. Run Simple RAG CLI

```bash
python scripts/simple_rag.py
```

This will:

- Load all documents from `./data/source/`
- Generate embeddings and store in vector database
- Ask sample questions and display answers

### 3. Start API Server

```bash
python src/main.py
```

The API will start on `http://localhost:8000`

## API Usage

### Interactive Documentation

Once the API is running, visit:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Example API Calls

#### Ingest Documents

```bash
curl -X POST "http://localhost:8000/api/ingest"
  -H "Content-Type: application/json"
  -d '{"source_path": "./data/source"}'
```

#### Query the System

```bash
curl -X POST "http://localhost:8000/api/query"
  -H "Content-Type: application/json"
  -d '{"query": "What is the main topic?", "top_k": 3}'
```

#### Get Statistics

```bash
curl -X GET "http://localhost:8000/api/stats"
```

#### Clear Vector Store

```bash
curl -X POST "http://localhost:8000/api/clear"
```

## Python API Usage

### Basic Example

```python
from rag_app.pipeline import RAGPipeline

# Initialize pipeline
pipeline = RAGPipeline()

# Ingest documents
pipeline.ingest("./data/source")

# Query
answer, retrieved_docs, metadatas = pipeline.query("What is the main topic?")
print(answer)
```

### Advanced Example

```python
from rag_app.embeddings import EmbeddingModel
from rag_app.generation import OllamaLLM
from rag_app.pipeline import RAGPipeline
from rag_app.vectorstore import VectorStore

# Custom components
embeddings = EmbeddingModel()
llm = OllamaLLM(model_name="mistral")
vector_store = VectorStore()

# Create pipeline
pipeline = RAGPipeline(
    embedding_model=embeddings,
    llm=llm,
    vector_store=vector_store,
    chunk_size=1000,
    chunk_overlap=100
)

# Use pipeline
pipeline.ingest("./data/source")
answer, docs, meta = pipeline.query("Your question here")
```

## Project Structure

```
RAG/
├── data/
│   ├── source/           # Place your documents here
│   ├── vector_store/     # Chroma database (auto-created)
│   └── ...
├── src/
│   ├── rag_app/
│   │   ├── api/          # FastAPI endpoints and models
│   │   ├── config.py     # Configuration settings
│   │   ├── embeddings/   # Embedding models
│   │   ├── generation/   # LLM providers (Ollama, HuggingFace)
│   │   ├── ingestion/    # Document loading and chunking
│   │   ├── pipeline/     # Main RAG pipeline
│   │   ├── retrieval/    # Retrieval module
│   │   └── vectorstore/  # Vector store (Chroma)
│   └── main.py          # API server entry point
├── scripts/
│   ├── simple_rag.py     # Simple CLI example
│   ├── test_api.py       # API testing
│   └── advanced_example.py # Advanced features example
├── test/                 # Unit tests
├── requirements.txt      # Python dependencies
├── .env.example         # Configuration template
└── README.md            # This file
```

## Configuration

Edit `.env` file to customize:

### Embedding Model

```
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DEVICE=cpu  # or cuda for GPU
```

### LLM Configuration

```
LLM_MODEL=mistral
LLM_BASE_URL=http://localhost:11434
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=512
```

### Text Chunking

```
CHUNK_SIZE=500          # Characters per chunk
CHUNK_OVERLAP=50        # Overlap between chunks
TOP_K=3                 # Documents to retrieve
```

### Vector Store

```
CHROMA_DB_PATH=./data/vector_store
```

## Troubleshooting

### "Could not connect to Ollama"

**Solution:** Make sure Ollama is running:

```bash
ollama serve
```

### "Model not found"

**Solution:** Pull the model first:

```bash
ollama pull mistral
```

### "Out of memory"

**Solution:**

- Use a smaller embedding model
- Enable GPU if available (`EMBEDDING_DEVICE=cuda`)
- Reduce `CHUNK_SIZE`

### Import errors

**Solution:** Make sure you're in the project directory and have installed dependencies:

```bash
pip install -r requirements.txt
```

## Supported Document Formats

| Format | Loader | Notes |
|--------|--------|-------|
| PDF    | PyPDF2 | Extracts text from all pages |
| DOCX   | python-docx | Extracts text and tables |
| XLSX   | openpyxl | Extracts all sheets |
| XLS    | openpyxl | Extracts all sheets |
| CSV    | pandas | Converts to readable text format |
| TXT    | Built-in | Plain text files |

## Examples

See the `scripts/` folder for ready-to-use examples:

1. **simple_rag.py** - Basic RAG usage
2. **test_api.py** - Testing REST API
3. **advanced_example.py** - Advanced features and custom components

## Performance Tips

1. **GPU Acceleration:** Set `EMBEDDING_DEVICE=cuda` for faster embeddings
2. **Batch Processing:** Use `pipeline.batch_query()` for multiple queries
3. **Chunk Size:** Adjust `CHUNK_SIZE` based on your documents
4. **Model Selection:** Choose appropriate embedding and LLM models

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

## Support

For issues and questions:

- Check the troubleshooting section
- Review the examples in `scripts/`
- Check documentation in code docstrings