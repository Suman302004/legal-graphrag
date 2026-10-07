from pathlib import Path

import faiss
import pandas as pd

from sentence_transformers import SentenceTransformer


CHUNKS_PATH = Path(
    "data/judgments/chunks.csv"
)

INDEX_PATH = Path(
    "data/judgments/chunks.index"
)

MODEL_NAME = "all-MiniLM-L6-v2"


def main():

    print("Loading chunks...")

    df = pd.read_csv(CHUNKS_PATH)

    print(f"Chunks loaded: {len(df)}")

    print("\nLoading FAISS index...")

    index = faiss.read_index(
        str(INDEX_PATH)
    )

    print(
        f"FAISS vectors: {index.ntotal}"
    )

    print("\nLoading embedding model...")

    model = SentenceTransformer(
        MODEL_NAME
    )

    print("Model loaded.")

    print("\n===================================")
    print("LEGAL DOCUMENT RETRIEVER")
    print("===================================")

    while True:

        query = input(
            "\nEnter your legal question "
            "(or type 'exit'): "
        )

        if query.lower() == "exit":
            break

        print("\nSearching...")

        query_embedding = model.encode(
            [query],
            normalize_embeddings=True
        )

        scores, indices = index.search(
            query_embedding,
            5
        )

        print("\n===================================")
        print("TOP RELEVANT CHUNKS")
        print("===================================")

        for rank, (score, idx) in enumerate(
            zip(scores[0], indices[0]),
            start=1
        ):

            row = df.iloc[idx]

            print(
                f"\n--- RESULT {rank} ---"
            )

            print(
                f"Score: {score:.4f}"
            )

            print(
                f"Chunk ID: {row['chunk_id']}"
            )

            print(
                f"Page: {row['page']}"
            )

            print("\nText:")

            print(row["text"])

            print(
                "\n" + "-" * 70
            )


if __name__ == "__main__":
    main()