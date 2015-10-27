__author__ = 'yixing'

from elasticsearch import Elasticsearch
import mmh3
import string


# es_index = 'aiw_test'

# result = es.search(
#     index=es_index,
#     body={
#         "size": 300000,
#         "fields": ["_id"],
#         "query": {
#             "match_all": {}
#         }
#     },
#     timeout=600
# )

# es_ids = xrange(1, 20000)
# for re in result['hits']['hits']:
#     # print re['_id']
#     es_ids.append(re['_id'])
#
# print 'es_ids get...'

es = Elasticsearch()
es_index = 'crawler_yi'
cluster_index = 'm_x_h_cluster'
cluster = Elasticsearch(
    [{'host':'169.254.134.137', 'port': 9201}]
)


es_ids = xrange(1, 22000)
duplication = 0

def merger():
    counter = 0
    for id in es_ids:
        result = es.search(
            index=es_index,
            body={
                    "query": {
                        "filtered": {
                            "query": {
                                "match_all": {}
                            },
                            "filter": {
                                "ids": {
                                    "values": [int(id)]
                                }
                            }
                        }
                    }
                }
        )
        if not result['hits']['hits']:
            continue
        source = result['hits']['hits'][0]['_source']
        url = string.strip(source['url'], '/')
        url_hash = mmh3.hash(url)
        if search_url(url_hash):
            continue
        doc = dict(docno=url, html_Source=source['raw'], HTTPheader=source['header'],author='xing',
                   text=source['text'], title=source['title'], out_links=source['outlinks'])
        res = cluster.index(index=cluster_index, doc_type='document', id=url_hash, body=doc, timeout=60)
        if not res['created']:
            print 'insert error '
            # exit(1)

        counter += 1

        if counter % 100 == 0:
            print '{} entries processed...'.format(counter)

def search_url(url_hash):
    global duplication
    result = cluster.search(
        index = cluster_index,
        body = {
            "query": {
                "filtered": {
                    "query": {
                        "match_all": {}
                    },
                    "filter": {
                        "ids": {
                            "values": [
                                url_hash
                            ]
                        }
                    }
                }
            },
            "fields": []
        }
    )
    if result['hits']['total'] == 1:
        duplication += 1
        print '{} duplicates find.'.format(duplication)
        return True
    else:
        return False


merger()

