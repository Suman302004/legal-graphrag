import pandas as pd
import re

df = pd.read_parquet(
    "data/metadata/metadata_1995.parquet"
)

row = df[
    df["case_id"] == "1995 INSC 114"
].iloc[0]

html = str(row["raw_html"])

print()
print("===================================")
print("PDF SOURCE INSPECTION")
print("===================================")

print()
print("Case:", row["case_id"])
print("Path:", row["path"])

print()
print("Looking for JavaScript files...")

scripts = re.findall(
    r'<script[^>]+src=["\']([^"\']+)',
    html,
    flags=re.IGNORECASE
)

if scripts:

    for script in scripts:
        print(script)

else:

    print("No script files found inside this stored HTML.")

print()
print("Looking for PDF-related functions...")

for function in [
    "open_pdf",
    "get_pdf_lang",
    "pdf"
]:

    print()
    print("----", function, "----")

    matches = [
        line.strip()
        for line in html.splitlines()
        if function.lower() in line.lower()
    ]

    for line in matches:
        print(line)

print()
print("===================================")
print("DONE")
print("===================================")