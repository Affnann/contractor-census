# Check report

1. Reading A and reading B agree exactly: **yes** (251 rows, 68 reports)
2. Rows where total = U.S. + TCN + local: **246 of 251**
   - FY09_3Q_5A_Aug2009.pdf, Afghanistan: known printing error in the report
   - FY15_3Q_5A_Jul2015.pdf, Other USCENTCOM locations: known printing error in the report
   - FY15_3Q_5A_Jul2015.pdf, USCENTCOM AOR total: known printing error in the report
   - FY17_1Q_5A_Jan2017.pdf, Other USCENTCOM locations: known printing error in the report
   - FY17_1Q_5A_Jan2017.pdf, USCENTCOM AOR total: known printing error in the report
3. Reports whose areas add up to the AOR total: **65 of 68**
   - FY08_3Q_5A_Aug2008.pdf: table total [242558, 42827, 82919, 116812] vs sum of areas [203660, 34335, 66771, 102554] (explained, see note)
   - FY08_4Q_5A_Nov2008.pdf: table total [266678, 40890, 100640, 125148] vs sum of areas [231698, 33450, 76490, 121758] (explained, see note)
   - FY09_3Q_5A_Aug2009.pdf: table total [243735, 50958, 102984, 89793] vs sum of areas [243735, 50958, 102984, 88793] (explained, see note)
4. Key-points figure matches the table total (within 1%, as the text often rounds): **67 of 68** reports that state a figure
   - FY10_4Q_5A_Dec2010.pdf: text says 194,405, table says 176,340 (explained, see note)
5. File name quarter matches the quarter named in the text: **68 of 68**
6. Quarters where the AOR total changed by more than 30%: **0**

All checks passed or are explained. Wrote contractor_census_headcounts.csv (251 rows).
