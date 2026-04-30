"""README: Vector Store Backends

Quick Guide to Using Different Vector Database Backends
"""

# Vector Store Backends - Quick Setup Guide

## 🎯 What You Need to Know

The RAG system supports **6 vector database backends**, allowing you to switch with just one configuration change:

```ini
# In .env file
VECTOR_STORE_TYPE=chroma     # Switch to: faiss, weaviate, qdrant, pinecone, astradb
```

## ⚡ Quick Start (5 Minutes)

### Default Setup (Chroma)
```bash
# Already included! Just run:
python run.py api

# Check logs:
tail -f logs/vectorstore/chroma_store.log
```

### Switch to FAISS (Fast Local)
```ini
# Edit .env
VECTOR_STORE_TYPE=faiss
```

```bash
# Install
pip install faiss-cpu

# Run (same command, different backend)
python run.py api
```

## 📦 Installation by Backend

### Option 1: Install Specific Backend
```bash
python scripts/install_vectorstore_deps.py faiss
# or: chroma, weaviate, qdrant, pinecone, astradb
```

### Option 2: Install All Backends
```bash
python scripts/install_vectorstore_deps.py all
```

### Option 3: Manual Installation
```bash
pip install -r requirements-vectorstore.txt
```

## 🗺️ Backend Comparison

| Feature | Chroma | FAISS | Weaviate | Qdrant | Pinecone | Astra |
|---------|--------|-------|----------|--------|----------|-------|
| **Setup** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Speed** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Cost** | Free | Free | Free | Free | Paid | Paid |
| **Scalability** | Small | Small | Large | Large | Large | Large |
| **Best For** | Dev | Research | Prod | Prod | Enterprise | Enterprise |

## 📚 Detailed Setup

### 1️⃣ Chroma (Default ✅)

Already configured! No setup needed.

```python
# Use it
from rag_app.pipeline import RAGPipeline

pipeline = RAGPipeline()  # Uses Chroma by default
pipeline.ingest("./data/source")
answer, docs, _ = pipeline.query("What is RAG?")
```

---

### 2️⃣ FAISS (Fast Local Search)

**Install:**
```bash
pip install faiss-cpu
```

**Configure:**
```ini
# .env
VECTOR_STORE_TYPE=faiss
VECTOR_STORE_PATH=./data/vector_store
```

**Use:**
```python
pipeline = RAGPipeline(vector_store_backend="faiss")
```

**Best for:** Speed-critical applications, offline deployments

---

### 3️⃣ Weaviate (Flexible Cloud)

**Install:**
```bash
pip install weaviate-client
```

**Option A: Self-Hosted (Docker)**
```bash
docker run -d -p 8080:8080 semitechnologies/weaviate:latest
```

**Option B: Cloud Service**
- Sign up at https://console.weaviate.cloud
- Create cluster
- Get API key

**Configure:**
```ini
# .env - For local Docker
VECTOR_STORE_TYPE=weaviate
WEAVIATE_URL=http://localhost:8080

# Or for cloud
WEAVIATE_URL=https://your-cluster.weaviate.network
WEAVIATE_API_KEY=your-api-key
```

**Use:**
```python
pipeline = RAGPipeline(vector_store_backend="weaviate")
```

---

### 4️⃣ Qdrant (High Performance)

**Install:**
```bash
pip install qdrant-client
```

**Option A: Local Mode (Files)**
```ini
# .env
VECTOR_STORE_TYPE=qdrant
VECTOR_STORE_PATH=./data/vector_store
```

**Option B: Self-Hosted (Docker)**
```bash
docker run -p 6333:6333 qdrant/qdrant:latest
```

```ini
# .env
VECTOR_STORE_TYPE=qdrant
QDRANT_URL=http://localhost:6333
```

**Option C: Cloud (Qdrant Cloud)**
- Sign up at https://cloud.qdrant.io
- Create cluster
- Get API key and URL

```ini
# .env
VECTOR_STORE_TYPE=qdrant
QDRANT_URL=https://your-project.qdrant.io
QDRANT_API_KEY=your-api-key
```

**Use:**
```python
pipeline = RAGPipeline(vector_store_backend="qdrant")
```

---

### 5️⃣ Pinecone (Managed Cloud) 💳

**Setup (5 minutes):**
1. Sign up at https://www.pinecone.io (free tier available)
2. Create API key
3. Create index named "documents" with dimension **384**
4. Add to .env:

```ini
# .env
VECTOR_STORE_TYPE=pinecone
PINECONE_API_KEY=your-api-key-here
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=documents
```

**Use:**
```python
pipeline = RAGPipeline(vector_store_backend="pinecone")
```

**Pricing:** Free tier includes 1 project, paid starts at $0.60/1M vector hours

---

### 6️⃣ Astra DB (Enterprise) 🔐

**Setup (10 minutes):**
1. Sign up at https://astra.datastax.com
2. Create serverless database
3. Create API token
4. Get database ID and region
5. Add to .env:

```ini
# .env
VECTOR_STORE_TYPE=astradb
ASTRA_DB_ID=your-database-id
ASTRA_DB_REGION=us-east1
ASTRA_DB_TOKEN=your-api-token
```

**Use:**
```python
pipeline = RAGPipeline(vector_store_backend="astradb")
```

**Pricing:** Free tier available, paid based on usage

---

## 🔄 Switching Backends

