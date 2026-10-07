import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer


# ==============================
# CONFIGURATION
# ==============================

INDEX_PATH = "data/judgments/chunks.index"
CHUNKS_PATH = "data/judgments/chunks_with_embeddings.csv"

MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 5


# ==============================
# LOAD MODEL
# ==============================

print("Loading embedding model...")
model = SentenceTransformer(MODEL_NAME)


# ==============================
# LOAD FAISS INDEX
# ==============================

print("Loading FAISS index...")
index = faiss.read_index(INDEX_PATH)

print(f"FAISS vectors: {index.ntotal}")
print(f"Vector dimension: {index.d}")


# ==============================
# LOAD CHUNKS
# ==============================

print("Loading document chunks...")
chunks = pd.read_csv(CHUNKS_PATH)

print(f"Chunks loaded: {len(chunks)}")


# ==============================
# RETRIEVAL FUNCTION
# ==============================

def retrieve_chunks(question, top_k=TOP_K):

    # Convert question into embedding
    question_embedding = model.encode(
        [question],
        convert_to_numpy=True
    )

    # Search FAISS
    distances, indices = index.search(
        question_embedding,
        top_k
    )

    results = []

    for rank, (distance, idx) in enumerate(
        zip(distances[0], indices[0]),
        start=1
    ):

        if idx == -1:
            continue

        chunk = chunks.iloc[idx]

        results.append({
            "rank": rank,
            "distance": float(distance),
            "chunk_id": int(chunk["chunk_id"]),
            "case_id": chunk["case_id"],
            "page": int(chunk["page"]),
            "text": chunk["text"]
        })

    return results


# ==============================
# INTERACTIVE SEARCH
# ==============================

if __name__ == "__main__":

    print("\n===================================")
    print("LEGAL DOCUMENT RETRIEVER")
    print("===================================")

    while True:

        question = input(
            "\nEnter your legal question "
            "(or type 'exit'): "
        )

        if question.lower() == "exit":
            break

        results = retrieve_chunks(question)

        print("\n===================================")
        print("RETRIEVED LEGAL CONTEXT")
        print("===================================")

        for result in results:

            print(
                f"\n--- RESULT {result['rank']} ---"
            )

            print(
                f"Case ID : {result['case_id']}"
            )

            print(
                f"Page    : {result['page']}"
            )

            print(
                f"Chunk   : {result['chunk_id']}"
            )

            print(
                f"Distance: {result['distance']:.4f}"
            )

            print(
                f"\n{result['text']}"
            )

            print("-" * 70)