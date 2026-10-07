import pandas as pd
import glob
import os

TARGET_CASES = [
    "1961 INSC 197",
    "1988 INSC 204",
    "1993 INSC 221",
    "1994 INSC 573",
    "1995 INSC 114",
    "2000 INSC 497",
]

print()
print("===================================")
print("FINDING PRECEDENT CASES")
print("===================================")

found = {}

for file in glob.glob("data/metadata/*.parquet"):

    df = pd.read_parquet(file)

    for case_id in TARGET_CASES:

        if case_id in found:
            continue

        matches = df[df["case_id"].astype(str).str.strip() == case_id]

        if matches.empty:
            continue

        row = matches.iloc[0]

        found[case_id] = True

        print()
        print("FOUND:", case_id)
        print("Metadata:", os.path.basename(file))
        print("Title:", row["title"])
        print("Citation:", row["citation"])
        print("Path:", row["path"])
        print("Date:", row["decision_date"])
        print("-----------------------------------")


print()
print("===================================")
print("RESULT")
print("===================================")

print(f"Found {len(found)} of {len(TARGET_CASES)} cases.")

missing = [
    case_id
    for case_id in TARGET_CASES
    if case_id not in found
]

if missing:
    print()
    print("NOT FOUND:")
    for case_id in missing:
        print(" ", case_id)

print()
print("Done.")