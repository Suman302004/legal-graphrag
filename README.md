⚖️ Legal GraphRAG

Evidence-Grounded Legal Reasoning with Knowledge Graphs + RAG







Ask a legal question → retrieve relevant evidence → traverse connected precedents → generate an evidence-grounded answer.

Legal reasoning is not only about finding similar passages. Judgments cite, rely on, and refer to other judgments. This project combines semantic retrieval with citation-aware knowledge graph traversal to provide richer legal context before generating an answer.

🚀 What Makes This Different?

Traditional RAG

Legal GraphRAG

Finds semantically similar text

Finds text and legal relationships

Primarily document-centric

Case + precedent-centric

Flat retrieval

Graph-based expansion

Can miss important authorities

Traverses connected precedents

Context comes mainly from retrieved chunks

Context combines vector + graph evidence

The core idea

                 Legal Question
                       │
                       ▼
              Semantic Retrieval
                       │
                       ▼
                 Primary Case
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
       Relevant Chunks      Citation Graph
                                 │
                                 ▼
                         Connected Precedents
                                 │
             └──────────┬────────┘
                        ▼
                 Hybrid Evidence
                        │
                        ▼
                  Local LLM
                        │
                        ▼
              Grounded Legal Answer

🧠 System Architecture



The system follows a multi-stage pipeline:

Judgment ingestion — Supreme Court judgment documents are collected and processed.

Text extraction — PDF content is converted into machine-readable text.

Chunking — Long judgments are divided into retrieval-friendly chunks.

Embedding generation — Chunks are converted into dense vectors using all-MiniLM-L6-v2.

Vector retrieval — FAISS retrieves semantically relevant passages.

Citation extraction — Legal citations are identified from judgment text.

Citation resolution — Citations are matched against Supreme Court metadata.

Knowledge graph construction — Cases and their relationships are represented in Neo4j.

Graph expansion — Connected precedents are retrieved from the graph.

Hybrid evidence construction — Semantic and graph evidence are combined.

Answer generation — Ollama/Llama 3.2 generates an evidence-grounded response.

🕸️ Knowledge Graph

The current graph contains:

7 case nodes

6 case relationships

1 primary Supreme Court judgment

6 connected authorities

Current relationships:

2025 INSC 24
     │
     ├── CITES ──────────► 1961 INSC 197
     ├── CITES ──────────► 1988 INSC 204
     ├── CITES ──────────► 1993 INSC 221
     ├── CITES ──────────► 1994 INSC 573
     ├── RELIES_ON ──────► 1995 INSC 114
     └── REFERRED_TO ────► 2000 INSC 497

This allows the system to move from a primary judgment to the authorities connected to it.

⚖️ Primary Case

The current implementation uses:

2025 INSC 24 — Krishna Devi @ Sabitri Devi (Rani) M/s S.R. Engineering Construction v. Union of India & Ors.

The system uses this judgment as the primary case and retrieves its connected authorities through the knowledge graph.

💬 Example Legal Question

Question

What is the limitation period for filing objections to the arbitration award?

Retrieval

The system identifies the primary case and expands the evidence through its six graph-connected authorities:

2025 INSC 24
     │
     ├── 1961 INSC 197
     ├── 1988 INSC 204
     ├── 1993 INSC 221
     ├── 1994 INSC 573
     ├── 1995 INSC 114
     └── 2000 INSC 497

Answer

The Supreme Court applied a 30-day limitation period under Article 119(b) of the First Schedule to the Limitation Act, 1963.

The relevant trigger was service of notice of the filing of the award. In this case, the respondents were held to have sufficient awareness of the award's filing on 21 September 2022. The later formal notice dated 18 November 2022 was treated as having no significance in the circumstances.

Accordingly, the limitation period expired on 20 October 2022, and the lower courts were found to have erred in treating the limitation period as still running.

🔎 Retrieval Pipeline

┌──────────────────────────────┐
│ Supreme Court Judgments      │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ PDF / Text Extraction        │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ Chunking                     │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ Sentence Embeddings          │
│ all-MiniLM-L6-v2             │
└──────────────┬───────────────┘
               ▼
        ┌───────────────┐
        │     FAISS     │
        │ Vector Search │
        └───────┬───────┘
                │
                │
                ├─────────────────────┐
                │                     │
                ▼                     ▼
        Semantic Evidence      Citation Extraction
                                      │
                                      ▼
                              Citation Resolution
                                      │
                                      ▼
                               ┌────────────┐
                               │   Neo4j    │
                               │ Legal Graph│
                               └─────┬──────┘
                                     │
                                     ▼
                              Graph Expansion
                                     │
                ┌────────────────────┘
                ▼
        ┌──────────────────┐
        │ Hybrid Retrieval │
        │ Vector + Graph   │
        └────────┬─────────┘
                 ▼
        ┌──────────────────┐
        │ Evidence Context │
        └────────┬─────────┘
                 ▼
        ┌──────────────────┐
        │ Ollama / Llama   │
        │      3.2         │
        └────────┬─────────┘
                 ▼
        ┌──────────────────┐
        │ Grounded Answer  │
        └──────────────────┘

