\# Legal GraphRAG — Evidence-Grounded Legal Analysis



A GraphRAG-based legal analysis system that combines vector retrieval, knowledge graphs, hybrid retrieval, and a local LLM to answer questions over Indian Supreme Court judgments.



The project focuses on improving legal question answering by combining semantic similarity with citation-based relationships between judgments, allowing relevant precedents to be retrieved and incorporated into the answer.



\---



\## Overview



Traditional Retrieval-Augmented Generation (RAG) primarily retrieves documents based on semantic similarity.



Legal reasoning often requires more than finding similar text.



A judgment may:



\- cite another judgment

\- rely on a previous decision

\- refer to an earlier authority

\- establish a legal principle that is interpreted through later cases



This project addresses that requirement by combining:



\*\*Vector Retrieval + Knowledge Graphs + Hybrid Retrieval + Local LLM\*\*



The system uses a Supreme Court judgment as the primary case and expands retrieval through its connected precedents.



\---



\## Key Features



\- Semantic retrieval using sentence-transformer embeddings

\- FAISS-based vector search

\- Neo4j knowledge graph for case relationships

\- Citation extraction and resolution

\- Graph-based precedent expansion

\- Hybrid retrieval combining semantic and graph evidence

\- Local LLM inference using Ollama

\- Evidence-grounded legal question answering

\- Automatic precedent downloading and text extraction

\- Metadata-based precedent resolution

\- No external LLM API required for inference



\---



\## System Architecture



