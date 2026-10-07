import fitz
from pathlib import Path


PDF_PATH = Path("data/judgments/2025_1_81_92_EN.pdf")
OUTPUT_PATH = Path("data/judgments/2025_1_81_92_EN.txt")


def extract_text():
    print("Reading PDF...")

    doc = fitz.open(PDF_PATH)

    print(f"Pages: {len(doc)}")

    pages = []

    for page_number, page in enumerate(doc, start=1):
        text = page.get_text()

        pages.append(
            f"\n\n--- PAGE {page_number} ---\n\n{text}"
        )

    full_text = "".join(pages)

    OUTPUT_PATH.write_text(
        full_text,
        encoding="utf-8"
    )

    print(f"Characters: {len(full_text)}")
    print(f"Saved to: {OUTPUT_PATH}")

    print("\n--- PREVIEW ---")
    print(full_text[:3000])


if __name__ == "__main__":
    extract_text()