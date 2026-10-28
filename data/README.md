# Data

## Source

| Item | Details |
|---|---|
| Reports | *Contractor Support of U.S. Operations in the USCENTCOM Area of Responsibility* (quarterly; also called the "5A" reports) |
| Publisher | U.S. Department of Defense, Office of the Under Secretary for Acquisition and Sustainment (prepared by its logistics office) |
| Listing page | https://www.acq.osd.mil/asds/log/cso/ocs/cent.html (FY2010 onward) and https://www.acq.osd.mil/asds/log/cso/ocs/CENTCOM_reports_archvd.html (FY2008 to FY2009) |
| File location | `https://www.acq.osd.mil/asds/log/cso/ocs/docs/CENTCOM/<file name>` |
| Downloaded on | 28 October 2026 |
| Number of reports | 68 (FY2008 Q3 to FY2025 Q2) |
| License / terms | Works of the U.S. federal government are not subject to U.S. copyright (17 U.S.C. § 105). |

## Files

- `raw/` holds the 68 PDFs exactly as downloaded, with their original file names. One original name contains a space: `FY11_3Q_5A Jul2011.pdf`.
- The listing page also has two hidden links, for July and October 2025. Both files return "not found" on the Pentagon's site, and the April 2025 report states that it is the final report.
- `clean/contractor_census_headcounts.csv` is the dataset (see the main README). License: CC BY 4.0.
- `clean/headcounts_reading_a.csv` and `clean/headcounts_reading_b.csv` are the two independent readings used for checking.
- `clean/check_report.md` is the output of the checks.
