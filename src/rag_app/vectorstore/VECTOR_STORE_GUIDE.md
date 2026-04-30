# Vector Store Backends Guide

This document explains all available vector store backends in the RAG system and how to configure them.

## Quick Comparison Table

| Backend | Type | Setup | Cost | Scale | Use Case |
|---------|------|-------|------|-------|----------|
| **Chroma** | Local/Embedded | Easy | Free | Small-Medium | Development, small deployments |
| **FAISS** | Local/Embedded | Easy | Free | Small-Medium | Fast local search, research |
| **Weaviate** | Self-hosted/Cloud | Medium | Free/Paid | Medium-Large | Flexible deployments |
| **Qdrant** | Self-hosted/Cloud | Medium | Free/Paid | Medium-Large | High-performance search |
| **Pinecone** | Managed Cloud | Easy | Paid | Large | Serverless, minimal ops |
| **Astra DB** | Managed Cloud | Easy | Paid | Large | Enterprise, multi-region |

## Backend Details

### 1. Chroma (Default) ⭐

**Type:** Local/Embedded Vector Database

**Best For:** Development, small datasets, quick prototyping

**Pros:**
- ✅ No external dependencies
- ✅ Automatic persistence (SQLite + Parquet)
- ✅ Fast for small datasets
- ✅ Zero configuration needed

**Cons:**
- ❌ Not suitable for very large datasets
- ❌ Limited to single machine

**Configuration:**
```ini
VECTOR_STORE_TYPE=chroma
VECTOR_STORE_PATH=./data/vector_store
CHROMA_COLLECTION_NAME=documents
```

**Installation:**
```bash
pip install chromadb
```

**Example Usage:**
```python
from rag_app.pipeline import RAGPipeline

# Uses Chroma by default
pipeline = RAGPipeline()
pipeline.ingest("./data/source")
answer, docs, _ = pipeline.query("What is RAG?")
```

---

### 2. FAISS (Facebook AI Similarity Search)

**Type:** Local/Embedded Vector Search Library

**Best For:** Lightweight deployments, research, very fast local search

**Pros:**
- ✅ Extremely fast similarity search
- ✅ Very small memory footprint
- ✅ Great for offline/offline-first systems
- ✅ Simple to use

**Cons:**
- ❌ Requires manual index rebuilding for updates
- ❌ Not suitable for frequent updates
- ❌ Limited to single machine

**Configuration:**
```ini
VECTOR_STORE_TYPE=faiss
VECTOR_STORE_PATH=./data/vector_store
FAISS_COLLECTION_NAME=documents
```

**Installation:**
```bash
# CPU version (recommended)
pip install faiss-cpu

# GPU version (if you have CUDA)
pip install faiss-gpu
```

**Example Usage:**
```python
from rag_app.pipeline import RAGPipeline

pipeline = RAGPipeline(vector_store_backend="faiss")
pipeline.ingest("./data/source")
answer, docs, _ = pipeline.query("What is RAG?")
```

---

### 3. Weaviate

**Type:** Self-hosted or Cloud Vector Database

**Best For:** Medium-to-large deployments, flexible cloud infrastructure

**Pros:**
- ✅ Both self-hosted and cloud options
- ✅ Excellent for scalability
- ✅ GraphQL API
- ✅ Built-in ML-ready schema

**Cons:**
- ⚠️ Requires setup/deployment
- ⚠️ More complex configuration
- ⚠️ Higher resource requirements

**Configuration:**

**Self-hosted:**
```ini
VECTOR_STORE_TYPE=weaviate
WEAVIATE_URL=http://localhost:8080
```

**Cloud (Weaviate Cloud Service):**
```ini
VECTOR_STORE_TYPE=weaviate
WEAVIATE_URL=https://your-cluster.weaviate.network
WEAVIATE_API_KEY=your-api-key
```

**Installation:**
```bash
pip install weaviate-client
```

**Docker (Self-hosted):**
```bash
docker run -d \
  -p 8080:8080 \
  semitechnologies/weaviate:latest \
  --host 0.0.0.0 \
  --port 8080 \
  --scheme http
```

**Example Usage:**
```python
from rag_app.pipeline import RAGPipeline

pipeline = RAGPipeline(vector_store_backend="weaviate")
pipeline.ingest("./data/source")
```

---

### 4. Qdrant

**Type:** Self-hosted or Cloud Vector Search Engine

**Best For:** High-performance requirements, distributed deployments

**Pros:**
- ✅ Excellent performance for large-scale data
- ✅ Self-hosted and cloud options
- ✅ REST API and gRPC
- ✅ Advanced filtering capabilities
- ✅ Open-source (self-hosted)

**Cons:**
- ⚠️ Requires deployment for self-hosted
- ⚠️ More infrastructure overhead than Chroma/FAISS

**Configuration:**

**Local (storage mode):**
```ini
VECTOR_STORE_TYPE=qdrant
VECTOR_STORE_PATH=./data/vector_store
```

