"""Check the extracted headcounts and build the final clean file.

Checks, for every report:
  1. Reading A and reading B agree exactly (two independent PDF readers).
  2. Each row adds up: total = U.S. citizens + third-country + local nationals.
  3. The area rows add up to the report's own USCENTCOM AOR total (every column).
  4. The AOR total matches the number stated in the report's "Key points" text,
     when the text gives an exact figure.
  5. The fiscal year and quarter in the file name match the quarter named in the text.
  6. Big quarter-to-quarter changes (over 30% in the AOR total) are listed for review.

Usage:  python code/02_check_headcounts.py
Output: data/clean/contractor_census_headcounts.csv  (only if every problem is explained)
        data/clean/check_report.md
"""

import re
import subprocess
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "clean"
COLS = ["total", "us_citizens", "third_country_nationals", "local_nationals"]
# Problems found in the published reports themselves. Each was confirmed by looking
# at an image of the printed page, so the numbers here are what the Pentagon printed.
# They are kept as published and flagged in the "note" column; nothing is corrected.
KNOWN_SOURCE_ISSUES = {
    ("FY09_3Q_5A_Aug2009.pdf", "Afghanistan"):
        "As printed, U.S. + TCN + local = 72,968, not the printed total of 73,968.",
    ("FY09_3Q_5A_Aug2009.pdf", "USCENTCOM AOR total"):
        "As printed, the local-national areas add up to 88,793, not the printed 89,793.",
    ("FY15_3Q_5A_Jul2015.pdf", "Other USCENTCOM locations"):
        "As printed, U.S. + TCN + local = 11,698, not the printed total of 11,642.",
    ("FY15_3Q_5A_Jul2015.pdf", "USCENTCOM AOR total"):
        "As printed, U.S. + TCN + local = 41,978, not the printed total of 41,922.",
    ("FY17_1Q_5A_Jan2017.pdf", "Other USCENTCOM locations"):
        "As printed, U.S. + TCN + local = 13,935, not the printed total of 15,935.",
    ("FY17_1Q_5A_Jan2017.pdf", "USCENTCOM AOR total"):
        "As printed, U.S. + TCN + local = 43,549, not the printed total of 45,549.",
    ("FY08_3Q_5A_Aug2008.pdf", "USCENTCOM AOR total"):
        "This report has no row for other USCENTCOM locations; the AOR total includes them.",
    ("FY08_4Q_5A_Nov2008.pdf", "USCENTCOM AOR total"):
        "This report has no row for other USCENTCOM locations; the AOR total includes them.",
    ("FY10_4Q_5A_Dec2010.pdf", "USCENTCOM AOR total"):
        "Revised recount. The report says a first count of 194,405 looked wrong in Afghanistan and was redone.",
}

ORDINAL = {"1st": 1, "first": 1, "2nd": 2, "second": 2, "3rd": 3, "third": 3, "4th": 4, "fourth": 4}


def report_text(name: str) -> str:
    return subprocess.run(["pdftotext", "-layout", "-l", "3", str(RAW / name), "-"],
                          capture_output=True, text=True, check=True).stdout


def stated_total(text: str):
    """The 'approximately N contractor personnel' figure in the key points, if exact."""
    flat = re.sub(r"\s+", " ", text)
    m = re.search(r"(?:approximately|over|about)\s+([\d,]+)\s*(K)?\s+(?:DoD\s+)?contractor personnel", flat, re.I)
    if not m or m.group(2):
        return None
    return int(m.group(1).replace(",", ""))


def stated_quarter(text: str):
    flat = re.sub(r"\s+", " ", text)
    m = re.search(r"\b(1st|2nd|3rd|4th|first|second|third|fourth)\s+quarter\s+(?:of\s+)?"
                  r"(?:fiscal year|FY)\s*(?:\(FY\)\s*)?(\d{2,4})", flat, re.I)
    if not m:
        return None
    yr = int(m.group(2))
    return (2000 + yr if yr < 100 else yr, ORDINAL[m.group(1).lower()])


