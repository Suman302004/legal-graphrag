import pandas as pd
import os


# ============================================================
# CONFIGURATION
# ============================================================

RELATIONSHIPS_PATH = (
    "data/resolved_relationships.csv"
)

METADATA_DIR = "data/metadata"

OUTPUT_PATH = "data/cases.csv"


# ============================================================
# LOAD RELATIONSHIPS
# ============================================================

print("Loading resolved relationships...")

relationships = pd.read_csv(
    RELATIONSHIPS_PATH
)


# ============================================================
# Collect all case IDs
# ============================================================

case_ids = set()

# Source cases
for case_id in relationships[
    "source_case_id"
].dropna():

    case_ids.add(
        str(case_id)
    )


# Target cases
for case_id in relationships[
    "target_case_id"
].dropna():

    case_ids.add(
        str(case_id)
    )


print(
    f"Unique cases found: "
    f"{len(case_ids)}"
)


# ============================================================
# Load metadata
# ============================================================

metadata_frames = []


files = [
    f
    for f in os.listdir(
        METADATA_DIR
    )
    if f.startswith("metadata_")
    and f.endswith(".parquet")
]


for file in files:

    path = os.path.join(
        METADATA_DIR,
        file
    )

    print(
        f"Loading {file}"
    )

    df = pd.read_parquet(
        path
    )

    metadata_frames.append(
        df
    )


# ============================================================
# Combine metadata
# ============================================================

metadata = pd.concat(
    metadata_frames,
    ignore_index=True
)


# ============================================================
# Select required columns
# ============================================================

columns = [

    "case_id",
    "title",
    "citation",
    "judge",
    "author_judge",
    "decision_date",
    "court",
    "path"

]


metadata = metadata[
    [
        c
        for c in columns
        if c in metadata.columns
    ]
]


# ============================================================
# Filter required cases
# ============================================================

cases = metadata[
    metadata["case_id"]
    .astype(str)
    .isin(case_ids)
].copy()


# ============================================================
# Remove duplicates
# ============================================================

cases = cases.drop_duplicates(
    subset=["case_id"]
)


# ============================================================
# Save
# ============================================================

cases.to_csv(
    OUTPUT_PATH,
    index=False
)


# ============================================================
# Display
# ============================================================

print("\n==========================================")

print(
    "CASE NODE DATASET CREATED"
)

print("==========================================")

print(
    f"Cases: {len(cases)}"
)

print(
    f"Saved to: {OUTPUT_PATH}"
)


print("\n--- CASE NODES ---")

print(
    cases.to_string(
        index=False
    )
)