# -*- coding: utf-8 -*-
import os
import logging
import codecs
import requests
from bs4 import BeautifulSoup
import re
import json
import sys
from utils import load_owner_list, init_log

reload(sys)
sys.setdefaultencoding('utf8')

########################### LOGGING ############################################
g_working_dir = os.path.dirname(os.path.realpath(__file__))
g_log_file = "{}/log/{}.log".format(g_working_dir, os.path.basename(__file__))
logger = init_log(g_log_file, __name__)
################################################################################

# For retriever.us.oracle.com

with codecs.open('./conf.json', 'r', encoding='utf8') as conf_list_file:
    config = json.load(conf_list_file)
    session_id = config["retriever.us.oracle.com"]["session_id"]
    cookie = config["retriever.us.oracle.com"]["cookie"]

result_pages_folder = 'result_pages/retriever'
my_asset_list = "current asset list: "

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': cookie,
    'Host': 'retriever.us.oracle.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}


def asset_detail_url(session_id, assetowner_id):
    return 'http://retriever.us.oracle.com/apex/f?p=121:22:' + str(session_id) + '::NO:RP:P22_CONTAINER_ID,P22_PREV_PAGE:' + str(assetowner_id) + ''


def get_asset_detail_page(owner, assetowner_id):
    resp = requests.get(asset_detail_url(session_id, assetowner_id), headers=headers)
    with codecs.open('./{}/{}_{}_summary.html'.format(result_pages_folder, str(owner['id']), str(assetowner_id)), 'w', 'utf-8') as f:
        f.write(resp.text)


def get_asset_pages(owner, assetowner_id):
    get_asset_detail_page(owner, assetowner_id)


def summary_url(session_id, owner):
    summaryUrl = 'http://retriever.us.oracle.com/apex/f?p=121:21:{}::NO:RP,21:P21_APPLY_AS_FILTERS,P21_AS_NAME,P21_AS_DESCRIPTION,P21_AS_SUBMITTER,P21_AS_AUTHOR,P21_AS_TIER,P21_AS_UPDATE_DATE_FROM,P21_AS_UPDATE_DATE_TO,P21_SEARCH_WITHIN,P21_AS_CONT_TYPE,P21_AS_OWNER,P21_TAB_POS,P21_INCLUDE_CATS,P21_SEARCH_WORD,P21_AS_CONTENT_TYPE,P21_SORT_BY:Y,,,,,,,,N,,{},0,,,,DOWN#orderBy:Y|columnOrder:11_desc|tabPos:0|refreshPage:'.format(session_id, owner['id'])
    logger.info('*** summaryUrl: ' + summaryUrl)
    return summaryUrl

def extract_summay_to_get_details(owner, file):
    # global skip
    global my_asset_list

    soup = BeautifulSoup(file, 'lxml')

    if len(soup.select('#reportSingle')) == 0:
        return

    url_prefix='http://retriever.us.oracle.com/apex/'
    table = soup.find("table", { "class" : "t1standardalternatingrowcolors" })
    rows = table.findAll("tr")
    skip_first = 0
    show_only_url = 1
    for row in rows:
        if skip_first == 0 :
            skip_first = skip_first + 1
            continue
        else:
            skip_first = skip_first + 1
            cells = row.findAll("td")
            for hidden in cells[1].find_all(style=re.compile(r'display:\s*none')):
                hidden.decompose()
            if show_only_url == 0 :
                logger.info('   Last Updated Date:' + cells[1].get_text().strip())
            for hidden in cells[2].find_all(style=re.compile(r'display:\s*none')):
                hidden.decompose()
            if show_only_url == 0 :
                logger.info('   Asset Title :' + cells[2].get_text().strip())
                
            link = cells[2].find_all('a', href=True)
            my_link = url_prefix+link[0]['href']
            logger.info('   Asset Link: ' + my_link)
            my_asset_author_id = my_link.split(':')[-1].strip()
            logger.info('   my_asset_author_id: ' + my_asset_author_id)
            my_asset_id = my_asset_author_id.split(',')[0].strip()
            logger.info('   my_asset_id: ' + my_asset_id)

            if my_asset_list.find(my_asset_id) == -1:
                my_asset_list = my_asset_list +','+ my_asset_id
            else:
                continue

            get_asset_pages(owner, my_asset_author_id)


def get_eng_summary_page(owner):
    resp = requests.get(summary_url(session_id, owner), headers=headers)
    with codecs.open('./{}/{}_summary.html'.format(result_pages_folder, str(owner['id'])), 'w', 'utf-8') as f:
        f.write(resp.text)

    get_eng_details_page(owner)


def get_eng_details_page(owner):
    logger.info('Processing {}'.format(owner['id']))
    summary_file = codecs.open('./{}/{}_summary.html'.format(result_pages_folder, str(owner['id'])), 'r', encoding='utf8')
    extract_summay_to_get_details(owner, summary_file)
    logger.info('Done for {}'.format(owner['id']))


def get_eng_pages(owner):
    get_eng_summary_page(owner)


def scrap_retriever():
    owner_list = load_owner_list('./author_list.csv')
    owner_list.extend(load_owner_list('./author_unknown_list.csv'))
    for owner in owner_list:
        get_eng_pages(owner)


if __name__ == "__main__":
    scrap_retriever()

