import os
import json
import re
from pathlib import Path

import pandas as pd
import requests

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

METADATA_DIR = PROJECT_ROOT / "data" / "metadata"
PDF_DIR = PROJECT_ROOT / "data" / "precedents" / "pdf"
TEXT_DIR = PROJECT_ROOT / "data" / "precedents" / "text"
MANIFEST_FILE = PROJECT_ROOT / "data" / "precedents" / "precedents.json"

# These are the six precedents connected to the main case:
# 2025 INSC 24.
PRECEDENTS = [
    "1961 INSC 197",
    "1988 INSC 204",
    "1993 INSC 221",
    "1994 INSC 573",
    "1995 INSC 114",
    "2000 INSC 497",
]

S3_BASE = "https://indian-supreme-court-judgments.s3.amazonaws.com/"

REQUEST_TIMEOUT = 60


# ============================================================
# HELPERS
# ============================================================

def safe_filename(case_id):
    return case_id.replace(" ", "_")


def load_metadata():
    """
    Load the locally downloaded Supreme Court metadata parquet files.

    The project previously used yearly metadata parquet files to resolve
    neutral citations such as '1961 INSC 197' to the exact PDF path.
    """
    if not METADATA_DIR.exists():
        raise FileNotFoundError(
            f"Metadata directory not found: {METADATA_DIR}\n"
            "The project needs the yearly metadata parquet files to "
            "resolve the precedent PDF paths."
        )

    files = sorted(METADATA_DIR.rglob("*.parquet"))

    if not files:
        raise FileNotFoundError(
            f"No metadata parquet files found under: {METADATA_DIR}"
        )

    frames = []

    for file in files:
        try:
            df = pd.read_parquet(file)

            if "case_id" not in df.columns:
                continue

            matches = df[df["case_id"].astype(str).isin(PRECEDENTS)]

            if not matches.empty:
                frames.append(matches)

        except Exception as exc:
            print(f"Skipping metadata file {file.name}: {exc}")

    if not frames:
        raise RuntimeError(
            "None of the six precedent case IDs were found in the "
            "local metadata parquet files."
        )

    metadata = pd.concat(frames, ignore_index=True)

    # Keep one row per case ID.
    metadata = metadata.drop_duplicates(subset=["case_id"])

    return metadata


def get_metadata_row(metadata, case_id):
    matches = metadata[
        metadata["case_id"].astype(str) == case_id
    ]

    if matches.empty:
        return None

    return matches.iloc[0]


def normalize_s3_path(path):
    """
    The metadata 'path' field is normally relative to the public bucket.
    """
    path = str(path).strip()

    if path.startswith("s3://"):
        path = path[len("s3://"):]

        # Remove bucket name if it is included.
        path = re.sub(
            r"^indian-supreme-court-judgments/",
            "",
            path,
            flags=re.IGNORECASE,
        )

    path = path.lstrip("/")

    return path


def build_pdf_url(metadata_row):
    path = metadata_row.get("path")

    if path is None or str(path).strip() in {"", "nan", "None"}:
        raise ValueError(
            f"No PDF path available in metadata for "
            f"{metadata_row['case_id']}"
        )

    relative_path = normalize_s3_path(path)

    # Metadata paths may occasionally point at a non-PDF object.
    # The judgment PDF is stored under data/pdf/.
    if not relative_path.lower().endswith(".pdf"):
        raise ValueError(
            f"Metadata path is not a PDF for {metadata_row['case_id']}: "
            f"{relative_path}"
        )

    return S3_BASE + relative_path


def download_file(url, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)

    print(f"Downloading:")
    print(f"  {url}")

    response = requests.get(
        url,
        timeout=REQUEST_TIMEOUT,
        stream=True,
    )

    response.raise_for_status()

    with open(destination, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                file.write(chunk)


def extract_pdf_text(pdf_path, text_path):
    if PdfReader is None:
        raise ImportError(
            "pypdf is not installed. Install it with:\n"
            "pip install pypdf"
        )

    print(f"Extracting text: {pdf_path.name}")

    reader = PdfReader(str(pdf_path))

    pages = []

    for page in reader.pages:
        try:
            page_text = page.extract_text() or ""
        except Exception as exc:
            print(f"  Warning: could not extract one page: {exc}")
            page_text = ""

        pages.append(page_text)

    text = "\n\n".join(pages).strip()

    if not text:
        raise RuntimeError(
            f"No text could be extracted from {pdf_path}"
        )

    text_path.parent.mkdir(parents=True, exist_ok=True)
    text_path.write_text(
        text,
        encoding="utf-8",
    )

    return text


# ============================================================
# MAIN SETUP
# ============================================================

def main():
    print("===================================")
    print("PRECEDENT SETUP")
    print("===================================")
    print("Main case: 2025 INSC 24")
    print(f"Precedents to prepare: {len(PRECEDENTS)}")

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)

    print("\nLoading local metadata...")
    metadata = load_metadata()

    print(
        f"Metadata rows found for precedents: "
        f"{len(metadata)}"
    )

    manifest = {}

    for case_id in PRECEDENTS:
        print("\n-----------------------------------")
        print(f"PRECEDENT: {case_id}")
        print("-----------------------------------")

        row = get_metadata_row(metadata, case_id)

        if row is None:
            print(f"ERROR: metadata not found for {case_id}")
            continue

        pdf_path = PDF_DIR / f"{safe_filename(case_id)}.pdf"
        text_path = TEXT_DIR / f"{safe_filename(case_id)}.txt"

        try:
            pdf_url = build_pdf_url(row)

            # Reuse an existing PDF if it is already present.
            if pdf_path.exists() and pdf_path.stat().st_size > 0:
                print(f"PDF already exists: {pdf_path.name}")
            else:
                download_file(pdf_url, pdf_path)

            # Reuse existing text when available.
            if text_path.exists() and text_path.stat().st_size > 0:
                text = text_path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
                print(f"Text already exists: {text_path.name}")
            else:
                text = extract_pdf_text(pdf_path, text_path)

            manifest[case_id] = {
                "case_id": case_id,
                "title": str(row.get("title", "")),
                "petitioner": str(row.get("petitioner", "")),
                "respondent": str(row.get("respondent", "")),
                "citation": str(row.get("citation", "")),
                "decision_date": str(row.get("decision_date", "")),
                "pdf_url": pdf_url,
                "pdf_file": str(pdf_path.relative_to(PROJECT_ROOT)),
                "text_file": str(text_path.relative_to(PROJECT_ROOT)),
                "text_length": len(text),
            }

            print(f"SUCCESS: {case_id}")

        except Exception as exc:
            print(f"FAILED: {case_id}")
            print(f"Reason: {exc}")

    # Save the manifest even if one item failed, so successful downloads
    # remain recorded.
    with open(
        MANIFEST_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            manifest,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print("\n===================================")
    print("PRECEDENT SETUP COMPLETE")
    print("===================================")
    print(f"Successfully prepared: {len(manifest)}/{len(PRECEDENTS)}")
    print(f"PDF directory:  {PDF_DIR}")
    print(f"Text directory: {TEXT_DIR}")
    print(f"Manifest:       {MANIFEST_FILE}")

    if len(manifest) != len(PRECEDENTS):
        print(
            "\nWARNING: One or more precedents could not be prepared."
        )
        print(
            "Review the errors above before relying on a fresh rebuild."
        )
    else:
        print("\nAll six precedents are ready.")


if __name__ == "__main__":
    main()
