# -*- coding: utf-8 -*-
from codecs import open
from bs4 import BeautifulSoup
import csv
import sys
import os
from utils import load_owner_list, init_log
import os.path

reload(sys)
sys.setdefaultencoding('utf8')

# For demo.oracle.com
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

    if len(soup.select('#result_#DOC_ID#')) == 0:
        skip = True
        return


    details_container = soup.select('#result_#DOC_ID#')[0].select('.docContainer')[0].select('.leftList')[0].findAll('li')
    real_author = details_container[0].find('span', {'class': 'bld lrg red'})
    # Check the author again to avoid the bad data
    if not owner['id'] in real_author.get_text().strip():
        skip = True
        return

    # fields['Description'] = details_container[2].find('div', {'class': 'headerDesc'}).get_text().strip()
    fields['Description'] = details_container[1].find('div', {'class': 'headerDesc'}).get_text().strip()

    doc_container = soup.select("#resultList")[0].select(".detailsContainer")[0].select(".docContainer")[0]
    details_list = doc_container.select('.detailsList')
    fields['Last_Update'] = details_list[0].findAll('li')[0].find('span', {'class': 'bld lrg red'}).get_text().strip()
    fields['Create_Date'] = details_list[0].findAll('li')[1].find('span', {'class': 'bld lrg red'}).get_text().strip()
    # fields['Downloads'] = details_list[1].findAll('li')[0].find('span', {'class': 'bld lrg red'}).get_text().strip()
    ######fields['Downloads'] = 0
    # fields['Format'] = details_list[1].findAll('li')[1].find('span', {'class': 'red sml'}).get_text().strip()
    ######fields['Format'] = ''
    ######fields['Program'] = ''
    ######fields['Geography'] = ''
    ######fields['Organization'] = ''
    fields['Language'] = soup.select("#resultList")[0].select(".detailsContainer")[0].select(".attributeContainer")[0].findAll('li', {'class': 'med grey mkp2'})[4].select('.attrUl')[0].get_text().strip()
    ######fields['Solution_Area'] = ''
    ######fields['Product_Line'] = ''

    # No need to get them from file
    fields['Asset_Owner'] = owner['id']
    ######fields['Asset_Author'] = owner['id'].split('@')[0]
    # This two fields are not in files, just pass the value from owner
    ######fields['Asset_Owner_Manger'] = owner['manager']
    ######fields['Country'] = owner['country']
    fields['Keywords'] = soup.select("#resultList")[0].select(".detailsContainer")[0].select(".attributeContainer")[0].findAll('li', {'class': 'med grey mkp2'})[5].select('.attrUl')[0].get_text().strip()
    fields['Industries'] = soup.select("#resultList")[0].select(".detailsContainer")[0].select(".attributeContainer")[0].findAll('li', {'class': 'med grey mkp2'})[2].select('.attrUl')[0].get_text().strip()
    ######fields['Products'] = soup.select("#resultList")[0].select(".detailsContainer")[0].select(".attributeContainer")[0].findAll('li', {'class': 'productsList'})[0].select('.attrUl')[0].get_text().strip()


def extract_summay(owner, html_file, fields):
    # global skip
    global my_asset_list

    soup = BeautifulSoup(html_file, 'lxml')

    if len(soup.select('#searchfResults')) == 0:
        return []

    # no need to contain /apex in prefix
    url_prefix = 'http://demo.oracle.com'
    divs = soup.select('#searchfResults')[0]
    rows = divs.select(".searchRows")
    skip_first = 1
    show_only_url = 1
    results = []
    for row in rows:
        if skip_first == 0:
            skip_first = skip_first + 1
            continue
        else:
            skip_first = skip_first + 1
            real_author = row.select('.docContainer')[0].select('.detailsUl')[0].select('.detailsLi')[0].text
            fields = {}

            ######fields['Asset_Author'] = owner['id'].split('@')[0]

            if not (owner['id'].split('@')[0] in real_author):
                # need to check the search result again
                # because GSE has no exact-match search function
                logger.info('   Find and ignore bad page - expect {}, but got {}'.format(owner['id'].split('@')[0], real_author))
                continue
            else:
                link = row.select('.titleClass')[0].select('.titleLink')[0]
                if show_only_url == 0:
                    logger.info('   Asset Title: ' + link.get_text().strip())

                fields['Asset_Title'] = link.get_text().strip()

                my_link = url_prefix + link['href']
                logger.info('   Asset_URL: ' + my_link)

                fields['Asset_URL'] = my_link

                doc_id = my_link.split(':')[-1].strip()
                my_asset_id = doc_id.split(',')[0].strip()

                if my_asset_list.find(my_asset_id) == -1:
                    my_asset_list = my_asset_list + ',' + my_asset_id
                else:
                    continue

                logger.debug(my_asset_list)

                if show_only_url == 0:
                    logger.info('   Author: ' + owner['id'])

                # score = row.select('.docContainer')[0].select('.detailsUl')[0].findAll('li')[1].find('span', {'class': 'bld lrg red'})
                # if show_only_url == 0:
                #     logger.info('   Score: ' + score.get_text().strip())
                # fields['Score'] = score.get_text().strip()
                ######fields['Score'] = '0'

                # extract detail information.
                fname = './result_pages/demo/{}_{}_summary.html'.format(owner['id'], my_asset_id)
                if os.path.isfile(fname): 
                    with open(fname, 'r', encoding='utf8') as detail_file:
                        extract_details(detail_file, fields, owner)
                        results.append(fields)
                else:
                    logger.error('   FileNotFoundError: ' + fname)

    return results


def analyze_demo():
    with open('./result_csv/demo_results.csv', 'wb', encoding='utf8') as result_file:
        my_field_headers = [
            'Asset_Title',
            'Last_Update',
            'Create_Date',
            ######'Asset_Author',
            'Asset_Owner',
            ######'Asset_Owner_Manger',
            ######'Country',
            ######'Product_Line',
            ######'Solution_Area',
            ######'Score',
            ######'Downloads',
            ######'Format',
            ######'Program',
            ######'Geography',
            ######'Organization',
            'Language',
            'Asset_URL',
            'Description',
            'Keywords',
            'Industries'
            ######'Products'
        ]
        writer = csv.DictWriter(result_file, fieldnames=my_field_headers)
        writer.writeheader()

        skipped_engs = []
        results = []
        owner_list = load_owner_list('./author_list.csv')
        owner_list.extend(load_owner_list('./author_unknown_list.csv'))
        for owner in owner_list:
            logger.info('****** Processing {}'.format(owner['id']))
            my_field_values = {}

            fname = './result_pages/demo/{}_summary.html'.format(owner['id'])
            if os.path.isfile(fname): 
                with open(fname, 'r', encoding='utf8') as summary_file:
                    result_rows = extract_summay(owner, summary_file, my_field_values)
                    if result_rows and len(result_rows) > 0:
                        results.extend(result_rows)
            else:
                logger.error('   FileNotFoundError: ' + fname)

            logger.info('****** Done for {}'.format(owner['id']))

        if len(results) > 0:
            writer.writerows(results)

        with open('./log/demo_skipped.log', 'wb', encoding='utf8') as skipped_file:
            skipped_file.write('\n'.join([owner['id'] for owner in skipped_engs]))


if __name__ == "__main__":
    analyze_demo()
