import elasticsearch
import os
import json

path = '/Users/yixing/Documents/CS6200/AP_DATA/ap89_collection'

INDEX = 'ap_dataset'

DOC_TYPE = 'document'

def main():
	es=elasticsearch.Elasticsearch()
	read_files(es)

def read_files(es):
	filenamelist=os.listdir(path)
	id = 0
	for x in xrange(len(filenamelist)):
		if 'ap' in filenamelist[x]:
			filename = path+"/"+filenamelist[x]
			print filename
			id = parse_file(filename, es, id)
	print id


def parse_file(fn, es, id):
	fh = open(fn, "r")
	l = fh.readline()
	while l:
		while l and '<DOC>' not in l:
			l=fh.readline()
		while l and '<DOCNO>' not in l:
			l=fh.readline()
		doc_id=l.split(" ")[1]
		while l and '<TEXT>' not in l:
			l=fh.readline()
		text=''
		while l and '<TEXT>' in l:
			l=fh.readline()
			while l and '</TEXT>' not in l:
				text += l
				l =fh.readline()
			while l and '<TEXT>' not in l and '<DOC>' not in l:
				l =fh.readline()
			if l and '<TEXT>' in l:
				continue
			else: break
		es.index(index = INDEX, doc_type = DOC_TYPE, id = id, body={"docno": doc_id, "text": text})
		id += 1
		#print id
	fh.close()
	return id


if __name__ == '__main__':
	main()