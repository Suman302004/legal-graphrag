import os
import requests

# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://indian-supreme-court-judgments.s3.amazonaws.com"

OUTPUT_DIR = "data/judgments"

PRECEDENTS = {
    "1961 INSC 197": {
        "year": "1962",
        "path": "1962_2_551_558"
    },
    "1988 INSC 204": {
        "year": "1988",
        "path": "S_1988_2_231_237"
    },
    "1993 INSC 221": {
        "year": "1993",
        "path": "1993_3_1028_1035"
    },
    "1994 INSC 573": {
        "year": "1994",
        "path": "S_1994_6_266_276"
    },
    "1995 INSC 114": {
        "year": "1995",
        "path": "1995_2_65_70"
    },
    "2000 INSC 497": {
        "year": "2000",
        "path": "S_2000_4_307_312"
    }
}


# ============================================================
# DOWNLOAD
# ============================================================

def download_case(case_id, year, path):

    filename = f"{path}_EN.pdf"
    output_path = os.path.join(OUTPUT_DIR, filename)

    # Don't download again if already present
    if os.path.exists(output_path):
        print(f"Already exists: {filename}")
        return True

    url = (
        f"{BASE_URL}/data/pdf/"
        f"year={year}/english/{path}.pdf"
    )

    print()
    print("Downloading:", case_id)
    print("URL:", url)

    try:

        response = requests.get(
            url,
            timeout=60
        )

        if response.status_code != 200:

            print(
                f"FAILED - HTTP {response.status_code}"
            )

            return False

        with open(output_path, "wb") as f:
            f.write(response.content)

        print(
            f"SUCCESS - {filename} "
            f"({len(response.content):,} bytes)"
        )

        return True

    except Exception as e:

        print("FAILED:", e)

        return False


# ============================================================
# MAIN
# ============================================================

def main():

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    print()
    print("===================================")
    print("DOWNLOADING PRECEDENT JUDGMENTS")
    print("===================================")

    success = 0

    for case_id, info in PRECEDENTS.items():

        if download_case(
            case_id,
            info["year"],
            info["path"]
        ):
            success += 1

    print()
    print("===================================")
    print("DOWNLOAD COMPLETE")
    print("===================================")

    print(
        f"Downloaded: {success}/{len(PRECEDENTS)}"
    )

    print()
    print("Files are in:")
    print(OUTPUT_DIR)


if __name__ == "__main__":
    main()