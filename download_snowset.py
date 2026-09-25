import gzip
import io
import os
import requests

URL = "http://www.cs.cornell.edu/~midhul/snowset/snowset-main.csv.gz"

OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "snowset_real.csv")

ROWS_TO_DOWNLOAD = 20000


def download_data():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Connecting to Snowset...")
    print(f"Downloading first {ROWS_TO_DOWNLOAD:,} real query records...")

    response = requests.get(URL, stream=True, timeout=120)
    response.raise_for_status()

    with gzip.GzipFile(fileobj=response.raw) as gz:
        text_stream = io.TextIOWrapper(
            gz,
            encoding="utf-8",
            errors="replace"
        )

        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8",
            newline=""
        ) as output:

            header = text_stream.readline()

            if not header:
                raise RuntimeError("Could not read Snowset header.")

            output.write(header)

            rows = 0

            for line in text_stream:
                output.write(line)
                rows += 1

                if rows % 5000 == 0:
                    print(f"Downloaded {rows:,} rows")

                if rows >= ROWS_TO_DOWNLOAD:
                    break

    print()
    print("DONE")
    print(f"Saved to {OUTPUT_FILE}")
    print(f"Rows downloaded: {rows:,}")


if __name__ == "__main__":
    download_data()