**Self-hosted (Docker):**
```ini
VECTOR_STORE_TYPE=qdrant
QDRANT_URL=http://localhost:6333
```

**Cloud (Qdrant Cloud):**
```ini
VECTOR_STORE_TYPE=qdrant
QDRANT_URL=https://your-project.qdrant.io
QDRANT_API_KEY=your-api-key
```

**Installation:**
```bash
pip install qdrant-client
```

**Docker (Self-hosted):**
```bash
docker run -p 6333:6333 \
  -v $(pwd)/qdrant_storage:/qdrant/storage:z \
  qdrant/qdrant:latest
```

**Example Usage:**
```python
from rag_app.pipeline import RAGPipeline

pipeline = RAGPipeline(vector_store_backend="qdrant")
pipeline.ingest("./data/source")
```

---

### 5. Pinecone ⭐ (Managed Cloud)

**Type:** Fully Managed Cloud Vector Database

**Best For:** Large-scale production deployments, serverless infrastructure

**Pros:**
- ✅ Fully managed (no infrastructure)
- ✅ Automatic scaling
- ✅ Multi-region support
- ✅ Built-in security and backups
- ✅ High availability out-of-the-box

**Cons:**
- ❌ Requires paid subscription
- ❌ API-only (no local option)
- ❌ Vendor lock-in

**Pricing:**
- Free tier: Small projects
- Paid: $0.60-$4.00 per 1M vector-hours depending on index size

**Configuration:**
```ini
VECTOR_STORE_TYPE=pinecone
PINECONE_API_KEY=your-api-key-here
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=documents
```

**Installation:**
```bash
pip install pinecone-client
```

**Getting Started:**
1. Sign up at https://www.pinecone.io
2. Create an API key
3. Create an index with dimension matching your embeddings (384 for all-MiniLM-L6-v2)
4. Add credentials to .env

**Example Usage:**
```python
from rag_app.pipeline import RAGPipeline

pipeline = RAGPipeline(vector_store_backend="pinecone")
pipeline.ingest("./data/source")  # Automatically syncs with Pinecone
```

---

### 6. Astra DB (DataStax) 🔐 (Enterprise Managed)

**Type:** Enterprise Managed Vector Database

**Best For:** Large enterprises, mission-critical deployments, compliance requirements

**Pros:**
- ✅ Enterprise-grade SLA
- ✅ Multi-region replication built-in
- ✅ Advanced security (SOC 2, compliance)
- ✅ Based on Apache Cassandra (battle-tested)
- ✅ Free tier available for development

**Cons:**
- ❌ Requires Astra DB subscription
- ❌ More setup overhead
- ❌ Vendor lock-in

**Pricing:**
- Free tier: Small projects (400M read units/month)
- Paid: Based on operations (reads/writes)

**Configuration:**
```ini
VECTOR_STORE_TYPE=astradb
ASTRA_DB_ID=your-database-id
ASTRA_DB_REGION=us-east1
ASTRA_DB_TOKEN=your-api-token
```

**Installation:**
```bash
pip install astrapy
```

**Getting Started:**
1. Sign up at https://astra.datastax.com
2. Create a serverless database
3. Generate an API token
4. Get your database ID and region
5. Add credentials to .env

**Example Usage:**
```python
from rag_app.pipeline import RAGPipeline

pipeline = RAGPipeline(vector_store_backend="astradb")
pipeline.ingest("./data/source")
```

---

## Decision Guide

### Choose based on your needs:

**Development & Prototyping:**
```
Start with Chroma (default) ✅
- No setup needed
- Works out of the box
- Easy to switch later
```

**Small Production (< 1M vectors):**
```
Chroma or FAISS
- Low cost
- Simple infrastructure
- Good performance
```

**Medium Production (1M-100M vectors):**
```
Qdrant or Weaviate (self-hosted)
- Better scalability
- More control
- Can self-host or use cloud
```

**Large Scale / Enterprise:**
```
Pinecone or Astra DB
- Fully managed
- Automatic scaling
- Enterprise SLA
- Minimal ops overhead
```

**Performance-Critical (Sub-millisecond latency):**
```
FAISS (if single-machine)
Pinecone or Qdrant (if distributed)
- Optimized for speed
- Advanced indexing
```

---

## Switching Backends

Switching between backends is simple:

### Option 1: Configuration File
```ini
# Change this one line in .env
VECTOR_STORE_TYPE=faiss
```

### Option 2: Environment Variable
```bash
export VECTOR_STORE_TYPE=qdrant
python run.py api
```

### Option 3: Code
```python
from rag_app.pipeline import RAGPipeline

# Easy switch
pipeline = RAGPipeline(vector_store_backend="pinecone")
```

**Note:** Each backend stores data separately, so switching requires re-ingesting documents.

---

## Production Deployment Examples

### Small Server (Chroma)
```ini
VECTOR_STORE_TYPE=chroma
VECTOR_STORE_PATH=/var/rag/vectorstore
```

