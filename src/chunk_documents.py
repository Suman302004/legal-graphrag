from pathlib import Path
import re
import pandas as pd


INPUT_PATH = Path(
    "data/judgments/2025_1_81_92_EN.txt"
)

OUTPUT_PATH = Path(
    "data/judgments/chunks.csv"
)

CASE_ID = "2025 INSC 24"


def clean_text(text):
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


def create_chunks():

    print("Reading extracted document...")

    text = INPUT_PATH.read_text(
        encoding="utf-8"
    )

    # Split using our page markers
    pages = re.split(
        r"--- PAGE \d+ ---",
        text
    )

    chunks = []

    chunk_id = 0

    for page_number, page_text in enumerate(
        pages[1:],
        start=1
    ):

        page_text = clean_text(page_text)

        if not page_text:
            continue

        # Break long pages into smaller chunks
        words = page_text.split()

        chunk_size = 300
        overlap = 50

        start = 0

        while start < len(words):

            end = min(
                start + chunk_size,
                len(words)
            )

            chunk_text = " ".join(
                words[start:end]
            )

            chunks.append({
                "chunk_id": chunk_id,
                "case_id": CASE_ID,
                "page": page_number,
                "text": chunk_text
            })

            chunk_id += 1

            if end == len(words):
                break

            start = end - overlap

    df = pd.DataFrame(chunks)

    df.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8"
    )

    print("\n===================================")
    print("DOCUMENT CHUNKING COMPLETE")
    print("===================================")

    print(f"Total chunks: {len(df)}")
    print(f"Saved to: {OUTPUT_PATH}")

    print("\n--- FIRST 3 CHUNKS ---")

    print(
        df[
            ["chunk_id", "case_id", "page", "text"]
        ].head(3).to_string(index=False)
    )


if __name__ == "__main__":
    create_chunks()