# -*- coding: utf-8 -*-
import codecs, os, logging
import requests
from bs4 import BeautifulSoup
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

# For demo.oracle.com

with codecs.open('./conf.json', 'r', encoding='utf8') as conf_list_file:
    config = json.load(conf_list_file)
    session_id = config["demo.oracle.com"]["session_id"]
    cookie = config["demo.oracle.com"]["cookie"]

result_pages_folder = 'result_pages/demo'
my_asset_list = "current asset list: "

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en,zh;q=0.9,zh-CN;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': cookie,
    'Host': 'demo.oracle.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'
}


def asset_detail_url(session_id, doc_id):
    # https://demo.oracle.com/apex/f?p=DEMOSTORE:15:105241645467504:::15:P15_DOC_ID:62473
    return 'https://demo.oracle.com/apex/f?p=DEMOSTORE:15:{}:::15:P15_DOC_ID:{}'.format(session_id, doc_id)


def get_asset_detail_page(owner, doc_id):
    logger.info('*** asset_detail_url: ' + asset_detail_url(session_id, doc_id))
    resp = requests.get(asset_detail_url(session_id, doc_id), headers=headers)
    with codecs.open('./{}/{}_{}_summary.html'.format(result_pages_folder, str(owner['id']), str(doc_id)), 'w', 'utf-8') as f:
        f.write(resp.text)


def get_asset_pages(owner, doc_id):
    get_asset_detail_page(owner, doc_id)


def summary_url(session_id, owner):
    # https://demo.oracle.com/apex/f?p=100:10:105241645467504:SEARCH:NO:10,RP:P10_INDUSTRY,P10_RELEASE,P10_CONTENT,P10_REGION,P10_PRODUCT,P10_PRODUCT_CHECK,P10_SECURITY,P10_LANGUAGE,P10_SHOW_GSE_ONLY,P10_SHOW_ORACLE_ONLY,F_DELETE_FILTERS,F_SEARCH:,,,,,,,,0,1,N,kevin%2Exin%40oracle%2Ecom
    # only use the name part as the key work, not use @oracle.com
    owner_name = owner['id'].split('@')[0]
    
    # https://demo.oracle.com/apex/f?p=100:10:113256527845827:SEARCH:NO:10,RP:P10_INDUSTRY,P10_RELEASE,P10_CONTENT,P10_REGION,P10_PRODUCT,P10_PRODUCT_CHECK,P10_SECURITY,P10_LANGUAGE,P10_SHOW_GSE_ONLY,P10_SHOW_ORACLE_ONLY,F_DELETE_FILTERS,F_SEARCH:,,,,,,,,1,0,N,bradley%2Epetrik#

    summary_url = 'https://demo.oracle.com/apex/f?p=100:10:{}:SEARCH:NO:10,RP:P10_INDUSTRY,P10_RELEASE,P10_CONTENT,P10_REGION,P10_PRODUCT,P10_PRODUCT_CHECK,P10_SECURITY,P10_LANGUAGE,P10_SHOW_GSE_ONLY,P10_SHOW_ORACLE_ONLY,F_DELETE_FILTERS,F_SEARCH:,,,,,,,,0,1,Y,{}'.format(session_id, owner_name)

    logger.info('************ summary_url is :' + summary_url)

    return summary_url

def extract_summary_to_get_details(owner, html_file):
    # global skip
    global my_asset_list

    soup = BeautifulSoup(html_file, 'lxml')

    if len(soup.select('#searchfResults')) == 0:
        return

    # no need to contain /apex in prefix
    url_prefix = 'http://demo.oracle.com'
    divs = soup.select('#searchfResults')[0]
    rows = divs.select(".searchRows")
    skip_first = 1 # No need to skip the first line for demo
    show_only_url = 1
    for row in rows:
        if skip_first == 0:
            skip_first = skip_first + 1
            continue
        else:
            skip_first = skip_first + 1
            real_author = row.select('.docContainer')[0].select('.detailsUl')[0].select('.detailsLi')[0].text
            if not (owner['id'].split('@')[0] in real_author):
                # need to check the search result again
                # because GSE has no exact-match search function
                continue
            else:
                link = row.select('.titleClass')[0].select('.titleLink')[0]
                if show_only_url == 0:
                    logger.info('   Asset Title :' + link.get_text().strip())
                my_link = url_prefix + link['href']
                logger.info('   Asset Link :' + my_link)

                doc_id = my_link.split(':')[-1].strip()
                my_asset_id = doc_id.split(',')[0].strip()

                if my_asset_list.find(my_asset_id) == -1:
                    my_asset_list = my_asset_list + ',' + my_asset_id
                else:
                    continue

                get_asset_pages(owner, doc_id)


def get_summary_page(owner):
    data = {
        "p_flow_id": 100,
        "p_flow_step_id": 10,
        "p_instance": session_id,
        "p_request": "APXWGT",
        "p_widget_action": "paginate",
        "p_pg_min_row": 1,
        "p_pg_max_rows": 1000, # use the 1000 as max item in one page
        "p_pg_rows_fetched": 1000, # use the 1000 as max item in one page
    }

    # use the post method to pass the form data
    resp = requests.post(summary_url(session_id, owner), headers=headers, data=data)

    with codecs.open('./{}/{}_summary.html'.format(result_pages_folder, str(owner['id'])), 'w', 'utf-8') as f:
        f.write(resp.text)

    # starting to handle details for asset
    get_details_page(owner)
    # done


def get_details_page(owner):
    logger.info('Processing {}'.format(owner['id']))

    logger.info('*** _summary: ' + './{}/{}_summary.html'.format(result_pages_folder, str(owner['id'])))
    
    with codecs.open('./{}/{}_summary.html'.format(result_pages_folder, str(owner['id'])), 'r', encoding='utf8') as f:
        extract_summary_to_get_details(owner, f)

    logger.info('Done for {}'.format(owner['id']))


def get_pages(owner):
    get_summary_page(owner)


def scrap_demo():
    owner_list = load_owner_list('./author_list.csv')
    owner_list.extend(load_owner_list('./author_unknown_list.csv'))
    for owner in owner_list:
        get_pages(owner)


if __name__ == "__main__":
    scrap_demo()