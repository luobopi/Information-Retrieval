__author__ = 'yixing'

from elasticsearch import Elasticsearch

class Store:

    def __init__(self):
        self.client = Elasticsearch()
        # self.index = 'crawler'
        self.index = 'crawler_yi'
        self.doc_type = 'document'

    def insert(self, id, url, header, title, text, raw, out_links,):
        try:
            in_links = []
            body = {
                'url': url,
                'header': header,
                'title': title,
                'text': text,
                'raw': raw,
                'inlinks': in_links,
                'outlinks': out_links
            }
            self.client.index(index = self.index, doc_type = self.doc_type, id = id, body = body, timeout = 600)
        except Exception,e:
            print 'ES insert exception'.format(e)
        return id

    def update(self):
        pass