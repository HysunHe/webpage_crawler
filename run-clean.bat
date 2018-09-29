@echo off
del result_pages\demo\*.html
del result_pages\retriever\*.html
del result_csv\*.csv
del log\*.log
python assets-collector.py
