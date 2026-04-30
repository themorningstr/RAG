"""Vector Store Architecture & Decision Tree"""

# Vector Store Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     RAG Application Layer                    │
├─────────────────────────────────────────────────────────────┤
│  Pipeline (rag_pipeline.py)                                 │
│  - Ingestion, Query, Statistics                             │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │ VectorStoreFactory    │
         │ (factory.py)          │
         └───────────┬───────────┘
                     │
         ┌───────────┴───────────────────────────────┐
         │      VectorStoreBase (abstract)           │
         │      - initialize()                       │
         │      - add_documents()                    │
         │      - search()                           │
         │      - delete_collection()                │
         │      - get_collection_count()             │
         │      - persist()                          │
         │      - close()                            │
         └───────────┬───────────────────────────────┘
                     │
        ┌────────────┼────────────┬────────────┬──────────┐
        │            │            │            │          │
        ▼            ▼            ▼            ▼          ▼
    ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
    │ Chroma │  │ FAISS  │  │Weaviate│  │ Qdrant │  │Pinecone│
    │(Local) │  │(Local) │  │(Cloud) │  │(Cloud) │  │(Cloud) │
    └────────┘  └────────┘  └────────┘  └────────┘  └────────┘
                                                         
                            ┌──────────┐
                            │ Astra DB │
                            │(Cloud)   │
                            └──────────┘
```

## Decision Tree

```
                         START: Choose Vector Store
                                 │
                    ┌────────────┴────────────┐
                    │                         │
            Question: Local or Cloud?    ← Deployment Strategy
                    │                         │
        ┌───────────┴───────────┐              │
        │                       │              │
       LOCAL                   CLOUD           │
        │                       │              │
        │    ┌──────────┴──────┬┴─────┐        │
        │    │                 │      │        │
    ┌───┴────┴──┐    ┌────────┘  ┌──┘     └────┐
    │            │    │           │         │
Question:    Question: Question: Self-  Question:
Speed or     Self-   Scale     hosted? Budget?
Simple?    hosted?  needs?        │        │
    │       │        │        ┌───┴───┐    │
    │       │        │        │       │    │
   YES      YES     Large   YES     NO    Low
    │        │        │       │       │    │
    │        │        │    ┌──┴──┐    │    │
    ▼        ▼        ▼    │     ▼    │    ▼
  FAISS   Weaviate  Qdrant │  Astra   Pinecone
           Self-            │
           Hosted           │
           Docker           │
                         Pinecone/
                         Qdrant Cloud
                         /Weaviate Cloud
```

## Backend Selection Matrix

```
┌─────────────────────────────────────────────────────────────────┐
│                    Backend Selection Guide                       │
├─────────────────────────────────────────────────────────────────┤

Development & Testing:
  ├─ Chroma    ✅ (Default, no setup)
  └─ FAISS     ✅ (Fast local testing)

Small Production (< 100k vectors):
  ├─ Chroma          ✅ (Sufficient)
  └─ FAISS           ✅ (Good performance)

Medium Production (100k - 10M vectors):
  ├─ Self-Hosted Weaviate   ✅ (Control)
  ├─ Self-Hosted Qdrant     ✅ (Performance)
  ├─ Qdrant Cloud           ✅ (Managed)
  └─ Weaviate Cloud         ✅ (Flexible)

Large Production (> 10M vectors):
  ├─ Pinecone       ✅ (Serverless)
  ├─ Astra DB       ✅ (Enterprise)
  └─ Qdrant Cloud   ✅ (High performance)

Enterprise / Compliance:
  └─ Astra DB       ✅ (SOC 2, Enterprise SLA)

Cost-Sensitive:
  ├─ Chroma         ✅ (Free)
  ├─ FAISS          ✅ (Free)
  ├─ Self-Hosted Weaviate  ✅ (Free, pay for infra)
  └─ Self-Hosted Qdrant    ✅ (Free, pay for infra)

No Ops / Serverless:
  ├─ Pinecone       ✅ (Fully managed)
  └─ Astra DB       ✅ (Fully managed)
