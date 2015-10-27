__author__ = 'hanxuan'

from Utils.ucluster import cluster

DATA_SET = 'm_x_h_cluster'

def create_index(client):
    # create empty index
    client.indices.create(
        index=DATA_SET,
        body={
            'settings': {
                "index": {
                    "store": {
                        "type": "default"
                    },
                    "number_of_shards": 3,
                    "number_of_replicas": 1
                },
                # custom analyzer for analyzing file paths
                'analysis': {
                    "analyzer": {
                        "my_english": {
                            "type": "english",
                            "stopwords_path": "stoplist.txt"
                        }
                    }
                }
            }
        },
        # ignore already existing index
        ignore=400
    )

    client.indices.put_mapping(
        index=DATA_SET,
        doc_type='document',
        body={
            'document': {
                "properties": {
                    "docno": {
                        "type": "string",
                        "store": True,
                        "index": "analyzed",
                        "term_vector": "with_positions_offsets_payloads",
                        "analyzer": "my_english"
                    },
                    "HTTPheader": {
                        "type": "string",
                        "store": True,
                        "index": "not_analyzed"
                    },
                    "html_Source": {
                        "type": "string",
                        "store": True,
                        "index": "no"
                    },
                    "text": {
                        "type": "string",
                        "store": True,
                        "index": "analyzed",
                        "term_vector": "with_positions_offsets_payloads",
                        "analyzer": "my_english"
                    },
                    "title": {
                        "type": "string",
                        "store": True,
                        "index": "analyzed",
                        "term_vector": "with_positions_offsets_payloads",
                        "analyzer": "my_english"
                    },
                    "out_links": {
                        "type": "string",
                        "store": False,
                        "index": "no"
                    },
                    "in_links": {
                        "type": "string",
                        "store": False,
                        "index": "no"
                    },
                    "author":{
                        "type": "string",
                        "store": True,
                        "index": "analyzed",
                        "term_vector": "with_positions_offsets_payloads",
                        "analyzer": "my_english"
                    }
                }
            }
        }
    )

if __name__ == '__main__':

    cluster.indices.delete(index=DATA_SET, ignore=[400, 404])
    cluster.cluster.health(wait_for_status='yellow', request_timeout=5)
    cluster.indices.delete(index=DATA_SET, ignore=[400, 404])
    create_index(cluster)
