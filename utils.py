# -*- coding: utf-8 -*-
import codecs
import csv
import sys
import os
import logging
reload(sys)
sys.setdefaultencoding('utf8')

# The target site flag: only support two sites currently
g_retriever_site = 'retriever.us.oracle.com'
g_demo_site = 'demo.oracle.com'

def load_owner_list(f):
    _owner_list = []
    with codecs.open(f, 'r', 'utf-8') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=',', quotechar='"')
        for row in reader:
            _owner_list.append({"id": row['Email'], "manager": row['Manager'], "country": row['Country']})

    return _owner_list


def load_data(csv_file):
    data = list()
    with open(csv_file, 'rb') as f:
        reader = csv.reader(f)
        first_count = True
        link_index = 9
        for row in reader:
            # do something with row, such as row[0],row[1]
            if first_count:
                first_count = False
                link_index = row.index("Asset Link")
                continue
            data.append(row[link_index])

    return data


def init_log(log_file, logger_name):
    #file_handler = logging.FileHandler(filename=log_file)
    stdout_handler = logging.StreamHandler()
    #handlers = [file_handler, stdout_handler]
    handlers = [stdout_handler]

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(filename)+27s:%(lineno)-4d %(levelname)-8s %(message)s',
        handlers=handlers
    )

    return logging.getLogger(logger_name)


def get_retriever_container_id(url):
    return url.split(':')[-1].split(',')[0]


def get_demo_doc_id(url):
    return url.split(':')[-1]


def get_asset_id_pair(url_strs):
    retriever_container_id = ''
    demo_doc_id = ''
    for url in url_strs.split():
        if len(url) > 0 and '://' in url:
            # get rid of the http:// or https://
            url = url.split('://')[1]
        if url.startswith(g_retriever_site):
            retriever_container_id = get_retriever_container_id(url)
        if url.startswith(g_demo_site):
            demo_doc_id = get_demo_doc_id(url)
    return (retriever_container_id, demo_doc_id)


def match_urls(str_a, str_b):
    (a1, a2) = get_asset_id_pair(str_a)
    (b1, b2) = get_asset_id_pair(str_b)
    result  = False

    if len(a1) > 0 or len(b1) > 0:
        if a1 == b1:
            result = True
    if len(a2) > 0 or len(b2) > 0:
        if a2 == b2:
            result = True

    return result


def csv2list(csv_file):
    data = []
    with codecs.open(csv_file, 'r', encoding='utf8') as f:
        a_reader = csv.DictReader(f)
        data = [row for row in a_reader]
    return data