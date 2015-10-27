#! /user/bin/python

# Author: Yi Xing, Date: 05/28/2015
# Course: CS6200 Information Retrieval Summer 2015
# This script creat a index for query file in elasticsearch


import elasticsearch
import os, sys

#QUERYFILE='/Users/yixing/Documents/CS6200/AP_DATA/query_desc.51-100.short.txt'
#QUERYFILE='/Users/yixing/Documents/CS6200/query_desc.51-100.short_v3.txt'
QUERYFILE='/Users/yixing/Documents/CS6200/query_desc.51-100.short_v2.txt'
INDEX = 'ap_dataset'
QUERY_TYPE = 'query'


def main():
	es = elasticsearch.Elasticsearch()
	parseQuery(es)

# read query file, get the query number of each query, parse the words in query 
# to build the index by each query
def parseQuery(es):
	fh=open(QUERYFILE,"r")
	querys=fh.readlines()
	new_querys = []
	for query in querys:
		if len(query) < 3:
			continue
		query_num = query.split(".")[0]
		print query_num
		terms= query.split()[4:]
		query = ' '.join(terms)
		es.index(index=INDEX, doc_type=QUERY_TYPE, id = query_num, body={"text": query})
	# return query_num

if __name__ == '__main__':
	main()