# Greek Gazette Digitization

This repository is refactored from a project I worked on as a summer 2025 research assistant at the Princeton Macrofinance Lab.

## Import Liberalization and European Reconstruction

After World War II, many European countries restricted the imports of foreign goods. This meant that, in order to import goods, importers had to obtain a permit from the central bank, which were heavily rationed at the time. In the late 1940s, European countries began to liberalize their imports, such that permits were no longer required for importers. This was done by publishing lists of "liberalized goods" in the country's official periodical publication, where other legal and public notices are also published.

My work in this project involved the digitization of liberalized import lists in archival publications from Spain, France, Iceland, Italy, and Greece. This repository highlights the digitization of the Greek Government Gazette (FEK).

## Technical Details

This repository is an end-to-end automation of the following digitization pipeline. In total, it covered the years 1950-1970 (inclusive) for 20k+ total PDFs.

Digitization Pipeline
1. Download PDFs of the Greek Government Gazette (FEK) (Selenium, BeautifulSoup)
2. Convert the first page of each PDF to a PNG (PyMuPDF)
3. Transcribe and translate each image and save as JSON (Gemini: 1.5-Flash and 1.5 Pro)
4. Consolidate JSONs into searchable CSVs (Pandas)

## Project Status

This repository is still a work in progress.

To-Do:
1. Add sample data for demonstration.
2. Add pipeline documentation with more details.
3. Clean up comments in scripts.

## Notes and Requirements

1. ChromeDriver executable installed and available for Selenium (this project was developed on a Windows system, where `CHROMEDRIVER_PATH` in `config.py` points to the `chromedriver.exe` location).
2. `GEMINI_API_KEY` set as an environment variable.
3. Disclosure: I composed the code in this repository. AI tools were used to suggest style improvements and documentation edits.