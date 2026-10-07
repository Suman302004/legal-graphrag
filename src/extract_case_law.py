import re
import pandas as pd
from pypdf import PdfReader


# ============================================================
# Configuration
# ============================================================

PDF_PATH = "data/judgments/2025_1_81_92_EN.pdf"

SOURCE_CASE_ID = "2025 INSC 24"

OUTPUT_PATH = "data/case_relationships_raw.csv"


# ============================================================
# 1. Extract PDF text
# ============================================================

print("Reading judgment...")

reader = PdfReader(PDF_PATH)

full_text = "\n".join(
    page.extract_text() or ""
    for page in reader.pages
)

print(f"Pages: {len(reader.pages)}")
print(f"Characters: {len(full_text):,}")


# ============================================================
# 2. Extract Case Law Cited section
# ============================================================

start_marker = "Case Law Cited"
end_marker = "List of Acts"

start = full_text.find(start_marker)
end = full_text.find(end_marker, start)

if start == -1:
    raise ValueError(
        "Could not find Case Law Cited section."
    )

if end == -1:
    raise ValueError(
        "Could not find List of Acts section."
    )

case_law_text = full_text[
    start + len(start_marker):end
].strip()


# ============================================================
# 3. Remove page headers
# ============================================================

case_law_text = re.sub(
    r'\[\d{4}\]\s*\d+\s*S\.C\.R\.\s*\d+',
    '',
    case_law_text,
    flags=re.IGNORECASE
)


# Remove repeated current case title

case_law_text = re.sub(
    r'Krishna Devi.*?Construction\s+v\.\s+Union of India\s*&\s*Ors\.',
    '',
    case_law_text,
    flags=re.IGNORECASE | re.DOTALL
)


# ============================================================
# 4. Normalize whitespace
# ============================================================

case_law_text = re.sub(
    r'\s+',
    ' ',
    case_law_text
).strip()


print("\n--- CLEANED CASE LAW SECTION ---")
print(case_law_text)


# ============================================================
# 5. Split individual cited cases
# ============================================================

case_law_text = re.sub(
    r'(\b(?:relied on|referred to|followed|'
    r'distinguished|overruled))\.\s+(?=[A-Z])',
    r'\1.; ',
    case_law_text,
    flags=re.IGNORECASE
)


entries = [
    entry.strip()
    for entry in case_law_text.split(";")
    if entry.strip()
]


# ============================================================
# 6. Citation extraction
# ============================================================

citation_patterns = [

    # SCR
    r'\[\d{4}\]\s*(?:SUPP\.?\s*)?\d+\s+S\.?C\.?R\.?\s+\d+',

    # SCC
    r'\(\d{4}\)\s*(?:SUPP\.?\s*)?\d+\s+SCC\s+\d+',

    # SCC without parentheses
    r'\d{4}\s+(?:SUPP\.?\s+)?\d+\s+SCC\s+\d+',

    # SCC Online
    r'\d{4}\s+SCC\s+OnLine\s+SC\s+\d+',

    # INSC
    r'\d{4}\s+INSC\s+\d+',
]


def extract_citations(text):

    citations = []

    for pattern in citation_patterns:

        matches = re.findall(
            pattern,
            text,
            re.IGNORECASE
        )

        citations.extend(matches)

    return list(dict.fromkeys(citations))


# ============================================================
# 7. Relationship detection
# ============================================================

def detect_relationship(text):

    text_lower = text.lower()

    if "relied on" in text_lower:
        return "RELIES_ON"

    if "referred to" in text_lower:
        return "REFERRED_TO"

    if "distinguished" in text_lower:
        return "DISTINGUISHES"

    if "overruled" in text_lower:
        return "OVERRULES"

    if "followed" in text_lower:
        return "FOLLOWS"

    return "CITES"


# ============================================================
# 8. Extract case name
# ============================================================

def extract_case_name(text, citations):

    cleaned = text

    # Remove relationship suffix
    cleaned = re.sub(
        r'\s+[–-]\s*(relied on|referred to|'
        r'followed|distinguished|overruled)\.?',
        '',
        cleaned,
        flags=re.IGNORECASE
    )

    # Remove all citations
    for citation in citations:
        cleaned = re.sub(
            re.escape(citation),
            '',
            cleaned,
            flags=re.IGNORECASE
        )

    # Normalize whitespace
    cleaned = re.sub(
        r'\s+',
        ' ',
        cleaned
    ).strip()

    # Remove a trailing colon left behind after citation removal
    cleaned = re.sub(
        r'\s*:\s*$',
        '',
        cleaned
    ).strip()

    return cleaned


# ============================================================
# 9. Build structured records
# ============================================================

records = []


for entry in entries:

    citations = extract_citations(entry)

    relationship = detect_relationship(entry)

    case_name = extract_case_name(
        entry,
        citations
    )

    records.append({

        "source_case_id": SOURCE_CASE_ID,

        "case_name": case_name,

        "citations": " | ".join(citations),

        "relationship": relationship,

        "raw_entry": entry

    })


# ============================================================
# 10. Create DataFrame
# ============================================================

result = pd.DataFrame(records)


# ============================================================
# 11. Save
# ============================================================

result.to_csv(
    OUTPUT_PATH,
    index=False
)


# ============================================================
# 12. Display
# ============================================================

print("\n--- STRUCTURED CASE RELATIONSHIPS ---")

print(
    result[
        [
            "source_case_id",
            "case_name",
            "citations",
            "relationship"
        ]
    ].to_string(index=False)
)


print(
    f"\nSaved to: {OUTPUT_PATH}"
)