"""Draw the USCENTCOM-wide contractor total by nationality group, FY2008-FY2025.

Usage:  python code/03_make_figure.py
Output: figures/contractors_by_nationality.png
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
df = pd.read_csv(ROOT / "data" / "clean" / "contractor_census_headcounts.csv")
aor = df[df.area == "USCENTCOM AOR total"].copy()
aor["period"] = aor.fiscal_year + (aor.fiscal_quarter - 1) / 4

groups = [("us_citizens", "U.S. citizens", "#2f5d8a"),
          ("third_country_nationals", "Third-country nationals", "#d08c2c"),
          ("local_nationals", "Local/host-country nationals", "#7a9a5b")]

fig, ax = plt.subplots(figsize=(10, 5.2), dpi=150)
for col, label, color in groups:
    ax.plot(aor.period, aor[col] / 1000, label=label, color=color, linewidth=2)
ax.set_title("DoD contractor personnel in the USCENTCOM area, by nationality group",
             loc="left", fontsize=12, fontweight="bold")
ax.set_ylabel("Personnel (thousands)")
ax.set_xlabel("U.S. fiscal year (quarterly census)")
ax.set_xlim(2008, 2025.5)
ax.set_ylim(bottom=0)
ax.grid(axis="y", color="#dddddd", linewidth=0.8)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
ax.legend(frameon=False, loc="upper right")
fig.text(0.01, 0.01, "Source: U.S. DoD quarterly contractor census reports (68 reports, FY2008 Q3 to FY2025 Q2), "
         "as published. Coverage changes over time; see README.", fontsize=7.5, color="#555555")
fig.tight_layout(rect=(0, 0.03, 1, 1))
out = ROOT / "figures" / "contractors_by_nationality.png"
fig.savefig(out)
print(f"Saved {out.relative_to(ROOT)}")
