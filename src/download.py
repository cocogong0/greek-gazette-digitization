# src/download.py

"""
Scrape the Greek Government Gazette (FEK) search UI with Selenium, extract
direct PDF links, and downloads files.

Note: the Chrome driver is for a Windows operating system!

"""

from config import (
    CHROMEDRIVER_PATH,
    BASE_SEARCH_URL,
    API_REQUEST_TIMEOUT,
    API_COOLDOWN,
)

import re
import time
import urllib.parse
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def _driver(chromedriver_path):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--incognito")
    options.add_argument("--disable-extensions")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-logging")
    options.add_argument("user-agent=Mozilla/5.0")

    service = ChromeService(executable_path=Path(chromedriver_path).expanduser())

    return webdriver.Chrome(service=service, options=options)


def _filename_from_row(row):
    tds = row.find_all("td")

    # issue date, format as YYMMDD
    issue_date = ""
    if len(tds) > 1:
        date_str = tds[1].get_text(strip=True)
        try:
            issue_date = datetime.strptime(date_str, "%d-%m-%Y").strftime("%y%m%d")
        except Exception:
            pass

    # issue type (usually a Greek letter)
    if len(tds) > 3:
        issue_type = tds[3].get_text(strip=True)
    else:
        issue_type = ""

    # issue number
    issue_number = ""
    if tds:
        link = tds[0].find("a", class_="fek-link")
        if link:
            label = link.get("aria-label", "")
            match = re.search(r"(\d+)/\d{4}", label)
            if match:
                issue_number = match.group(1)

    if issue_date and issue_type and issue_number:
        return f"{issue_date}_FEK_{issue_type}_{issue_number}.pdf"

    return ""


def _collect_year(year, driver, base_url):
    pdfs = set()
    driver.get(f"{base_url}?selectYear={year}")
    page = 1

    while True:
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "listing-items"))
            )

            soup = BeautifulSoup(driver.page_source, "html.parser")
            table = soup.find("table", id="listing-items")

            if not table or not table.tbody:
                print(f"No table on page {page} for year {year}")
                break

            rows = table.tbody.find_all("tr")
            if not rows:
                print(f"No table rows on page {page} for year {year}")
                break

            for row in rows:
                a = row.find("a", href=re.compile(r"\.pdf$", re.IGNORECASE))
                if not a:
                    continue
                pdf_url = a.get("href", "")
                if not pdf_url:
                    continue

                # make URLs absolute
                if not pdf_url.startswith("http"):
                    parsed = urllib.parse.urlparse(driver.current_url)
                    pdf_url = urllib.parse.urljoin(
                        f"{parsed.scheme}://{parsed.netloc}", pdf_url
                    )

                fname = (
                    _filename_from_row(row)
                    or Path(urllib.parse.urlparse(pdf_url).path).name
                )

                pdfs.add((pdf_url, fname))

            # pagination
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "button.table-button[aria-label='Next']")
                    )
                )

                if "disabled" in (next_button.get_attribute("class") or ""):
                    break

                next_button.click()
                page += 1
                time.sleep(2)  # be polite
            except (NoSuchElementException, TimeoutException):
                break

        except Exception as e:
            print(f"Error on page {page} for year {year}: {e}")
            break

    return sorted(pdfs, key=lambda x: x[1])  # sort by date


def _download(pdf_url, dest_path):
    if dest_path.exists():
        return {"ok": str(dest_path)}

    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        with requests.get(
            pdf_url, stream=True, headers=headers, timeout=API_REQUEST_TIMEOUT
        ) as request:
            request.raise_for_status()
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            with dest_path.open("wb") as f:
                for chunk in request.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        return {"ok": str(dest_path)}
    except Exception as e:
        return {"error": f"{e}"}


def process_downloads_for_year(year, download_dir_pattern):
    out_dir = Path(download_dir_pattern.format(year=year))
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Downloading to {out_dir}")

    driver = None
    try:
        driver = _driver(CHROMEDRIVER_PATH)
        entries = _collect_year(year, driver, BASE_SEARCH_URL)
        print(f"Found {len(entries)} PDFs for year {year}")

        for i, (url, filename) in enumerate(entries, 1):
            dest = out_dir / filename
            print(f"Downloading {i}/{len(entries)} files for year {year}: {filename}")
            result = _download(url, dest)

            if "error" in result:
                print(f"Failed file {filename}: {result['error']}")
            else:
                print(f"Saved file {filename}: {result['ok']}")

            time.sleep(API_COOLDOWN)  # be polite
    finally:
        if driver:
            driver.quit()

    print(f"Finished downloading year {year}")
