# src/main.py

"""
Digitization pipeline:
1. download PDFs
2. convert first page to PNG
3. transcribe PNGs to JSON
4. consolidate JSONs to CSV

"""

from config import (
    YEARS_TO_PROCESS,
    PDF_DIR_PATTERN,
    IMAGE_DIR_PATTERN,
    TRANSCRIPTION_DIR_PATTERN,
    CSV_OUTPUT_DIR,
)

from download import process_downloads_for_year
from conversion import convert_first_pages_for_year
from transcription import process_transcriptions_for_year
from consolidate import consolidate_json_to_csv


def main():
    for year in YEARS_TO_PROCESS:
        print(f"Digitizing year {year}")

        try:
            process_downloads_for_year(year, PDF_DIR_PATTERN)
        except Exception as e:
            print(f"Download failed for {year}: {e}")

        try:
            convert_first_pages_for_year(year, PDF_DIR_PATTERN, IMAGE_DIR_PATTERN)
        except Exception as e:
            print(f"Conversion failed for {year}: {e}")

        try:
            process_transcriptions_for_year(
                year, IMAGE_DIR_PATTERN, TRANSCRIPTION_DIR_PATTERN
            )
        except Exception as e:
            print(f"Transcription failed for {year}: {e}")

        try:
            consolidate_json_to_csv(year, TRANSCRIPTION_DIR_PATTERN, CSV_OUTPUT_DIR)
        except Exception as e:
            print(f"Consolidation failed for {year}: {e}")

    print("Digitization complete.")


if __name__ == "__main__":
    main()
