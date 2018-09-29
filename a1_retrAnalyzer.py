# -*- coding: utf-8 -*-
from codecs import open
from bs4 import BeautifulSoup
import csv
import re,os,logging
import sys
from utils import load_owner_list, init_log
reload(sys)
sys.setdefaultencoding('utf8')

########################### LOGGING ############################################
g_working_dir = os.path.dirname(os.path.realpath(__file__))
g_log_file = "{}/log/{}.log".format(g_working_dir, os.path.basename(__file__))
logger = init_log(g_log_file, __name__)
################################################################################

skip = False
my_asset_list = "current asset list:"


def extract_details(html_file, fields, owner):
    global skip
    soup = BeautifulSoup(html_file, "lxml")

    if len(soup.select('h2')) == 0:
        skip = True
        return
    #
    my_table = soup.find("td", { "class" : "center-region main-region-td" })
    my_paragraph = my_table.findAll("p")
    for p in my_paragraph:
        if len(p.select('b')) == 0:
            continue
        my_bold = p.find("b")
        my_column = my_bold.get_text().strip().split(':')[0]
        for hidden in p.find_all("b"):
            hidden.decompose()
        for hidden in p.find_all("script"):
            hidden.decompose()
        my_value = p.get_text().strip()
        #

        if my_column == 'Description':
            fields['Description'] = my_value
        if my_column == 'Document Format':
            fields['Format'] = my_value
        if my_column == 'Program':
            fields['Program'] = my_value
        if my_column == 'Geography':
            fields['Geography'] = my_value
        if my_column == 'Organization':
            fields['Organization'] = my_value
        if my_column == 'Language':
            fields['Language'] = my_value
        if my_column == 'Solution Area':
            fields['Solution_Area'] = re.sub('\r?\n', ' ',my_value)
        if my_column == 'Product Line':
            fields['Product_Line'] = re.sub('\r?\n', ' ',my_value)
        if my_column == 'Author':
            fields['Asset_Author'] = my_value
        if my_column == 'Owner/s':
            fields['Asset_Owner'] = owner['id'] #No need to get it from file
        if my_column == 'Creation Date':
            fields['Create_Date'] = my_value
        if my_column == 'Competitor':
            fields['Competitor'] = my_value

    # This two fields are not in files, just pass the value from owner
    fields['Asset_Owner_Manger'] = owner['manager']
    fields['Country'] = owner['country']


def extract_summay(owner, html_file, fields):
    # global skip
    global my_asset_list

    soup = BeautifulSoup(html_file, 'lxml')

    if len(soup.select('#reportSingle')) == 0:
        return

    fields['Asset_Author'] = owner['id']

    url_prefix = 'http://retriever.us.oracle.com/apex/'
    table = soup.find("table", {"class": "t1standardalternatingrowcolors"})
    rows = table.findAll("tr")
    skip_first = 0
    show_only_url = 1
    result_data = []
    for row in rows:
        if skip_first == 0 :
            skip_first = skip_first + 1
            continue
        else:
            skip_first = skip_first + 1
            fields = {}
            fields['Asset_Author'] = owner['id']
            cells = row.findAll("td")

            for hidden in cells[1].find_all(style=re.compile(r'display:\s*none')):
                hidden.decompose()
            if show_only_url == 0 :
                logger.info('   Last Updated Date: ' + cells[1].get_text().strip())
            fields['Last_Update'] = cells[1].get_text().strip()

            for hidden in cells[2].find_all(style=re.compile(r'display:\s*none')):
                hidden.decompose()
            if show_only_url == 0 :
                logger.info('   Asset Title: ' + cells[2].get_text().strip())
            fields['Asset_Title'] = cells[2].get_text().strip()

            link = cells[2].find_all('a', href=True)
            my_link = url_prefix+link[0]['href']
            logger.info('   Asset Link: ' + my_link)
            fields['Asset_URL'] = my_link
            my_asset_author_id = my_link.split(':')[-1].strip()
            my_asset_id = my_asset_author_id.split(',')[0].strip()

            if my_asset_list.find(my_asset_id) == -1:
                my_asset_list = my_asset_list + ',' + my_asset_id
            else:
                continue
            #
            logger.debug(my_asset_list)

            for hidden in cells[3].find_all(style=re.compile(r'display:\s*none')):
                hidden.decompose()
            if show_only_url == 0 :
                logger.info('   Author: ' + cells[3].get_text().strip())

            for hidden in cells[5].find_all(style=re.compile(r'display:\s*none')):
                hidden.decompose()

            if show_only_url == 0 :
                logger.info('   Score: ' + cells[5].get_text().strip())
            fields['Score'] = cells[5].get_text().strip()

            for hidden in cells[6].find_all(style=re.compile(r'display:\s*none')):
                hidden.decompose()

            if show_only_url == 0 :
                logger.info('   Downloads: ' + cells[6].get_text().strip())
            fields['Downloads'] = cells[6].get_text().strip()
            # extract detail information.
            with open('./result_pages/retriever/{}_{}_summary.html'.format(owner['id'], my_asset_author_id), 'r', encoding='utf8') as detail_file:
                extract_details(detail_file, fields, owner)
            result_data.append(fields)

    return result_data


def analyze_retriever():
    with open('./result_csv/retriever_results.csv', 'wb', encoding='utf8') as result_file:
        my_field_headers = [
            'Asset_Title',
            'Last_Update',
            'Create_Date',
            'Asset_Author',
            'Asset_Owner',
            'Asset_Owner_Manger',
            'Country',
            'Product_Line',
            'Solution_Area',
            'Score',
            'Downloads',
            'Format',
            'Program',
            'Geography',
            'Organization',
            'Language',
            'Asset_URL',
            'Description',
            'Competitor'
        ]
        writer = csv.DictWriter(result_file, fieldnames=my_field_headers)
        writer.writeheader()

        skipped_engs = []
        results = []
        owner_list = load_owner_list('./author_list.csv')
        owner_list.extend(load_owner_list('./author_unknown_list.csv'))
        for owner in owner_list:
            logger.info('Processing {}'.format(owner['id']))
            my_field_values = {}
            with open('./result_pages/retriever/{}_summary.html'.format(owner['id']), 'r', encoding='utf8') as summary_file:
                result_rows = extract_summay(owner, summary_file, my_field_values)
                if result_rows and len(result_rows) > 0:
                    results.extend(result_rows)
            logger.info('Done for {}'.format(owner['id']))

        if len(results) > 0:
            writer.writerows(results)

        with open('./log/retriever_skipped.log', 'wb', encoding='utf8') as skipped_file:
            skipped_file.write('\n'.join([owner['id'] for owner in skipped_engs]))


if __name__ == "__main__":
    analyze_retriever()