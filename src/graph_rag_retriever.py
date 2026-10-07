import os
import pandas as pd
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHUNKS_PATH = os.path.join(
    BASE_DIR,
    "data",
    "judgments",
    "chunks_with_embeddings.csv"
)

INDEX_PATH = os.path.join(
    BASE_DIR,
    "data",
    "judgments",
    "chunks.index"
)

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Suman@9699"


# ============================================================
# LOAD DATA
# ============================================================

print("Loading chunks...")

chunks_df = pd.read_csv(CHUNKS_PATH)

print(f"Chunks loaded: {len(chunks_df)}")


print("\nLoading FAISS index...")

index = faiss.read_index(INDEX_PATH)

print(f"FAISS vectors: {index.ntotal}")
print(f"Vector dimension: {index.d}")


print("\nLoading embedding model...")

embedding_model = SentenceTransformer(EMBEDDING_MODEL)

print("Embedding model loaded.")


# ============================================================
# NEO4J CONNECTION
# ============================================================

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)

driver.verify_connectivity()

print("Connected to Neo4j successfully.")


# ============================================================
# VECTOR SEARCH
# ============================================================

def vector_search(question, top_k=5):

    query_embedding = embedding_model.encode(
        [question],
        normalize_embeddings=True
    )

    query_embedding = np.asarray(
        query_embedding,
        dtype=np.float32
    )

    scores, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for score, idx in zip(scores[0], indices[0]):

        if idx < 0:
            continue

        row = chunks_df.iloc[int(idx)]

        results.append({
            "chunk_id": int(row["chunk_id"]),
            "case_id": str(row["case_id"]),
            "page": int(row["page"]),
            "text": str(row["text"]),
            "score": float(score)
        })

    return results


# ============================================================
# GRAPH EXPANSION
# ============================================================

def get_case_relationships(case_id):

    query = """
    MATCH (source:Case {case_id: $case_id})
          -[r]->
          (target:Case)

    RETURN
        source.case_id AS source_case_id,
        type(r) AS relationship,
        target.case_id AS target_case_id,
        target.title AS target_title,
        target.citation AS target_citation

    ORDER BY target.case_id
    """

    with driver.session() as session:

        records = session.run(
            query,
            case_id=case_id
        )

        return [record.data() for record in records]


# ============================================================
# MULTI-CASE RETRIEVAL
# ============================================================

def retrieve(question, top_k=5):

    print("\n===================================")
    print("VECTOR SEARCH")
    print("===================================")

    vector_results = vector_search(
        question,
        top_k=top_k
    )

    for item in vector_results:

        print(
            f"\nChunk {item['chunk_id']} "
            f"| Case: {item['case_id']} "
            f"| Page: {item['page']}"
        )

        print(
            f"Score: {item['score']:.4f}"
        )

        print(
            item["text"][:1000]
        )

    # --------------------------------------------------------
    # IDENTIFY UNIQUE CASES
    # --------------------------------------------------------

    case_ids = []

    for item in vector_results:

        case_id = item["case_id"]

        if case_id not in case_ids:

            case_ids.append(case_id)

    print("\n===================================")
    print("RELEVANT CASES")
    print("===================================")

    for case_id in case_ids:

        print(
            f"Case: {case_id}"
        )

    # --------------------------------------------------------
    # GRAPH EXPANSION FOR EACH CASE
    # --------------------------------------------------------

    print("\n===================================")
    print("GRAPH EXPANSION")
    print("===================================")

    graph_results = []

    for case_id in case_ids:

        print(
            f"\nExpanding case: {case_id}"
        )

        relationships = get_case_relationships(
            case_id
        )

        if not relationships:

            print(
                "No relationships found."
            )

        for relationship in relationships:

            graph_results.append(
                relationship
            )

            print(
                f"{relationship['relationship']} "
                f"→ {relationship['target_case_id']}"
            )

    # --------------------------------------------------------
    # REMOVE DUPLICATE GRAPH RELATIONSHIPS
    # --------------------------------------------------------

    unique_graph_results = []

    seen_relationships = set()

    for item in graph_results:

        key = (
            item["source_case_id"],
            item["relationship"],
            item["target_case_id"]
        )

        if key not in seen_relationships:

            seen_relationships.add(key)

            unique_graph_results.append(
                item
            )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print("\n===================================")
    print("RETRIEVAL SUMMARY")
    print("===================================")

    print(
        f"Vector results: {len(vector_results)}"
    )

    print(
        f"Unique cases: {len(case_ids)}"
    )

    print(
        f"Graph relationships: {len(unique_graph_results)}"
    )

    return {
        "vector_results": vector_results,
        "case_ids": case_ids,
        "graph_results": unique_graph_results
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n===================================")
    print("LEGAL GRAPH-RAG RETRIEVER")
    print("===================================")

    question = input(
        "\nEnter your legal question:\n> "
    ).strip()

    if not question:

        print(
            "No question entered."
        )

        return

    retrieve(
        question,
        top_k=5
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()