### Method 1: Configuration File (Simplest)
```ini
# Just change this line in .env
VECTOR_STORE_TYPE=qdrant
```

Then restart your application - it automatically uses the new backend!

### Method 2: Environment Variable
```bash
export VECTOR_STORE_TYPE=pinecone
python run.py api
```

### Method 3: Programmatically
```python
from rag_app.pipeline import RAGPipeline

# Different backends for different use cases
fast_pipeline = RAGPipeline(vector_store_backend="faiss")
cloud_pipeline = RAGPipeline(vector_store_backend="pinecone")
```

## 🧪 Testing Backends

### Check Available Backends
```python
from rag_app.vectorstore import VectorStoreFactory

backends = VectorStoreFactory.list_backends()
print(f"Available: {backends}")
# Output: Available: ['chroma', 'faiss', 'weaviate', 'pinecone', 'qdrant', 'astradb']
```

### Verify Installation
```bash
python scripts/install_vectorstore_deps.py --verify pinecone
```

### Test Backend
```python
from rag_app.vectorstore import VectorStoreFactory

store = VectorStoreFactory.create("faiss")
count = store.get_collection_count()
print(f"Documents in store: {count}")
store.close()
```

### Run Examples
```bash
# Chroma example
python scripts/vector_store_examples.py chroma

# FAISS example
python scripts/vector_store_examples.py faiss

# Switching example
python scripts/vector_store_examples.py switching

# All examples
python scripts/vector_store_examples.py
```

## 🚀 Production Recommendations

### Small Team / Startup
```ini
VECTOR_STORE_TYPE=chroma
# or
VECTOR_STORE_TYPE=faiss
```

### Growing Business (100k+ vectors)
```ini
VECTOR_STORE_TYPE=qdrant
# Self-hosted or Qdrant Cloud
```

### Large Enterprise
```ini
VECTOR_STORE_TYPE=astradb
# Multi-region, enterprise SLA
```

### Serverless / No Ops
```ini
VECTOR_STORE_TYPE=pinecone
# Fully managed, auto-scaling
```

## 📊 Performance Comparison

Approximate query latency for 100k documents:

```
FAISS:       10ms  (⚡ Fastest, local only)
Pinecone:    50ms  (Fast, managed)
Qdrant:      30ms  (Very fast)
Weaviate:   100ms  (Good)
Astra DB:   100ms  (Enterprise)
Chroma:      50ms  (Default)
```

## 🔍 Troubleshooting

### "Backend not found"
```python
# Check available backends
from rag_app.vectorstore import VectorStoreFactory
print(VectorStoreFactory.list_backends())
```

### "Connection refused" (Weaviate/Qdrant)
```bash
# For Weaviate
docker run -d -p 8080:8080 semitechnologies/weaviate:latest

# For Qdrant
docker run -d -p 6333:6333 qdrant/qdrant:latest
```

### "API key invalid" (Pinecone/Astra)
```bash
# Verify credentials in .env
cat .env | grep -E "PINECONE|ASTRA"

# Check logs
tail -f logs/vectorstore/*.log
```

### "ImportError: No module named X"
```bash
# Install specific backend
python scripts/install_vectorstore_deps.py pinecone

# Or install all
pip install -r requirements-vectorstore.txt
```

## 📖 More Information

- **Detailed Guide:** See [VECTOR_STORE_GUIDE.md](./VECTOR_STORE_GUIDE.md)
- **Examples:** Check [scripts/vector_store_examples.py](./scripts/vector_store_examples.py)
- **Configuration:** See [.env.example](./.env.example)
- **Source Code:** [src/rag_app/vectorstore/](./src/rag_app/vectorstore/)

## 🎓 Learning Path

1. **Start:** Use Chroma (default) - understand RAG basics
2. **Experiment:** Try FAISS for speed comparison
3. **Scale:** Use Qdrant or Pinecone for production
4. **Enterprise:** Consider Astra DB for compliance/SLA

## 💡 Pro Tips

### Tip 1: Local Development
```ini
# Development - fast, no external services
VECTOR_STORE_TYPE=faiss
```

### Tip 2: Testing Different Backends
```python
for backend in ["chroma", "faiss", "qdrant"]:
    try:
        pipeline = RAGPipeline(vector_store_backend=backend)
        # Test...
    except ImportError:
        print(f"Skipping {backend} - not installed")
```

### Tip 3: Backup Vector Data
```bash
# Chroma and FAISS use file-based storage - easy backup
cp -r ./data/vector_store ./backups/vector_store_$(date +%Y%m%d)

# Managed services (Pinecone, Astra) have automatic backups
```

### Tip 4: Monitor Backend Health
```bash
# Check logs
tail -f logs/vectorstore/*.log

# Monitor vector count
from rag_app.pipeline import RAGPipeline
stats = RAGPipeline().get_stats()
print(f"Documents: {stats['documents_in_store']}")
```

## 🤝 Support

- **Issues:** Check [troubleshooting](#troubleshooting)
- **Logs:** Look in `logs/vectorstore/` folder
- **Backend Docs:**
  - Chroma: https://docs.trychroma.com
  - FAISS: https://github.com/facebookresearch/faiss
  - Weaviate: https://weaviate.io/developers
  - Qdrant: https://qdrant.tech/documentation
  - Pinecone: https://docs.pinecone.io
  - Astra: https://docs.datastax.com/en/astra

---

**Last Updated:** April 2026
