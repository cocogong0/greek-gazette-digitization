# src/conversion.py

"""
Converts the first page of each Greek Government Gazette (FEK) PDF to a PNG.
This is where the table of contents is located.

"""

from pathlib import Path

import fitz  # PyMuPDF


def _pdf_to_png_first_page(pdf_path, png_path, dpi=200):
    if png_path.exists():
        return {"ok": str(png_path)}

    try:
        with fitz.open(pdf_path) as doc:
            if doc.page_count == 0:
                return {"error": f"Empty PDF: {pdf_path}"}

            # according to Dr. Degorce, the table of contents is always on first page
            page = doc.load_page(0)
            zoom = dpi / 72.0
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)

            png_path.parent.mkdir(parents=True, exist_ok=True)
            pix.save(png_path)

        return {"ok": str(png_path)}
    except Exception as e:
        return {"error": f"{e}"}


def convert_first_pages_for_year(year, pdf_dir_pattern, image_dir_pattern):
    pdf_dir = Path(pdf_dir_pattern.format(year=year))
    img_dir = Path(image_dir_pattern.format(year=year))
    img_dir.mkdir(parents=True, exist_ok=True)

    if not pdf_dir.exists():
        print(f"No PDF directory for {year}: {pdf_dir}")
        return

    pdfs = sorted(pdf_dir.glob("*.pdf"))
    print(f"Found {len(pdfs)} PDFs for year {year} to convert to PNGs")

    for i, pdf in enumerate(pdfs, 1):
        png = img_dir / f"{pdf.stem}.png"
        print(f"Converting {i}/{len(pdfs)} PDFs for year {year}: {png.name}")

        result = _pdf_to_png_first_page(pdf, png)
        if "error" in result:
            print(f"Failed {pdf.name}: {result['error']}")
        else:
            print(f"Saved {png.name}: {result['ok']}")

    print(f"Finished converting year {year}")
