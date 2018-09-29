import codecs
import csv
import sys

from utils import get_asset_id_pair, get_demo_doc_id, get_retriever_container_id, match_urls

reload(sys)
sys.setdefaultencoding('utf8')

a = codecs.open(r'C:\Users\kxin\Documents\code\python\reusable-assets-collectors\result_csv\all_results.csv', 'r', encoding='utf8')
a_reader = csv.DictReader(a)
a_rows = [row for row in a_reader]
b = codecs.open(r"C:\Users\kxin\Documents\code\python\reusable-assets-collectors\in\assets_20180326-1.csv", 'r', encoding='utf8')
b_reader = csv.DictReader(b)
b_rows = [row for row in b_reader]

print '{} rows in all_results.csv'.format(len(a_rows))
print '{} rows in assets_20180326.csv'.format(len(b_rows))

headers = [ 'RETRIEVER_CONTAINER_ID',
            'DEMO_DOC_ID',
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
            'Comment',
            'Format',
            'Program',
            'Geography',
            'Organization',
            'Language',
            'Asset_URL',
            'Description']

with codecs.open(r'C:\Users\kxin\Documents\code\python\reusable-assets-collectors\result_csv\all_results_with_id.csv', 'wb', encoding='utf8') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    new_data = []
    for a_row in a_rows:
        (retriever_container_id, demo_doc_id) = get_asset_id_pair(a_row['Asset_URL'])
        a_row['RETRIEVER_CONTAINER_ID'] = retriever_container_id
        a_row['DEMO_DOC_ID'] = demo_doc_id
        new_data.append(a_row)
    #print new_data;
    writer.writerows(new_data)


headers2 = [ 'RETRIEVER_CONTAINER_ID',
            'DEMO_DOC_ID',
            'Creation Date',
            'Update Date',
            'Creator',
            'Pillar',
            'Domain',
            'Product',
            'Sub-product',
            'Language',
            'Asset Name',
            'Asset Description',
            'Asset Link',
            'Download Count',
            'Comments'
            ]

with codecs.open(r'C:\Users\kxin\Documents\code\python\reusable-assets-collectors\in\assets_20180326-1_with_id.csv', 'wb', encoding='utf8') as f:
    writer = csv.DictWriter(f, fieldnames=headers2)
    writer.writeheader()
    new_data = []
    for b_row in b_rows:
        (retriever_container_id, demo_doc_id) = get_asset_id_pair(b_row['Asset Link'])
        b_row['RETRIEVER_CONTAINER_ID'] = retriever_container_id
        b_row['DEMO_DOC_ID'] = demo_doc_id
        new_data.append(b_row)
    #print new_data;
    writer.writerows(new_data)

a.close()
b.close()
