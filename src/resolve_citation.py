import os
import re
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_PATH = "data/case_relationships_raw.csv"

METADATA_DIR = "data/metadata"

OUTPUT_PATH = "data/resolved_relationships.csv"


# ============================================================
# METADATA CACHE
# ============================================================

metadata_cache = {}


# ============================================================
# NORMALIZE CITATION
# ============================================================

def normalize_citation(text):

    if pd.isna(text):
        return ""

    text = str(text).upper()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    text = text.replace(
        "S.C.R.",
        "SCR"
    )

    text = text.replace(
        "S.CC.",
        "SCC"
    )

    return text.strip()


# ============================================================
# LOAD METADATA
# ============================================================

def load_metadata(year):

    if year in metadata_cache:
        return metadata_cache[year]

    path = os.path.join(
        METADATA_DIR,
        f"metadata_{year}.parquet"
    )

    if not os.path.exists(path):

        print(
            f"Metadata not found: {year}"
        )

        return None

    print(
        f"Loading metadata: {year}"
    )

    df = pd.read_parquet(path)

    df["citation_normalized"] = (
        df["citation"]
        .apply(normalize_citation)
    )

    metadata_cache[year] = df

    return df


# ============================================================
# EXTRACT YEAR
# ============================================================

def extract_year(citation):

    match = re.search(
        r"\d{4}",
        citation
    )

    if match:

        return int(
            match.group()
        )

    return None


# ============================================================
# SEARCH METADATA
# ============================================================

def search_metadata(
    df,
    citation
):

    normalized = normalize_citation(
        citation
    )

    # Exact match
    matches = df[
        df["citation_normalized"]
        == normalized
    ]

    if len(matches) > 0:

        return (
            matches.iloc[0],
            "EXACT_CITATION"
        )

    # Partial match
    matches = df[
        df["citation_normalized"]
        .str.contains(
            re.escape(normalized),
            na=False
        )
    ]

    if len(matches) > 0:

        return (
            matches.iloc[0],
            "PARTIAL_CITATION"
        )

    return None, None


# ============================================================
# RESOLVE ONE CITATION
# ============================================================

def resolve_single_citation(
    citation
):

    citation_upper = citation.upper()

    # --------------------------------------------------------
    # SCR
    # --------------------------------------------------------

    if "SCR" in citation_upper:

        year = extract_year(
            citation
        )

        if year is None:

            return None

        df = load_metadata(
            year
        )

        if df is None:

            return None

        row, method = search_metadata(
            df,
            citation
        )

        if row is not None:

            return {

                "target_case_id":
                    row["case_id"],

                "target_title":
                    row["title"],

                "target_citation":
                    row["citation"],

                "resolution_method":
                    method

            }

        return None

    # --------------------------------------------------------
    # SCC
    # --------------------------------------------------------

    if "SCC" in citation_upper:

        # Search every locally available
        # metadata file.

        files = [
            f
            for f in os.listdir(
                METADATA_DIR
            )
            if f.startswith(
                "metadata_"
            )
            and f.endswith(
                ".parquet"
            )
        ]

        for file in files:

            match = re.search(
                r"metadata_(\d{4})\.parquet",
                file
            )

            if not match:

                continue

            year = int(
                match.group(1)
            )

            df = load_metadata(
                year
            )

            if df is None:

                continue

            row, method = search_metadata(
                df,
                citation
            )

            if row is not None:

                return {

                    "target_case_id":
                        row["case_id"],

                    "target_title":
                        row["title"],

                    "target_citation":
                        row["citation"],

                    "resolution_method":
                        method + "_SCC"

                }

        return None

    return None


# ============================================================
# LOAD RELATIONSHIPS
# ============================================================

print(
    "Loading extracted relationships..."
)

relationships = pd.read_csv(
    INPUT_PATH
)

print(
    f"Case relationships found: "
    f"{len(relationships)}"
)


# ============================================================
# RESOLVE CASES
# ============================================================

resolved_rows = []


for _, row in relationships.iterrows():

    source_case_id = (
        row["source_case_id"]
    )

    case_name = (
        row["case_name"]
    )

    relationship = (
        row["relationship"]
    )

    citations = [
        c.strip()
        for c in str(
            row["citations"]
        ).split("|")
        if c.strip()
    ]

    print("\n================================")

    print(
        f"CASE: {case_name}"
    )

    print(
        f"CITATIONS: {citations}"
    )

    print(
        f"RELATIONSHIP: {relationship}"
    )

    # --------------------------------------------------------
    # Try each citation
    # --------------------------------------------------------

    target = None

    successful_citation = None

    for citation in citations:

        print(
            f"Trying: {citation}"
        )

        result = resolve_single_citation(
            citation
        )

        if result:

            target = result

            successful_citation = (
                citation
            )

            print(
                "RESOLVED!"
            )

            break

    # --------------------------------------------------------
    # If one citation resolves,
    # the entire case resolves.
    # --------------------------------------------------------

    if target:

        print(
            f"TARGET: "
            f"{target['target_case_id']}"
        )

        print(
            f"Resolved using: "
            f"{successful_citation}"
        )

        resolved_rows.append({

            "source_case_id":
                source_case_id,

            "case_name":
                case_name,

            "citations":
                " | ".join(citations),

            "relationship":
                relationship,

            "target_case_id":
                target[
                    "target_case_id"
                ],

            "target_title":
                target[
                    "target_title"
                ],

            "target_citation":
                target[
                    "target_citation"
                ],

            "resolution_method":
                target[
                    "resolution_method"
                ],

            "resolved_using":
                successful_citation

        })

    else:

        print(
            "COULD NOT RESOLVE CASE"
        )

        resolved_rows.append({

            "source_case_id":
                source_case_id,

            "case_name":
                case_name,

            "citations":
                " | ".join(citations),

            "relationship":
                relationship,

            "target_case_id":
                None,

            "target_title":
                None,

            "target_citation":
                None,

            "resolution_method":
                "UNRESOLVED",

            "resolved_using":
                None

        })


# ============================================================
# SAVE RESULTS
# ============================================================

result_df = pd.DataFrame(
    resolved_rows
)

result_df.to_csv(
    OUTPUT_PATH,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

resolved_count = (
    result_df[
        "target_case_id"
    ].notna()
    .sum()
)

unresolved_count = (
    result_df[
        "target_case_id"
    ].isna()
    .sum()
)


print("\n==========================================")

print(
    "RESOLUTION COMPLETE"
)

print("==========================================")

print(
    f"Total cited cases: "
    f"{len(result_df)}"
)

print(
    f"Resolved cases: "
    f"{resolved_count}"
)

print(
    f"Unresolved cases: "
    f"{unresolved_count}"
)

print(
    f"\nSaved to: "
    f"{OUTPUT_PATH}"
)


print("\n--- FINAL CASE GRAPH EDGES ---")

print(
    result_df[
        [
            "source_case_id",
            "case_name",
            "relationship",
            "target_case_id",
            "target_title"
        ]
    ].to_string(
        index=False
    )
)