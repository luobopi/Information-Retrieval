#!/user/bin/python

# Author: Yi Xing, Date: 05/28/2015
# Course: CS6200 Information Retrieval Summer 2015
# This script get each query from elasticsearch,
# pass the query to models class

import elasticsearch
import os, sys
import math
import models

QUERYFILE='/Users/yixing/Documents/CS6200/AP_DATA/query_desc.51-100.short.txt'
INDEX = 'ap_dataset'
QUERY_TYPE = 'query'
DOC_TYPE = 'document'
def main():
	es = elasticsearch.Elasticsearch()
	query_numbers, querys = getQuerys(es)
	m = models.QueryModel(es, INDEX, DOC_TYPE)
	for query_num in query_numbers:
		if query_num in querys.keys():
			query = querys[query_num]
			print query
			m.models(query, query_num)

# get the query number from query file 
# according to the query number get the querys which is a dictinoary
# the key is the query number, the value is the relative query
# In querys, each query contains the words and their frequence in query 	
def getQuerys(es):
	fh=open(QUERYFILE,"r")
	querys=fh.readlines()
	new_querys = {}
	query_numbers = []
	for query in querys:
		query_map = {}
		if len(query) < 3:
			continue
		no = query.split('.')[0]
		query_numbers.append(no)
		new_query = es.termvector(index=INDEX, doc_type=QUERY_TYPE, id=no)['term_vectors']
		#print new_query
		# if not new_query.has_key('text'):
		# 	#print new_query,
		# 	print no
		# # print new_query['text']['terms']
		# else:
		for word in new_query['text']['terms']:
			tf = new_query['text']['terms'][word]['term_freq']
			query_map[word]=tf
		new_querys[no]=query_map
	fh.close()
	return query_numbers, new_querys



if __name__ == '__main__':
	main()