```

## Data Flow Diagram

```
                    Input Documents
                          │
                          ▼
                  ┌───────────────┐
                  │   Ingestion   │
                  │   Module      │
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │   Embeddings  │
                  │   Module      │
                  └───────┬───────┘
                          │
                  (Vector Embeddings)
                          │
                          ▼
              ┌─────────────────────────┐
              │  Vector Store Backend   │
              │  (Pluggable)            │
              ├─────────────────────────┤
              │ - Chroma  (SQLite)      │
              │ - FAISS   (Files)       │
              │ - Weaviate(GraphQL API) │
              │ - Qdrant  (REST API)    │
              │ - Pinecone(Cloud API)   │
              │ - Astra   (Cassandra)   │
              └──────────┬──────────────┘
                         │
                  ┌──────┴──────┐
                  │             │
            [Storage]    [Memory/Cache]
                  │             │
        ┌─────────▼─────────────▼──────────┐
        │      Search (Query Time)         │
        │                                  │
        │  1. User Query                   │
        │  2. Query Embedding              │
        │  3. Similarity Search            │
        │  4. Return Top-K Results         │
        └──────────┬───────────────────────┘
                   │
                   ▼
            Retrieved Documents
```

## Configuration Flow

```
┌─────────────────────────────────────────────────────────┐
│  .env Configuration File                                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  VECTOR_STORE_TYPE=qdrant    ← Backend Selection       │
│                                                         │
│  # Backend-Specific Settings                           │
│  QDRANT_URL=http://localhost:6333                      │
│  QDRANT_API_KEY=...                                    │
│                                                         │
│  # Common Settings                                     │
│  VECTOR_STORE_PATH=./data/vector_store                 │
│  EMBEDDING_MODEL=sentence-transformers/...            │
│                                                         │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────▼───────────┐
         │  config.py            │
         │  (Settings Class)      │
         │  - Validation         │
         │  - Type Checking      │
         │  - Defaults           │
         └───────────┬───────────┘
                     │
         ┌───────────▼────────────┐
         │  VectorStoreFactory    │
         │  - Reads config        │
         │  - Creates backend     │
         │  - Initializes         │
         └───────────┬────────────┘
                     │
         ┌───────────▼────────────┐
         │  Selected Backend      │
         │  - Connected           │
         │  - Ready for use       │
         └────────────────────────┘
```

## Operation Timeline

```
┌─────────────────────────────────────────────────────────────┐
│             Typical RAG Operation Flow                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  SETUP PHASE (One-time)                                   │
│  │                                                         │
│  ├─ 1. Read .env config                                   │
│  ├─ 2. Initialize vector store backend                    │
│  ├─ 3. Create/connect collection                          │
│  └─ 4. Verify connection                                  │
│                                                             │
│  INGESTION PHASE (Once per dataset)                        │
│  │                                                         │
│  ├─ 5. Load documents                                     │
│  ├─ 6. Chunk text                                         │
│  ├─ 7. Generate embeddings                                │
│  ├─ 8. Store in vector database                           │
│  └─ 9. Persist to disk (if applicable)                    │
│                                                             │
│  QUERY PHASE (Real-time, per user request)                │
│  │                                                         │
│  ├─ 10. Receive query                                     │
│  ├─ 11. Embed query                                       │
│  ├─ 12. Search in vector database                         │
│  ├─ 13. Retrieve top-k results                            │
│  ├─ 14. Rank/rerank results (optional)                    │
│  └─ 15. Return to user                                    │
│                                                             │
│  MONITORING PHASE (Continuous)                            │
│  │                                                         │
│  ├─ 16. Log operations                                    │
│  ├─ 17. Track metrics                                     │
│  ├─ 18. Monitor health                                    │
│  └─ 19. Handle errors                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Backend Comparison by Dimension

```
╔═══════════════════════════════════════════════════════════════╗
║  SETUP DIFFICULTY SPECTRUM                                   ║
╠═══════════════════════════════════════════════════════════════╣
║  Easy          ▓▓▓▓▓  Chroma, FAISS, Pinecone                ║
║  Medium        ▓▓▓    Weaviate, Qdrant (cloud)               ║
║  Complex       ▓      Weaviate, Qdrant (self-hosted)         ║
║  Enterprise    ▓▓     Astra DB                                ║
╚═══════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════╗
║  QUERY SPEED SPECTRUM                                        ║
╠═══════════════════════════════════════════════════════════════╣
║  Fastest       ▓▓▓▓▓  FAISS (10ms), Qdrant (30ms)             ║
║  Fast          ▓▓▓▓   Pinecone (50ms), Chroma (50ms)          ║
║  Good          ▓▓▓    Weaviate (100ms)                        ║
║  Acceptable    ▓▓     Astra DB (100ms)                        ║
╚═══════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════╗
║  COST SPECTRUM (Monthly, 1M vectors)                         ║
╠═══════════════════════════════════════════════════════════════╣
║  Free          ▓▓▓▓▓  Chroma, FAISS, Self-hosted             ║
║  Low           ▓      $0-100                                  ║
║  Medium        ▓▓     $100-500 (Qdrant Cloud)                 ║
║  High          ▓▓▓    $600+ (Pinecone)                        ║
║  Enterprise    ▓▓▓▓   Usage-based (Astra)                     ║
╚═══════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════╗
║  SCALABILITY SPECTRUM                                        ║
╠═══════════════════════════════════════════════════════════════╣
║  Small         ▓      Chroma, FAISS (< 1M vectors)            ║
║  Medium        ▓▓     Self-hosted (1M - 100M vectors)         ║
║  Large         ▓▓▓    Cloud backends (100M+ vectors)          ║
║  Enterprise    ▓▓▓▓▓  Astra, Pinecone (unlimited)             ║
╚═══════════════════════════════════════════════════════════════╝
```