def main():
    a = pd.read_csv(CLEAN / "headcounts_reading_a.csv")
    b = pd.read_csv(CLEAN / "headcounts_reading_b.csv")
    lines, problems = ["# Check report", ""], 0

    # 1. Two readings agree
    same = a.equals(b)
    lines.append(f"1. Reading A and reading B agree exactly: **{'yes' if same else 'NO'}** "
                 f"({len(a)} rows, {a.report_file.nunique()} reports)")
    if not same:
        problems += 1
        diff = a.merge(b, how="outer", indicator=True).query("_merge != 'both'")
        lines += ["", diff.to_markdown(index=False), ""]

    # 2. Rows add up
    bad = a[a.total != a.us_citizens + a.third_country_nationals + a.local_nationals]
    lines.append(f"2. Rows where total = U.S. + TCN + local: **{len(a) - len(bad)} of {len(a)}**")
    for _, r in bad.iterrows():
        known = (r.report_file, r.area) in KNOWN_SOURCE_ISSUES
        problems += 0 if known else 1
        lines.append(f"   - {r.report_file}, {r.area}: {'known printing error in the report' if known else 'NEW PROBLEM'}")

    # 3. Areas add up to the AOR total
    aor = a[a.area == "USCENTCOM AOR total"].set_index("report_file")[COLS]
    parts = a[a.area != "USCENTCOM AOR total"].groupby("report_file")[COLS].sum()
    mismatch = (aor != parts.loc[aor.index]).any(axis=1)
    lines.append(f"3. Reports whose areas add up to the AOR total: **{(~mismatch).sum()} of {len(aor)}**")
    for f in aor.index[mismatch]:
        known = (f, "USCENTCOM AOR total") in KNOWN_SOURCE_ISSUES
        problems += 0 if known else 1
        lines.append(f"   - {f}: table total {aor.loc[f].tolist()} vs sum of areas {parts.loc[f].tolist()}"
                     f" ({'explained, see note' if known else 'NEW PROBLEM'})")

    # 4 and 5. Compare with the report's own text
    totals_ok, totals_checked, quarter_bad, notes = 0, 0, [], []
    for f, row in aor.iterrows():
        text = report_text(f)
        s = stated_total(text)
        if s is not None:
            totals_checked += 1
            if abs(s - row.total) <= 0.01 * row.total:
                totals_ok += 1
            else:
                known = (f, "USCENTCOM AOR total") in KNOWN_SOURCE_ISSUES
                problems += 0 if known else 1
                notes.append(f"   - {f}: text says {s:,}, table says {row.total:,}"
                             f" ({'explained, see note' if known else 'NEW PROBLEM'})")
        meta = a[a.report_file == f].iloc[0]
        sq = stated_quarter(text)
        if sq != (meta.fiscal_year, meta.fiscal_quarter):
            quarter_bad.append(f"   - {f}: file name says FY{meta.fiscal_year} Q{meta.fiscal_quarter}, text says {sq}")
    lines.append(f"4. Key-points figure matches the table total (within 1%, as the text often rounds): "
                 f"**{totals_ok} of {totals_checked}** reports that state a figure")
    lines += notes
    lines.append(f"5. File name quarter matches the quarter named in the text: "
                 f"**{len(aor) - len(quarter_bad)} of {len(aor)}**")
    lines += quarter_bad
    problems += len(quarter_bad)

    # 6. Big jumps
    t = aor.join(a.drop_duplicates("report_file").set_index("report_file")[["fiscal_year", "fiscal_quarter"]])
    t = t.sort_values(["fiscal_year", "fiscal_quarter"])
    t["change"] = t.total.pct_change()
    jumps = t[t.change.abs() > 0.30]
    lines.append(f"6. Quarters where the AOR total changed by more than 30%: **{len(jumps)}**")
    for f, r in jumps.iterrows():
        lines.append(f"   - {f}: {r.change:+.0%} (to {r.total:,})")

    # Final file: only written if the hard checks pass
    if problems == 0:
        out = a.sort_values(["fiscal_year", "fiscal_quarter", "report_file"], kind="stable").copy()
        out["note"] = [KNOWN_SOURCE_ISSUES.get((f, ar), "") for f, ar in zip(out.report_file, out.area)]
        out.to_csv(CLEAN / "contractor_census_headcounts.csv", index=False)
        lines += ["", f"All checks passed or are explained. Wrote contractor_census_headcounts.csv ({len(out)} rows)."]
    else:
        lines += ["", "Unexplained problems found. The final file was NOT written."]

    (CLEAN / "check_report.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
