@echo off
set start=%date% %time%
echo Start ==== %start%

del result_pages\retriever\*.html
del result_csv\retriever_results.csv
rem del log\*.log

python a0_retrScratcher.py
python a1_retrAnalyzer.py

echo Started === %start%
echo End     === %date% %time%

pause