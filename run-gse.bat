@echo off
set start=%date% %time%
echo Start ==== %start%

del result_pages\demo\*.html
del result_csv\demo_results.csv
rem del log\*.log

python b0_demoScratcher.py
python b1_demoAnalyzer.py

echo Started === %start%
echo End     === %date% %time%

pause