```text

&#x20;                Supreme Court Judgments

&#x20;                         |

&#x20;                         v

&#x20;                 Text Extraction

&#x20;                         |

&#x20;                         v

&#x20;                      Chunking

&#x20;                         |

&#x20;                         v

&#x20;                Sentence Embeddings

&#x20;                         |

&#x20;                         v

&#x20;                   FAISS Index

&#x20;                         |

&#x20;            +------------+------------+

&#x20;            |                         |

&#x20;            v                         v

&#x20;     Semantic Retrieval        Citation Extraction

&#x20;                                      |

&#x20;                                      v

&#x20;                               Citation Resolution

&#x20;                                      |

&#x20;                                      v

&#x20;                               Neo4j Knowledge Graph

&#x20;                                      |

&#x20;                                      v

&#x20;                               Graph-Based Expansion

&#x20;            |                         |

&#x20;            +------------+------------+

&#x20;                         |

&#x20;                         v

&#x20;                  Hybrid Retrieval

&#x20;                         |

&#x20;                         v

&#x20;                Evidence Construction

&#x20;                         |

&#x20;                         v

&#x20;                   Ollama LLM

&#x20;                         |

&#x20;                         v

&#x20;             Evidence-Grounded Answer







Graph Structure



The knowledge graph represents relationships between Supreme Court cases.



Example:



2025 INSC 24

&#x20;    |

&#x20;    +---- CITES ------> 1961 INSC 197

&#x20;    |

&#x20;    +---- CITES ------> 1988 INSC 204

&#x20;    |

&#x20;    +---- CITES ------> 1993 INSC 221

&#x20;    |

&#x20;    +---- CITES ------> 1994 INSC 573

&#x20;    |

&#x20;    +---- RELIES\_ON --> 1995 INSC 114

&#x20;    |

&#x20;    +---- REFERRED\_TO -> 2000 INSC 497



The graph currently contains the primary judgment and six connected precedent cases.





Technologies

Component	Technology

Language	Python

Vector Embeddings	Sentence Transformers

Embedding Model	all-MiniLM-L6-v2

Vector Database	FAISS

Knowledge Graph	Neo4j

LLM	Ollama / Llama 3.2

PDF Processing	PyPDF

Data Processing	Pandas

Version Control	Git / GitHub

Project Structure

legal-graphrag/

│

├── data/

│   ├── cases.csv

│   ├── case\_relationships\_raw.csv

│   ├── resolved\_relationships.csv

│   │

│   ├── judgments/

│   │   ├── 2025\_1\_81\_92\_EN.txt

│   │   └── chunks.csv

│   │

│   ├── metadata/

│   │   ├── metadata\_1962.parquet

│   │   ├── metadata\_1988.parquet

│   │   ├── metadata\_1993.parquet

│   │   ├── metadata\_1994.parquet

│   │   ├── metadata\_1995.parquet

│   │   ├── metadata\_1999.parquet

│   │   ├── metadata\_2000.parquet

│   │   └── metadata\_2025.parquet

│   │

│   └── precedents/

│       └── precedents.json

│

├── src/

│   ├── build\_case\_nodes.py

│   ├── chunk\_documents.py

│   ├── create\_embeddings.py

│   ├── download\_precedents.py

│   ├── extract\_case\_law.py

│   ├── extract\_document.py

│   ├── extract\_precedent\_text.py

│   ├── find\_precedents.py

│   ├── graph\_context.py

│   ├── graph\_queries.py

│   ├── graph\_rag\_qa.py

│   ├── graph\_rag\_retriever.py

│   ├── graph\_retriever.py

│   ├── hybrid\_retrieval.py

│   ├── inspect\_pdf\_source.py

│   ├── load\_into\_neo4j.py

│   ├── resolve\_citation.py

│   ├── retrieve.py

│   ├── retrieve\_chunks.py

│   └── setup\_precedents.py

│

├── .gitignore

└── README.md

Primary Case



The current implementation uses:



2025 INSC 24



Krishna Devi @ Sabitri Devi (Rani) M/s S.R. Engineering Construction v. Union of India \& Ors.



The system uses this judgment as the primary case and retrieves its connected authorities through the knowledge graph.



Example Legal Question

Question



What is the limitation period for filing objections to the arbitration award?



Evidence Used



The system retrieves the primary judgment and its connected precedents through the hybrid retrieval pipeline.



The graph contains six connected authorities:



1961 INSC 197

1988 INSC 204

1993 INSC 221

1994 INSC 573

1995 INSC 114

2000 INSC 497

Answer



The Supreme Court applied a 30-day limitation period under Article 119(b) of the First Schedule to the Limitation Act, 1963.



The relevant trigger was service of notice of the filing of the award. In the case, the respondents were held to have sufficient awareness of the award's filing on 21 September 2022. The Court treated the later formal notice dated 18 November 2022 as having no significance in the circumstances.



Accordingly, the limitation period expired on 20 October 2022, and the lower courts were found to have erred in treating the limitation period as still running.



Retrieval Pipeline



The retrieval process consists of several stages.



1\. Document Processing



Judgment PDFs are converted into text and divided into manageable chunks.



2\. Embedding Generation



Chunks are converted into dense vector representations using:



sentence-transformers/all-MiniLM-L6-v2

3\. Vector Retrieval



FAISS performs semantic similarity search to identify relevant portions of the judgment.



4\. Citation Extraction



Legal citations are extracted from the judgment text.



5\. Citation Resolution



Extracted citations are resolved against Supreme Court judgment metadata.



6\. Knowledge Graph Construction



Resolved cases are represented as nodes in Neo4j with relationships such as:



CITES

RELIES\_ON

REFERRED\_TO

7\. Graph Expansion



Once relevant cases are identified, connected precedent cases are retrieved from the graph.



8\. Hybrid Evidence Construction



Semantic evidence and graph-connected precedent evidence are combined.



9\. Answer Generation



The resulting evidence is provided to the local LLM for legal question answering.



Running the Project

1\. Clone the repository

git clone https://github.com/Suman302004/legal-graphrag.git

cd legal-graphrag

2\. Create a virtual environment



Windows:



python -m venv venv

venv\\Scripts\\activate

3\. Install dependencies

pip install -r requirements.txt

4\. Install and configure Neo4j



Run Neo4j locally and configure the connection used by the project.



The application expects:



NEO4J\_URI

NEO4J\_USER

NEO4J\_PASSWORD



Do not commit your actual password.



5\. Install Ollama



The project uses Ollama for local LLM inference.



The current implementation uses:



llama3.2:3b



Pull the model using:



ollama pull llama3.2:3b

6\. Prepare precedent data



The precedent setup script can be used to download and process the required precedent judgments:



python src/setup\_precedents.py

7\. Run the GraphRAG QA system

python src/graph\_rag\_qa.py



The system accepts legal questions and returns evidence-grounded answers.



Environment Configuration



Create a local .env file:



NEO4J\_URI=bolt://localhost:7687

NEO4J\_USER=neo4j

NEO4J\_PASSWORD=your\_password



The .env file is excluded from Git using .gitignore.



Why GraphRAG?



Legal documents are highly interconnected.



A purely semantic retrieval system may find passages that are textually similar but miss important relationships between cases.



GraphRAG introduces an additional reasoning structure:



Question

&#x20;  |

&#x20;  v

Relevant Passage

&#x20;  |

&#x20;  v

Primary Case

&#x20;  |

&#x20;  v

Connected Precedents

&#x20;  |

&#x20;  v

Legal Authorities



This allows the system to incorporate both semantic relevance and legal citation structure during retrieval.



Current Graph



The current graph contains:



7 Case Nodes

6 Case Relationships



The primary case is connected to six precedent authorities.



Current Retrieval Configuration



The implementation currently uses:



Top-K Retrieval: 5

Embedding Dimension: 384

Embedding Model: all-MiniLM-L6-v2

LLM: llama3.2:3b

Vector Store: FAISS

Graph Database: Neo4j

Project Goals



The main objective is to build a legal research assistant capable of:



retrieving relevant legal passages

identifying connected precedents

expanding retrieval through citation relationships

combining graph and vector evidence

generating answers grounded in retrieved legal material

Future Improvements



Potential extensions include:



Multi-case graph construction

Larger Supreme Court judgment corpus

More sophisticated legal entity extraction

Temporal legal reasoning

Improved citation classification

Graph-based ranking

Explainable retrieval paths

Confidence scoring

Larger local or hosted LLMs

Evaluation benchmarks for legal question answering

Web-based user interface

REST API deployment

Dockerized deployment

Disclaimer



This project is intended for research and educational purposes.



It is not a substitute for professional legal advice, legal representation, or independent verification of judicial authorities.



Author



R Suman



AI \& ML Engineering Student

BMS College of Engineering, Bengaluru



GitHub: https://github.com/Suman302004