🛠️ Technology Stack

Layer

Technology

Programming

Python

Embeddings

Sentence Transformers

Embedding Model

all-MiniLM-L6-v2

Vector Search

FAISS

Knowledge Graph

Neo4j

Local LLM

Ollama / Llama 3.2

Data Processing

Pandas / PyArrow

PDF Processing

PyMuPDF / PyPDF

Machine Learning

Scikit-learn

Version Control

Git / GitHub

📁 Project Structure

legal-graphrag/
│
├── data/
│   ├── cases.csv
│   ├── case_relationships_raw.csv
│   ├── resolved_relationships.csv
│   ├── judgments/
│   ├── metadata/
│   └── precedents/
│
├── docs/
│   └── architecture.png
│
├── src/
│   ├── build_case_nodes.py
│   ├── chunk_documents.py
│   ├── create_embeddings.py
│   ├── download_precedents.py
│   ├── extract_case_law.py
│   ├── extract_document.py
│   ├── extract_precedent_text.py
│   ├── find_precedents.py
│   ├── graph_context.py
│   ├── graph_queries.py
│   ├── graph_rag_qa.py
│   ├── graph_rag_retriever.py
│   ├── graph_retriever.py
│   ├── hybrid_retrieval.py
│   ├── load_into_neo4j.py
│   ├── resolve_citation.py
│   ├── retrieve.py
│   ├── retrieve_chunks.py
│   └── setup_precedents.py
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt

⚡ Quick Start

1. Clone

git clone https://github.com/Suman302004/legal-graphrag.git
cd legal-graphrag

2. Create a virtual environment

Windows:

python -m venv venv
venv\Scripts\activate

3. Install dependencies

pip install -r requirements.txt

4. Configure Neo4j

Create a local .env file using .env.example:

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

Never commit your real .env file.

5. Configure Ollama

Install Ollama and pull the local model:

ollama pull llama3.2:3b

6. Prepare precedents

python src/setup_precedents.py

7. Run the QA pipeline

python src/graph_rag_qa.py

📊 Current Configuration

Embedding Model     : all-MiniLM-L6-v2
Embedding Dimension : 384
Vector Store        : FAISS
Graph Database      : Neo4j
LLM                 : llama3.2:3b
Top-K Retrieval     : 5
Graph Nodes         : 7
Graph Relationships : 6

🔬 Core Engineering Concepts

Hybrid Retrieval

The project combines two complementary signals:

Vector retrieval

Finds passages that are semantically similar to the question.

Graph retrieval

Finds cases connected through legal relationships.

Together:

Semantic Similarity
        +
Legal Relationships
        ↓
Richer Evidence Context

Citation Resolution

The pipeline extracts case citations from judgment text and resolves them against Supreme Court metadata before creating graph relationships.

Evidence-Grounded Generation

Instead of asking the LLM to answer from general knowledge, the system constructs a context containing retrieved case evidence and connected precedent information before generating the response.

🎯 Project Goals

The system is designed to support legal research workflows by:

retrieving relevant legal passages

identifying connected precedents

expanding retrieval through citation relationships

combining graph and vector evidence

generating answers grounded in retrieved legal material

keeping inference local through Ollama

🚧 Future Roadmap

Expand to a larger Supreme Court judgment corpus

Multi-case graph construction

More sophisticated legal entity extraction

Graph-based relevance ranking

Explainable retrieval paths

Confidence scoring

Legal QA evaluation benchmark

Web-based interface

REST API

Dockerized deployment

Temporal legal reasoning

⚠️ Disclaimer

This project is intended for research and educational purposes.

It is not a substitute for professional legal advice, legal representation, or independent verification of judicial authorities.

👨‍💻 Author

R Suman

AI & ML Engineering Student
BMS College of Engineering, Bengaluru

GitHub

⭐ Project

If you find the project interesting, consider starring the repository.

Repository:
https://github.com/Suman302004/legal-graphrag
