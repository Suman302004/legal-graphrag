import pandas as pd
from bs4 import BeautifulSoup
import os

CASE_ID = "1995 INSC 114"

df = pd.read_parquet(
    "data/metadata/metadata_1995.parquet"
)

row = df[
    df["case_id"] == CASE_ID
].iloc[0]

html = str(row["raw_html"])

# Convert HTML to readable text
soup = BeautifulSoup(html, "html.parser")

text = soup.get_text(
    separator=" ",
    strip=True
)

print()
print("===================================")
print("PRECEDENT TEXT INSPECTION")
print("===================================")

print("Case:", row["case_id"])
print("Title:", row["title"])
print("Citation:", row["citation"])
print("Path:", row["path"])

print()
print("HTML characters:", len(html))
print("Extracted text characters:", len(text))

print()
print("FIRST 3000 CHARACTERS")
print("-----------------------------------")
print(text[:3000])

# Save it so we can inspect/use it later
os.makedirs("data/precedents", exist_ok=True)

output = "data/precedents/1995_INSC_114.txt"

with open(
    output,
    "w",
    encoding="utf-8"
) as f:
    f.write(text)

print()
print("Saved to:", output)

print()
print("===================================")
print("DONE")
print("===================================")