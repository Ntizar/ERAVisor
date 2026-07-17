#!/usr/bin/env python3
"""Descarga masiva de PDFs ERA — solo download, sin LLM"""
import json, os, time, sys
from pathlib import Path
import requests

BASE = Path("/root/workspace/ERAVisor")
PDF_DIR = BASE / "pdfs"
IDX_DIR = BASE / "data"
DELAY = 1.5
RETRIES = 3

def descargar(url, destino):
    if destino.exists() and destino.stat().st_size > 2000:
        return True
    for i in range(RETRIES):
        try:
            h = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"}
            r = requests.get(url, headers=h, timeout=60, allow_redirects=True)
            if r.status_code == 200 and r.content[:5] == b"%PDF-":
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_bytes(r.content)
                return True
            elif r.status_code == 429:
                time.sleep(DELAY * (i+1) * 3)
        except:
            time.sleep(DELAY * (i+1))
    return False

def main():
    pais = sys.argv[1] if len(sys.argv) > 1 else "ES"
    idx_file = IDX_DIR / f"{pais.lower()}-investigations-index.json"
    if not idx_file.exists():
        print(f"Index not found: {idx_file}")
        return

    with open(idx_file) as f:
        data = json.load(f)
    reports = data["reports"]
    pdf_dir = PDF_DIR / pais
    pdf_dir.mkdir(parents=True, exist_ok=True)

    ok, fail = 0, 0
    for i, r in enumerate(reports):
        fname = f"{pais}_{r['year']}_{r['title']}"
        path = pdf_dir / fname
        sys.stdout.write(f"\r[{i+1}/{len(reports)}] {r['title'][:50]:50s}")
        sys.stdout.flush()
        if descargar(r["pdf_url"], path):
            ok += 1
        else:
            fail += 1
        time.sleep(DELAY)

    print(f"\n✅ Descargados: {ok}/{len(reports)} | Fallos: {fail}")

if __name__ == "__main__":
    main()