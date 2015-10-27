__author__ = 'yixing'

import string

from elasticsearch import Elasticsearch

es = Elasticsearch([
    {'host': '169.254.142.191', 'port':'9201'}
])

def write_to_file():

    out_put_path = 'link_file.txt'
    out_file = open(out_put_path, 'w', 1024 * 1024 * 32)


    body = {
        "fields": ['out_links', 'in_links', 'docno'],
        "query": {
            "match_all": {}
        }
    }

    resp = es.search(index='m_x_h_cluster', doc_type='document', body=body, scroll='1000m', size=500)
    scroll_id = resp['_scroll_id']
    while True:
        for i in resp['hits']['hits']:
            url = string.strip(i['fields']['docno'][0])
            out_size = 0
            ins = []
            if 'out_links' in i['fields']: out_size = len(i['fields']['out_links'])
            if 'in_links' in i['fields']:
                for in_link in i['fields']['in_links']:
                    ins.append(string.strip(in_link))
            out_file.write('{}\t{}\t{}\n'.format(url, out_size, '\t'.join(ins)))

        resp = es.scroll(scroll_id=scroll_id, scroll='1000m')
        if len(resp['hits']['hits']) > 0:
            scroll_id = resp['_scroll_id']
            print 'scroll once'
        else:
            break

    out_file.close()

    print('finish...')

if __name__ == '__main__':
    write_to_file()