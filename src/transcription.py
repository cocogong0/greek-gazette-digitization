# src/transcription.py

"""
Transcribes and translates PNG images containing the tables of contents from the
Greek Government Gazette (FEK) using the Gemini API.

"""

from config import (
    GEMINI_API_KEY,
    GEMINI_PRIMARY_MODEL,
    GEMINI_RETRY_MODEL,
    TRANSCRIPTION_PROMPT,
    API_REQUEST_TIMEOUT,
    API_COOLDOWN,
)

import base64
import json
import time
from pathlib import Path

import requests


def _encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _gemini_request(image_b64, model_name):

    # enforcing both languages
    # this forces the model to commit to a transcription before translating
    json_schema = {
        "type": "object",
        "properties": {
            "greek_transcription": {"type": "string"},
            "english_translation": {"type": "string"},
        },
        "required": ["greek_transcription", "english_translation"],
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": TRANSCRIPTION_PROMPT},
                    {"inline_data": {"mime_type": "image/png", "data": image_b64}},
                ]
            }
        ],
        "generationConfig": {
            "response_mime_type": "application/json",
            "response_schema": json_schema,
        },
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}

    try:
        r = requests.post(
            url, headers=headers, json=payload, timeout=API_REQUEST_TIMEOUT
        )
        r.raise_for_status()
        data = r.json()

        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        if not parts:
            raise ValueError("No parts in response")

        text = (parts[0].get("text") or "").strip()
        parsed = json.loads(text)
        if not (
            isinstance(parsed, dict)
            and "greek_transcription" in parsed
            and "english_translation" in parsed
        ):
            raise ValueError("Missing expected keys in JSON")

        return {"ok": parsed}
    except Exception as e:
        return {"error": str(e)}


def _transcribe_image(image_path, model_name):
    try:
        b64 = _encode_image(image_path)
        return _gemini_request(b64, model_name)
    except Exception as e:
        return {"error": str(e)}


def _images_to_transcribe(image_dir, out_dir):
    images = sorted(p for p in image_dir.glob("*.png"))
    todo = []
    for image in images:
        json_path = out_dir / (image.stem + ".json")
        if not json_path.exists():
            todo.append(image)
            continue
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                obj = json.load(f)
            if isinstance(obj, dict) and ("error" in obj):
                todo.append(image)
        except Exception:
            todo.append(image)
    return todo


def process_transcriptions_for_year(year, image_dir_pattern, transcription_dir_pattern):
    img_dir = Path(image_dir_pattern.format(year=year))
    out_dir = Path(transcription_dir_pattern.format(year=year))

    if not img_dir.exists():
        print(f"No images for {year}: {img_dir}")
        return
    out_dir.mkdir(parents=True, exist_ok=True)

    # first pass through files
    files = _images_to_transcribe(img_dir, out_dir)
    print(f"First pass with {GEMINI_PRIMARY_MODEL}: {len(files)} images")
    for i, img in enumerate(files, 1):
        print(f"Transcribing {i}/{len(files)} images: {img.name}")

        result = _transcribe_image(img, GEMINI_PRIMARY_MODEL)
        out_path = out_dir / (img.stem + ".json")

        with open(out_path, "w", encoding="utf-8") as f:
            if "error" in result:
                data_to_write = result
            else:
                data_to_write = result.get("ok", {})

            json.dump(data_to_write, f, ensure_ascii=False, indent=2)

        time.sleep(API_COOLDOWN)

    # second pass through any failed files
    retry = _images_to_transcribe(img_dir, out_dir)
    print(f"Retry pass with {GEMINI_RETRY_MODEL}: {len(retry)} images")
    for i, img in enumerate(retry, 1):
        print(f"Retrying {i}/{len(retry)} images: {img.name}")

        result = _transcribe_image(img, GEMINI_RETRY_MODEL)
        out_path = out_dir / (img.stem + ".json")

        with open(out_path, "w", encoding="utf-8") as f:
            if "error" in result:
                data_to_write = result
            else:
                data_to_write = result.get("ok", {})

            json.dump(data_to_write, f, ensure_ascii=False, indent=2)

        time.sleep(API_COOLDOWN)

    print(f"Finished transcribing year {year}")
