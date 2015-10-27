#!/user/bin/python

# Author: Yi Xing, Date: 05/28/2015
# Course: CS6200 Information Retrieval Summer 2015
# This script get each query from elasticsearch,
# pass the query to models class


import os
import re
import models
from nltk.stem.porter import *
from nltk.corpus import stopwords

STOPLIST = stopwords.words('english')
# print STOPLIST
stemmer = PorterStemmer()

# QUERYFILE='/Users/yixing/Documents/CS6200/AP_DATA/query_desc.51-100.short.txt'
# QUERYFILE='/Users/yixing/Documents/CS6200/Homework2/NewQueries.txt'
QUERYFILE='/Users/yixing/Documents/CS6200/Homework2/query_desc.51-100.short_v2.txt'
QUERYPATH = '/Users/yixing/Documents/CS6200/Homework2/temp'


def main():
    type = 4 # the index type
    m = models.QueryModel()
    getIRmodels(m,type) # run 5 function models
    getProximityModel(m) # run proximity search

def getIRmodels(m,type):
    """
    get the query number list query dictionary, for each query use the model function to calculate it
    :param m: QueryModel class
    :param type: index type
    :return: None
    """
    query_numbers, querys = getQuerys(type)
    print query_numbers
    print querys
    for query_num in query_numbers:
        if query_num in querys.keys():
            query = querys[query_num]
            print query
            m.models(query, query_num)

def getProximityModel(m):
    """
    get the query dictionary and for each query us the proximity model to calculate it.
    :param m: QueryModel class
    :return: None
    """
    proximity_query = getProximityQueries()
    for num in proximity_query.keys():
        query = proximity_query[num]
        m.proximity_model(query, num)

def getQuerys(type):
    """
    read the query file and get the query number and useful content, tokenize them by different index type
    :param type: index type
    :return: list of query number and a query content dictionary
    """
    fh=open(QUERYFILE,"r")
    querys=fh.readlines()
    new_querys = {}
    query_numbers = []
    for query in querys:
        if len(query) < 3:
            continue
        queryno = query.split(".")[0]
        query_numbers.append(queryno)
        print query.split(" ",6)[6]
        new_query = createIndex(query.split(" ", 6)[6], type)
        new_querys[queryno] = new_query
    fh.close()
    f2 = open("/Users/yixing/Documents/CS6200/Homework2/quer_stem", "w")
    for num in new_querys:
        tmp = (" ").join(new_querys[num])
        f2.write('%s %s\n'%(num, tmp))
    f2.close()
    return query_numbers, new_querys

def createIndex(string,type):
    """
    index the query content by different type
    :param string: query string
    :param type: index type
    :return: query dictionary with key is query term and value is frequency
    """
    query = tokenizer(string)
    if type == 1:
        query_list = query
    elif type == 2:
        query_list = stemWords(query)
    elif type == 3:
        query_list = removeStopWords(query)
    elif type == 4:
        query_list = stemWords(removeStopWords(query))
    print query_list
    query_map = createMap(query_list)
    return query_map


def removeStopWords(text):
    textlist = []
    for word in text:
        if word not in STOPLIST:
            textlist.append(word)
    return textlist

def stemWords(text):
    stemwords = []
    for word in text:
        newword = stemmer.stem(word)
        stemwords.append(newword)
    return stemwords

def tokenizer(text):
    textlist = re.findall(r"\w+(?:\.?\w+)*",text.lower())
    print textlist
    return textlist

def createMap(query_list):
    map = {}
    for word in query_list:
        if word in map:
            map[word] += 1
        else:
            map[word] = 1
    return map

def getProximityQueries():
    """
    get the proximity query dictionary, with key is the query number and value is query term list
    :return: query dictionary
    """
    fh = open(QUERYPATH, "r")
    query_dict = {}
    for line in fh.readlines():
        if len(line) < 3:
            continue
        query_no = line.split(".")[0]
        # print query_no
        query = line.split(" ")[1:][:-1]
        # print query
        query_dict[query_no] = query
    return query_dict

if __name__ == '__main__':
    main()
