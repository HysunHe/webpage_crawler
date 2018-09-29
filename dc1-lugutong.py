# -*- coding: utf-8 -*-
import codecs, os, logging
import requests
import sys
from datetime import datetime
from utils import load_owner_list, init_log

reload(sys)
sys.setdefaultencoding('gbk')

########################### LOGGING ############################################
g_working_dir = os.path.dirname(os.path.realpath(__file__))
g_log_file = "{}/log/{}.log".format(g_working_dir, os.path.basename(__file__))
logger = init_log(g_log_file, __name__)
################################################################################

result_pages_folder = 'result_pages/lugutong'

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en,zh;q=0.9,zh-CN;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'data.eastmoney.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'
}

def get_data_page():
    resp = requests.get('http://data.eastmoney.com/zjlx/dpzjlx.html', headers=headers)
    resp.encoding='gbk'
    print(resp.text)
    datestring = datetime.now().strftime('%Y-%m-%d');
    with codecs.open('./{}/lugotong_{}.html'.format(result_pages_folder, str(datestring)), 'w', 'gbk') as f:
        f.write(resp.text)

if __name__ == "__main__":
    get_data_page()