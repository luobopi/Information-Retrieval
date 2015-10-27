#!/user/bin/python
# Author: Yi Xing, Date: 05/28/2015
# Course: CS6200 Information Retrieval Summer 2015
# This script get each query from elasticsearch,
# pass the query to models class

import elasticsearch
import os
import sys
import math
import operator
import time

INDEX = 'ap_dataset'
DOC_TYPE = 'document'
# STOPLIST = '/Users/yixing/Documents/CS6200/AP_DATA/stoplist.txt'
QUERY_TYPE = 'query'
OUTPATH = 'result/'
es=elasticsearch.Elasticsearch()

class QueryModel:
    """
    This class calculate IR models
    """
    def __init__(self, client, index, doc_type):
        """
        Initialize class with document numbers document average length,
        document unique vocabulary numbers and a dictionary with all doc length
        :param client: es
        :param index: index name
        :param doc_type: type name
        :return: None
        """
        self.index = index
        self.doc_type = doc_type
        self.client = client
        self.count, self.avgd = self.getAvgLen()
        self.vsize = self.getVsize()
        self.doc_len_dict = self.getDocLenDict()
        self.outputPath = OUTPATH
        print "The total document numbers is: " + str(self.count)
        print "The average length of documents is: " + str(self.avgd)
        print "The vocabulary size is: " + str(self.vsize)

    def getAvgLen(self):
        """
        Use elasctseach query to get the document numbers and average length
        :return: doc_count, avglen
        """
        body={
            "query": {
                "match_all": {}
            },
            "aggs": {
                "avg_docs": {
                    "stats": {
                        "script": "doc['text'].values.size()"
                    }
                }
            }
        }
        aggs = self.client.search(index=self.index, doc_type=self.doc_type, body=body)
        doc_count = aggs['aggregations']['avg_docs']['count']
        avglen = aggs['aggregations']['avg_docs']['avg']
        return doc_count, avglen

    def getDocLen(self, doc_id):
        """
        Use elasticsearch query to get the a document length
        :param doc_id: document id
        :return: length of one document
        """
        body={
            "query": {
                "match": {
                    "docno": doc_id
                }
            },
            "aggs": {
                "avg_docs": {
                    "stats": {
                        "script": "doc['text'].values.size()"
                    }
                }
            }
        }
        aggs = self.client.search(index=self.index, doc_type=self.doc_type,body=body)
        doc_len = aggs['aggregations']['avg_docs']['sum']
        return doc_len

    def getDocLenDict(self):
        """
        Use elastcseach query to get all documents and length
        Build a dictionary to store the documents and their length
        :return: a dictionary
        """
        doc_len_dict = {}
        body = {
          "fields": "docno",
          "query": {
            "match_all": {}
          },
          "size": self.count
        }
        doc = self.client.search(index=self.index, doc_type=self.doc_type, body=body)['hits']['hits']
        for i in doc:
            doc_id = i['fields']['docno'][0]
            # print doc_id
            doc_len_dict[doc_id] = self.getDocLen(doc_id)
        # print len(doc_len_dict)
        return doc_len_dict

    def getVsize(self):
        body = {
            "aggs": {
                "unique_terms": {
                    "cardinality": {
                        "script": "doc['text'].values"
                    }
                }
            }
        }
        unique_terms = self.client.search(index=self.index, doc_type=self.doc_type,body=body)
        vsize = unique_terms['aggregations']['unique_terms']['value']
        return vsize

    def getTF(self, term):
        """
        Use the elasticsearch query to get a word frequency, build a dictionary which the key is
        doc_id and value is the word frequency in this doc. And calculate relative parameters
        :param term: search word
        :return: df, a dictionary of tf, the sum of doc length where has the word, the sum of frequency
        """
        body={
          "fields":"docno",
          "query": {
            "function_score": {
              "query": {
                "term": {
                  "text": term
                }
              },
              "functions": [
                {
                  "script_score": {
                    "lang": "groovy",
                    "script_file": "tf-score",
                    "params": {
                      "term": term,
                      "field": "text"
                    }
                  }
                }
              ],
              "boost_mode": "replace"
            }
          }
        }

        #print body

        # body1=	{
        # 	  "query": {
        # 	    "term": {
        # 	      "text": term
        # 	    }
        # 	  },
        # 	  "explain": True
        # 	}
        # print body
        resp = self.client.search(index=self.index, doc_type=self.doc_type,body=body, explain=False, scroll="100m",size=100)
        # resp = self.client.search(index=self.index, doc_type=self.doc_type,body=body)
        df = resp['hits']['total']
        tf = {}
        # doclen = {}
        sum_doclen = 0
        sum_tf = 0
        # for i in resp['hits']['hits']:
        # 	print i
        # 	print i
        # tfs = {}
        # count = 0
        scrollId= resp['_scroll_id']
        while True:
            if resp is None:
                print "resp none"
                break;
            for i in resp['hits']['hits']:
                # print i
                # time.sleep(1)
                # freq = i['_explanation']['details'][0]['details'][0]['details'][0]['value']
                freq = i['_score']
                # doc_id = i['_source']['docno']
                doc_id = i['fields']['docno'][0]
                # print term,
                # print freq
                tf[doc_id] = freq
                #doc_len = self.getDocLen()
                #doclen[term] = doc_len
                doc_len = self.doc_len_dict[doc_id]
                sum_doclen += doc_len
                sum_tf += freq
                # print i['_score']
                # tfs[i['fields']['docno'][0]] = i['_score']
                # print count
                # count += 1
            resp = self.client.scroll(scroll_id = scrollId, scroll='1000ms')
            if len(resp['hits']['hits']) > 0:
                # print len(resp['hits']['hits'])
                scrollId = resp['_scroll_id']
            else:
                break
        #print len(tf)
        return df, tf, sum_doclen, sum_tf

    def models(self,query,query_num):
        """
        give a query and calculate the score using five models, which are okapiTF, TFiDF, okapiBM25, LM_laplace
        and LM_jm. and write the first 1000 result to the file
        :param query: a dictionary contains word and it frequency
        :param query_num: the query num
        :return: None
        """
        okapi_tf_sigma = {}
        tf_idf_sigma = {}
        bm25_sigma = {}
        lm_laplace = {}
        lm_jm = {}
        # query_len = sum(query.values()) # get length with weight
        query_len = len(query)
        lam = 0.99
        for word in query.keys():
            print word
            df, tfs, sumlen, sumtf= self.getTF(word)
            wqtf = query[word]
            #print tfs
            for doc in tfs.keys():
                doc_len = self.doc_len_dict[doc]
                tf = tfs[doc]
                laplace_base = math.log(1.0/(doc_len + self.vsize))
                jm_base = math.log((1-lam) * (sumtf-tf) / (sumlen-doc_len))
                okapi_tf = self.okapiTF(tf, doc_len)
                # okapi_tf = self.okapiTF(tf, doc_len, wqtf) # calculate with word weight
                tf_idf = self.tfiDF(okapi_tf, df)
                bm25 = self.okapiBM25(tf, doc_len, df, wqtf)
                log_p_laplace = self.lm_laplace(tf, doc_len)
                log_p_jm = self.lm_jm(tf, doc_len, sumtf, sumlen, lam)
                # if doc in lm_jm:
                if doc in okapi_tf_sigma:
                    okapi_tf_sigma[doc] += okapi_tf 
                    tf_idf_sigma[doc] += tf_idf
                    bm25_sigma[doc] += bm25
                    lm_laplace[doc] += log_p_laplace - laplace_base
                    # calculate the lm_laplace with word weight
                    # lm_laplace[doc] += (log_p_laplace - laplace_base) * wqtf
                    lm_jm[doc] += log_p_jm - jm_base
                    # lm_jm[doc] += (log_p_jm - jm_base) * wqtf
                else :
                    okapi_tf_sigma[doc] = okapi_tf
                    tf_idf_sigma[doc] = tf_idf
                    bm25_sigma[doc] = bm25
                    lm_laplace[doc] = (query_len - 1) * laplace_base + log_p_laplace
                    # calculate laplace with word weight
                    # lm_laplace[doc] = (query_len - wqtf) * laplace_base + log_p_laplace * wqtf
                    lm_jm[doc] = (query_len - 1) * jm_base + log_p_jm
                    # calculate jm with word weight
                    # lm_jm[doc] = (query_len - wqtf) * jm_base + log_p_jm * wqtf
        sorted_okapi_tf_sigma = sorted(okapi_tf_sigma.items(), key=operator.itemgetter(1), reverse = True)
        sorted_tf_idf_sigma = sorted(tf_idf_sigma.items(), key=operator.itemgetter(1), reverse = True)
        sorted_bm25_sigma = sorted(bm25_sigma.items(), key=operator.itemgetter(1), reverse = True)
        sorted_lm_laplace = sorted(lm_laplace.items(), key=operator.itemgetter(1), reverse = True)
        sorted_lm_jm = sorted(lm_jm.items(), key=operator.itemgetter(1), reverse = True)

        self.writeFile("okapitf", query_num, sorted_okapi_tf_sigma)
        self.writeFile("tfidf", query_num, sorted_tf_idf_sigma)
        self.writeFile("bm25", query_num, sorted_bm25_sigma)
        self.writeFile("lmlaplace", query_num, sorted_lm_laplace)
        self.writeFile("lmjm", query_num,sorted_lm_jm)
        # print sorted_okapi_tf_sigma
        self.bordaCount(query_num, sorted_okapi_tf_sigma, sorted_tf_idf_sigma,sorted_bm25_sigma,
            sorted_lm_laplace, sorted_lm_jm)

        return sorted_okapi_tf_sigma, sorted_tf_idf_sigma, sorted_bm25_sigma, sorted_lm_laplace, sorted_lm_jm

    # def okapiTF(self, tf, doc_len, wqtf): # calculate with word weights
    def okapiTF(self, tf, doc_len):
        okapi_tf = tf / (tf + 0.5 + 1.5 * (doc_len/self.avgd))
        return okapi_tf
        #return okapi_tf * wqtf

    def tfiDF(self, okapi_tf, df):
        tf_idf = okapi_tf * (math.log(self.count) - math.log(df))
        return tf_idf

    def okapiBM25(self, tf, doc_len, df, wqtf):
        k1 = 1.5
        k2 = 1.5
        b = 0.75
        part1 = (math.log(self.count + 0.5) - math.log(df + 0.5))
        part2 = (tf + k1 * tf) / (tf + k1 * ((1-b) + b * (doc_len/self.avgd)))
        part3 = (wqtf + k2 * wqtf) / (wqtf + k2)
        bm25 = part1 * part2 * part3
        return bm25

    def lm_laplace(self, tf, doc_len):
        p_laplace = (tf + 1.0)/(doc_len + self.vsize)
        return math.log(p_laplace)

    def lm_jm(self, tf, doc_len, sum_tf, sum_len, lam):
        p_jm = lam * (tf/doc_len) + (1- lam)*((sum_tf - tf)/(sum_len - doc_len))
        return math.log(p_jm)

    def writeFile(self,filename,query_num,query_result):
        """
        Write the result in given name file
        :param filename: the output filename
        :param query_num: query number
        :param query_result: a dictionary stores the query reuslt
        :return: None
        """
        output = self.outputPath + filename
        if not os.path.exists(output):
            f=open(output, "w")
        else :
            f=open(output, "a")
        count = 1
        for k in query_result:
            if count <= 1000:
                f.write('%s Q0 %s %d %f Exp\n'%(query_num, k[0], count, k[1]))
                count += 1
            else: break
        f.close()

    def bordaCount(self, query_num, okapitf, tfidf, bm25, lmlaplace, lmjm):
        bordacount = {}
        for i in range(1000):
            okapitf_doc = okapitf[i][0]
            tfidf_doc = tfidf[i][0]
            bm25_doc = bm25[i][0]
            lmlaplace_doc = lmlaplace[i][0]
            lmjm_doc = lmjm[i][0]
            point = 1000 - i
            bordacount = self.addDoc(okapitf_doc, point, bordacount)
            bordacount = self.addDoc(tfidf_doc, point, bordacount)
            bordacount = self.addDoc(bm25_doc, point, bordacount)
            bordacount = self.addDoc(lmlaplace_doc, point, bordacount)
            bordacount = self.addDoc(lmjm_doc, point, bordacount)
        sorted_bordacount = sorted(bordacount.items(), key=operator.itemgetter(1), reverse = True)
        self.writeFile("bordacount", query_num, sorted_bordacount)

    def addDoc(self, doc, point, bordacount):
        if doc in bordacount:
            bordacount[doc] += point
        else: 
            bordacount[doc] = point
        return bordacount

