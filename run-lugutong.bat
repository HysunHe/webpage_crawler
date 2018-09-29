@echo off
set start=%date% %time%
echo Start ==== %start%

rem del result_pages\demo\*.html
rem del result_csv\demo_results.csv
rem del log\*.log

set http_proxy=http://cn-proxy.jp.oracle.com:80
set https_proxy=http://cn-proxy.jp.oracle.com:80

python dc1-lugutong.py

echo Started === %start%
echo End     === %date% %time%

pause