import os
import pandas as pd
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase


# ==========================================
# CONFIGURATION
# ==========================================

FAISS_INDEX = "data/judgments/chunks.index"
CHUNKS_FILE = "data/judgments/chunks_with_embeddings.csv"

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Suman@9699"

MODEL_NAME = "all-MiniLM-L6-v2"


# ==========================================
# LOAD VECTOR DATABASE
# ==========================================

print("Loading chunks...")

chunks = pd.read_csv(CHUNKS_FILE)

print(f"Chunks loaded: {len(chunks)}")


print("\nLoading FAISS index...")

index = faiss.read_index(FAISS_INDEX)

print(f"FAISS vectors: {index.ntotal}")
print(f"Vector dimension: {index.d}")


# ==========================================
# LOAD EMBEDDING MODEL
# ==========================================

print("\nLoading embedding model...")

model = SentenceTransformer(MODEL_NAME)

print("Embedding model loaded.")


# ==========================================
# CONNECT TO NEO4J
# ==========================================

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)

driver.verify_connectivity()

print("Connected to Neo4j successfully.")


# ==========================================
# VECTOR SEARCH
# ==========================================

def vector_search(question, top_k=5):

    print("\n===================================")
    print("VECTOR SEARCH")
    print("===================================")

    query_embedding = model.encode(
        [question],
        normalize_embeddings=True
    )

    query_embedding = np.asarray(
        query_embedding,
        dtype="float32"
    )

    scores, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for score, idx in zip(scores[0], indices[0]):

        if idx == -1:
            continue

        row = chunks.iloc[idx]

        results.append({
            "score": float(score),
            "chunk_id": int(row["chunk_id"]),
            "case_id": row["case_id"],
            "page": int(row["page"]),
            "text": row["text"]
        })

    return results


# ==========================================
# GRAPH SEARCH
# ==========================================

def graph_search(case_id):

    print("\n===================================")
    print("GRAPH SEARCH")
    print("===================================")

    query = """
    MATCH (source:Case {case_id: $case_id})
          -[r]->(target:Case)

    RETURN
        source.case_id AS source_case_id,
        source.title AS source_title,
        type(r) AS relationship,
        target.case_id AS target_case_id,
        target.title AS target_title,
        target.citation AS target_citation
    """

    with driver.session() as session:

        result = session.run(
            query,
            case_id=case_id
        )

        relationships = []

        for record in result:

            relationships.append({
                "source_case_id": record["source_case_id"],
                "source_title": record["source_title"],
                "relationship": record["relationship"],
                "target_case_id": record["target_case_id"],
                "target_title": record["target_title"],
                "target_citation": record["target_citation"]
            })

    return relationships


# ==========================================
# HYBRID RETRIEVAL
# ==========================================

def hybrid_search(question, top_k=5):

    print("\n\n===================================")
    print("HYBRID LEGAL RETRIEVAL")
    print("===================================")

    print(f"\nQuestion:")
    print(question)

    # --------------------------------------
    # STEP 1: VECTOR SEARCH
    # --------------------------------------

    vector_results = vector_search(
        question,
        top_k
    )

    print(
        f"\nRetrieved {len(vector_results)} "
        f"relevant chunks."
    )

    # --------------------------------------
    # STEP 2: GRAPH SEARCH
    # --------------------------------------

    case_ids = set()

    for result in vector_results:

        case_ids.add(
            result["case_id"]
        )

    graph_results = []

    for case_id in case_ids:

        relationships = graph_search(
            case_id
        )

        graph_results.extend(
            relationships
        )

    # --------------------------------------
    # DISPLAY VECTOR RESULTS
    # --------------------------------------

    print("\n\n===================================")
    print("RELEVANT DOCUMENT CHUNKS")
    print("===================================")

    for i, result in enumerate(
        vector_results,
        start=1
    ):

        print(f"\n--- RESULT {i} ---")

        print(
            f"Score: {result['score']:.4f}"
        )

        print(
            f"Case ID: {result['case_id']}"
        )

        print(
            f"Page: {result['page']}"
        )

        print(
            f"Chunk ID: {result['chunk_id']}"
        )

        print("\nText:")

        print(
            result["text"][:1500]
        )

    # --------------------------------------
    # DISPLAY GRAPH RESULTS
    # --------------------------------------

    print("\n\n===================================")
    print("GRAPH RELATIONSHIPS")
    print("===================================")

    if not graph_results:

        print("No graph relationships found.")

    else:

        for relationship in graph_results:

            print(
                f"\n{relationship['source_case_id']}"
            )

            print(
                f"  --[{relationship['relationship']}]-->"
            )

            print(
                f"  {relationship['target_case_id']}"
            )

            print(
                f"  {relationship['target_title']}"
            )

    # --------------------------------------
    # BUILD COMBINED CONTEXT
    # --------------------------------------

    context = []

    context.append(
        "RELEVANT LEGAL DOCUMENTS:\n"
    )

    for result in vector_results:

        context.append(
            f"""
Case ID: {result['case_id']}
Page: {result['page']}
Similarity Score: {result['score']:.4f}

{result['text']}
"""
        )

    context.append(
        "\nRELATED CASE LAW:\n"
    )

    for relationship in graph_results:

        context.append(
            f"""
Source Case: {relationship['source_case_id']}
Relationship: {relationship['relationship']}
Target Case: {relationship['target_case_id']}
Target Title: {relationship['target_title']}
Target Citation: {relationship['target_citation']}
"""
        )

    combined_context = "\n".join(
        context
    )

    return combined_context


# ==========================================
# MAIN
# ==========================================

def main():

    question = input(
        "\nEnter your legal question: "
    )

    context = hybrid_search(
        question,
        top_k=5
    )

    print("\n\n===================================")
    print("COMBINED GRAPH + VECTOR CONTEXT")
    print("===================================")

    print(context)

    driver.close()


if __name__ == "__main__":
    main()