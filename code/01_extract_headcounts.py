"""Extract the headline contractor headcount table from every census report.

Each quarterly report has a table "DoD Contractor Personnel in the USCENTCOM AOR"
with one row per area (e.g. Afghanistan, Iraq, other USCENTCOM locations, and the
USCENTCOM AOR total) and four columns: total contractors, U.S. citizens,
third-country nationals and local/host-country nationals.

The table is read twice, with two independent PDF text extractors:
  A. pdfplumber (Python)
  B. pdftotext (Poppler command-line tool)
Both readings are saved so that 02_check_headcounts.py can compare them.

Usage:  python code/01_extract_headcounts.py
Output: data/clean/headcounts_reading_a.csv, data/clean/headcounts_reading_b.csv
"""

import csv
import re
import subprocess
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "clean"

HEADER = re.compile(r"contractor personnel in the uscentcom aor", re.I)
NUMBER = re.compile(r"(?<![\w.])\d{1,3}(?:,\d{3})+(?![\w,])|(?<![\w.,])\d+(?![\w.,%])")
FILENAME = re.compile(r"FY(\d{2})_(\d)Q_5A[ _]([A-Za-z]{3})(\d{4})\.pdf$")


def area_from_label(label: str) -> str:
    """Map the report's row label to a standard area name."""
    low = label.lower()
    if "afghanistan" in low:
        return "Afghanistan"
    if "iraq" in low and "syria" in low:
        return "Iraq and Syria"
    if "iraq" in low:
        return "Iraq"
    if "other" in low:
        return "Other USCENTCOM locations"
    raise ValueError(f"Unknown row label: {label!r}")


def parse_table(text: str):
    """Return a list of rows: (area, label as printed, total, us, tcn, ln)."""
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if HEADER.search(line))
    labels, numbers, end = [], [], None
    for i in range(start + 1, min(start + 40, len(lines))):
        line = lines[i]
        words = re.sub(NUMBER, " ", line).strip()
        if re.search(r"\b(afghanistan|iraq|other)\b", words, re.I):
            labels.append(re.sub(r"\s+", " ", words))
        numbers += [int(n.replace(",", "")) for n in NUMBER.findall(line)]
        if re.search(r"\bAOR\b", line):
            end = i
            break
    if end is None:
        raise ValueError("Could not find the end of the table (the 'AOR' total row)")
    labels.append("USCENTCOM AOR")
    if len(numbers) != 4 * len(labels):
        raise ValueError(f"Found {len(numbers)} numbers for {len(labels)} rows: {numbers}")
    rows = []
    for k, label in enumerate(labels):
        area = "USCENTCOM AOR total" if k == len(labels) - 1 else area_from_label(label)
        rows.append((area, label, *numbers[4 * k: 4 * k + 4]))
    return rows


def text_a(pdf: Path) -> str:
    with pdfplumber.open(pdf) as doc:
        return "\n".join((p.extract_text(layout=True) or "") for p in doc.pages[:3])


def text_b(pdf: Path) -> str:
    result = subprocess.run(
        ["pdftotext", "-layout", "-l", "3", str(pdf), "-"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    fields = ["report_file", "fiscal_year", "fiscal_quarter", "published",
              "area", "label_in_report", "total", "us_citizens",
              "third_country_nationals", "local_nationals"]
    for name, reader in (("a", text_a), ("b", text_b)):
        out_rows, failures = [], []
        for pdf in sorted(RAW.glob("*.pdf")):
            m = FILENAME.search(pdf.name)
            fy, q, mon, yr = 2000 + int(m.group(1)), int(m.group(2)), m.group(3), m.group(4)
            try:
                for row in parse_table(reader(pdf)):
                    out_rows.append([pdf.name, fy, q, f"{mon} {yr}", *row])
            except Exception as err:  # keep going; failures are reported, never guessed
                failures.append(f"{pdf.name}: {err}")
        path = OUT / f"headcounts_reading_{name}.csv"
        with path.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(fields)
            w.writerows(out_rows)
        print(f"Reading {name.upper()}: {len(out_rows)} rows -> {path.relative_to(ROOT)}")
        for fail in failures:
            print(f"  FAILED {fail}")


if __name__ == "__main__":
    main()
