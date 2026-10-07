from pathlib import Path

import pandas as pd
import numpy as np
import faiss

from sentence_transformers import SentenceTransformer


INPUT_PATH = Path(
    "data/judgments/chunks.csv"
)

INDEX_PATH = Path(
    "data/judgments/chunks.index"
)

OUTPUT_PATH = Path(
    "data/judgments/chunks_with_embeddings.csv"
)

MODEL_NAME = "all-MiniLM-L6-v2"


def main():

    print("Loading chunks...")

    df = pd.read_csv(INPUT_PATH)

    print(f"Chunks: {len(df)}")

    print("\nLoading embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    print("Model loaded.")

    texts = df["text"].fillna("").tolist()

    print("\nCreating embeddings...")

    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    print(
        f"Embedding shape: {embeddings.shape}"
    )

    dimension = embeddings.shape[1]

    print(
        f"Vector dimension: {dimension}"
    )

    print("\nBuilding FAISS index...")

    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    faiss.write_index(
        index,
        str(INDEX_PATH)
    )

    print(
        f"FAISS index saved to: {INDEX_PATH}"
    )

    # Save embeddings separately as well
    embedding_strings = [
        ",".join(map(str, vector))
        for vector in embeddings
    ]

    df["embedding"] = embedding_strings

    df.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8"
    )

    print(
        f"Chunks with embeddings saved to: {OUTPUT_PATH}"
    )

    print("\n===================================")
    print("EMBEDDING CREATION COMPLETE")
    print("===================================")


if __name__ == "__main__":
    main()