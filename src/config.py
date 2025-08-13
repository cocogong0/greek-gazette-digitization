# src/config.py

import os

# project settings
YEARS_TO_PROCESS = range(1950, 1971)
BASE_SEARCH_URL = "https://search.et.gr/en/simple-search/"
CHROMEDRIVER_PATH = "~/chromedriver-win64/chromedriver-win64/chromedriver.exe"

# directory patterns
PDF_DIR_PATTERN = "data/{year}_FEK_Downloads"
IMAGE_DIR_PATTERN = "data/{year}_FEK_Page_Images"
TRANSCRIPTION_DIR_PATTERN = "data/{year}_FEK_Transcriptions"
CSV_OUTPUT_DIR = "data/Consolidated_CSVs"

# Gemini API configurations
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_PRIMARY_MODEL = "gemini-1.5-flash-latest"
GEMINI_RETRY_MODEL = "gemini-1.5-pro-latest"

TRANSCRIPTION_PROMPT = (
    "You are an expert OCR and translation assistant specializing in historical Greek Government Gazettes.\n"
    "Your task is to analyze the provided image of a table of contents page.\n\n"
    "Instructions:\n"
    "1. Transcribe the Greek text verbatim. Preserve all original text, including headings like 'ΠΕΡΙΕΧΟΜΕΝΑ' and section titles.\n"
    "2. Extract Page Numbers: For each entry in the table of contents, identify the page number at the end of the line.\n"
    "3. Ignore Dot Leaders: Do not transcribe the series of dots that connect the text to the page number. Replace them with a single space.\n"
    "4. Translate to English: Provide a clear English translation of the transcribed text.\n"
    "5. Format as JSON: Your final output must be a single, valid JSON object with two keys: 'greek_transcription' and 'english_translation'. Do not include any other text, notes, or markdown. Do not use escape characters unless it is for a newline (\\n).\n\n"
    "If the page does not contain a discernible table of contents, return a JSON object with empty strings for both values."
)

# timing configs
API_REQUEST_TIMEOUT = 180
API_COOLDOWN = 2