## Switching Backend Flow

```
┌──────────────────────────────────────┐
│ Decision: Switch to New Backend      │
└────────────┬─────────────────────────┘
             │
    ┌────────▼────────┐
    │ Update .env:    │
    │ VECTOR_STORE_   │
    │ TYPE=new_name   │
    └────────┬────────┘
             │
    ┌────────▼────────────────────┐
    │ Restart Application          │
    │ (Settings reloaded)          │
    └────────┬────────────────────┘
             │
    ┌────────▼────────────────────┐
    │ Factory detects change       │
    │ Creates new backend instance │
    └────────┬────────────────────┘
             │
    ┌────────▼────────────────────┐
    │ New backend initializes      │
    │ (clean storage, empty)       │
    └────────┬────────────────────┘
             │
    ┌────────▼────────────────────┐
    │ Reingest documents           │
    │ (pipeline.ingest(...))       │
    └────────┬────────────────────┘
             │
    ┌────────▼────────────────────┐
    │ ✅ New backend ready!         │
    │ Same API, different engine   │
    └──────────────────────────────┘

NOTE: Each backend maintains separate storage
      No data migration needed (reingest once)
      Instant backend switching via config
```

## Error Handling Flow

```
┌─────────────────────────────────────┐
│  Vector Store Operation              │
└────────────┬────────────────────────┘
             │
    ┌────────▼────────────┐
    │ Try Operation       │
    └────────┬────────────┘
             │
    ┌────────┴────────────────────────┐
    │                                  │
    ▼                                  ▼
  SUCCESS                            ERROR
    │                                  │
    ├─ Return Result          ┌────────┴────────┐
    ├─ Log INFO               │                 │
    └─ Continue               ├─ Connection Error
                              │  (retry logic)
                              │
                              ├─ Invalid Data
                              │  (VectorStoreError)
                              │
                              ├─ API Error
                              │  (with code)
                              │
                              ├─ Log ERROR
                              ├─ Log Stack Trace
                              └─ Raise Exception
```

## Multi-Backend Usage Pattern

```
Production Setup (Multiple Backends):

┌─────────────────────────────────────────────────────────┐
│                  Application                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────┐      ┌─────────────────┐          │
│  │ Analytics       │      │ Production      │          │
│  │ Pipeline        │      │ Pipeline        │          │
│  └────────┬────────┘      └────────┬────────┘          │
│           │                        │                    │
│     VECTOR_STORE_TYPE=     VECTOR_STORE_TYPE=          │
│     qdrant (self-hosted)   pinecone (managed)          │
│           │                        │                    │
│  ┌────────▼────────────┐  ┌────────▼────────────┐      │
│  │ Qdrant Server       │  │ Pinecone Cloud      │      │
│  │ (Full Control)      │  │ (Zero Ops)          │      │
│  │ (Lower Cost)        │  │ (Higher SLA)        │      │
│  └─────────────────────┘  └─────────────────────┘      │
│           │                        │                    │
│  ┌────────▼──────────────────────┴────────┐            │
│  │        Unified RAG Pipeline API         │            │
│  │        (Same interface both sides)      │            │
│  └─────────────────────────────────────────┘            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Quick Reference

| Need | Backend | Setup | Cost |
|------|---------|-------|------|
| **Get Started Fast** | Chroma | 5 min | Free |
| **Fastest Speed** | FAISS | 5 min | Free |
| **Flexible Self-Hosted** | Weaviate | 20 min | Free |
| **High Performance Self-Hosted** | Qdrant | 15 min | Free |
| **Managed Serverless** | Pinecone | 10 min | $$$ |
| **Enterprise Grade** | Astra DB | 10 min | $$$ |

---

**Last Updated:** April 30, 2026