### High-Availability Cloud (Pinecone)
```ini
VECTOR_STORE_TYPE=pinecone
PINECONE_API_KEY=${PINECONE_API_KEY}  # From secrets manager
PINECONE_ENVIRONMENT=us-west1-gcp
```

### Self-Hosted Kubernetes (Qdrant)
```ini
VECTOR_STORE_TYPE=qdrant
QDRANT_URL=http://qdrant-service.rag-namespace:6333
```

### Multi-Region Enterprise (Astra DB)
```ini
VECTOR_STORE_TYPE=astradb
ASTRA_DB_ID=${ASTRA_DB_ID}          # From secrets
ASTRA_DB_TOKEN=${ASTRA_DB_TOKEN}    # From secrets
ASTRA_DB_REGION=us-east1             # Auto-replicated across regions
```

---

## Troubleshooting

### Connection Issues

**Chroma:**
```python
from rag_app.vectorstore import VectorStoreFactory
try:
    store = VectorStoreFactory.create("chroma")
except Exception as e:
    print(f"Error: {e}")
    # Check: ./data/vector_store exists
```

**Weaviate:**
```bash
# Check if Weaviate is running
curl http://localhost:8080/v1/.well-known/ready
```

**Qdrant:**
```bash
# Check health
curl http://localhost:6333/health
```

**Pinecone:**
```python
# Test API key
from pinecone import Pinecone
pc = Pinecone(api_key="your-key")
print(pc.list_indexes())
```

**Astra DB:**
```python
# Test credentials
from astrapy.db import AstraDB
db = AstraDB(token="your-token", api_endpoint="your-endpoint")
```

---

## Performance Benchmarks

Approximate performance for 100k documents on standard hardware:

| Operation | Chroma | FAISS | Weaviate | Qdrant | Pinecone | Astra |
|-----------|--------|-------|----------|--------|----------|-------|
| Ingest | 5m | 3m | 8m | 6m | 10m | 12m |
| Search | 50ms | 10ms | 100ms | 30ms | 50ms | 100ms |
| Memory | 500MB | 200MB | 1.5GB | 800MB | Cloud | Cloud |
| Setup | 1m | 1m | 20m | 15m | 5m | 10m |

*Benchmarks are approximate and vary based on dataset and hardware*

---

## Migration Between Backends

To migrate from one backend to another:

```python
from rag_app.vectorstore import VectorStoreFactory

# Export from old backend
old_store = VectorStoreFactory.create("chroma")
documents = []
for i in range(old_store.get_collection_count()):
    # Fetch documents
    pass

# Import to new backend
new_store = VectorStoreFactory.create("pinecone")
new_store.add_documents(ids, documents, embeddings, metadatas)
```

Or use the built-in migration utility:
```bash
python scripts/migrate_vectorstore.py --from chroma --to pinecone
```

---

## Monitoring Vector Store Health

```python
from rag_app.pipeline import RAGPipeline

pipeline = RAGPipeline()
stats = pipeline.get_stats()

print(f"Documents: {stats['documents_in_store']}")
print(f"Vector Store: {stats['vector_store']}")
print(f"Backend: {stats['vector_store_backend']}")
```

Monitor logs:
```bash
tail -f logs/vectorstore/chroma_store.log
tail -f logs/vectorstore/factory.log
```

---

## Custom Backends

To add a custom vector store backend:

1. Create class inheriting from `VectorStoreBase`
2. Implement all abstract methods
3. Register with factory:

```python
from rag_app.vectorstore import VectorStoreFactory, VectorStoreBase

class MyCustomStore(VectorStoreBase):
    # Implement methods...
    pass

VectorStoreFactory.register_backend("custom", MyCustomStore)

# Use it
from rag_app.pipeline import RAGPipeline
pipeline = RAGPipeline(vector_store_backend="custom")
```

---

## Cost Comparison (for 1M vectors)

Approximate monthly costs:

- **Chroma**: $0 (self-hosted)
- **FAISS**: $0 (self-hosted)
- **Weaviate**: $0-500 (depends on deployment)
- **Qdrant**: $0-200 (self-hosted) or $100+ (cloud)
- **Pinecone**: $600+ (managed)
- **Astra DB**: $0-500 (usage-based)

**Note:** These are estimates and vary significantly based on query patterns and data size.

---

## FAQs

**Q: Which backend should I use?**
A: Start with Chroma (default), switch to Pinecone/Qdrant for production.

**Q: Can I use multiple backends?**
A: Yes, create multiple pipeline instances with different backends.

**Q: How do I backup my vector database?**
A: Chroma and FAISS support file backups. Managed services (Pinecone, Astra) have automatic backups.

**Q: What's the maximum vector size?**
A: Generally 2048 dimensions. Our default is 384 (all-MiniLM-L6-v2).

**Q: Can I use a different embedding model?**
A: Yes, change `EMBEDDING_MODEL` in .env. Your vectors will have different dimensions.

---

Last Updated: April 2026
