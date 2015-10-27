#! user/bin/python

import re
import os
from nltk.stem.porter import *
from nltk.corpus import stopwords


STOPLIST = stopwords.words('english')
# print STOPLIST

stemmer = PorterStemmer()


FILEPATH = '/Users/yixing/Documents/CS6200/AP_DATA/ap89_collection'
TEMPPATH = '/Users/yixing/Documents/CS6200/Homework2/tempindex'
CATALOGPATH = '/Users/yixing/Documents/CS6200/Homework2/catalog'
HOMEPATH = '/Users/yixing/Documents/CS6200/Homework2/'


# total = {}

# This is a global dictionary store term information, Which key is term and value is a list
# each item in list is a map has doc_id, tf, and offset
index_dict = {}
# global variable count the doc number, if dcount > 1000, will be reinitialize
dcount = 1
# global variable count total doc number which has read
dnum = 0
# a dictionary store the inverted list doc id and its real id in documents
docidToid = {}
# a dictionary store the inverted list doc id and its real length
doclen = {}
# a dictionary store the inverted list doc id and its doc unique term length
docuniq = {}
# a global variable to count the current file number
tempFileCount = 0


def removeStopWords(text):
    """
    Use the STOPLIST to remove stop words
    :param text: a list of words
    :return: a list of words which remove all stop words
    """
    textlist = []
    for word in text:
        if word not in STOPLIST:
            textlist.append(word)
    return textlist

def stemWords(text):
    """
    Use stemmer to stem word in list
    :param text: a list of words
    :return: a new list of words which all of words has been stemmed
    """
    stemwords = []
    for word in text:
        newword = stemmer.stem(word)
        stemwords.append(newword)
    return stemwords

def tokenizer(text):
    textlist = re.findall(r"\w+(?:\.?\w+)*",text.lower())
    # print textlist
    return textlist

def asIsIndex(text,id):
    textlist = tokenizer(text)
    # print textlist
    map = createDocIndexMap(textlist, id)
    # print len(map)
    insertDocMapToDict(map)

def stopWordRemoveIndex(text, id):
    textlist = tokenizer(text)
    newtextlist = removeStopWords(textlist)
    # print newtextlist
    map = createDocIndexMap(newtextlist, id)
    # print len(map)
    insertDocMapToDict(map)

def stemIndex(text, id):
    textlist = tokenizer(text)
    newtextlist = stemWords(textlist)
    map = createDocIndexMap(newtextlist, id)
    # print len(map)
    insertDocMapToDict(map)

def stemStopWordRemoveIndex(text, id):
    textlist = tokenizer(text)
    newtextlist = stemWords(removeStopWords(textlist))
    # print newtextlist
    map = createDocIndexMap(newtextlist,id)
    # print len(map)
    insertDocMapToDict(map)


def createDocIndexMap(textlist, id):
    """
    For one doc, create a index is a dictionary, the key is term
    value is a map which has doc_id, tf, and offset
    :param textlist: a list of words
    :param id: the doc id which will stored in inverted list
    :return: a dictionary
    """
    terms = {}
    offset = 0
    # print len(textlist)
    for word in textlist:
        # print word
        if word not in terms:
            # terms[word] = {'doc_id': id, 'tf': 1, 'offset': [offset]}
            terms[word] = {'doc_id': id, 'offset': [offset]}
        else:
            # terms[word]['tf'] += 1
            terms[word]['offset'].append(offset)
        offset += 1
    storeLen(id, len(textlist))
    storeUniTerm(id, len(terms))
    return terms

def insertDocMapToDict(map):
    """
    Insert the one doc dictionary to the global term dictionary
    :param map: a dictionary, key is term and value is a map
    :return: None
    """
    for word in map.keys():
        if word in index_dict:
            index_dict[word].append(map[word])
        else:
            index_dict[word]=[map[word]]

def storeLen(id, length):
    doclen[id] = length

def storeUniTerm(id, length):
    docuniq[id] = length

def indexFile(file, type):
    """
    Read the file line by line and store each doc in file as text to create index
    When the doc number greater than 1000, write them in a file and initialize the dictionary
    :param file: file in path
    :param type: the type to handle the text
    :return: None
    """
    global dcount
    global dnum
    global tempFileCount
    # type = 4
    fh = open(file, "r")
    line = fh.readline()
    while line:
        while line and '<DOC>' not in line:
            line = fh.readline()
        while line and 'DOCNO' not in line:
            line = fh.readline()
        doc_id = line.split(" ")[1]
        while line and '<TEXT>' not in line:
            line = fh.readline()
        text = ''
        while line and '<TEXT>' in line:
            line = fh.readline()
            while line and '</TEXT>' not in line:
                text += line
                line = fh.readline()
            while line and '<TEXT>' not in line and '<DOC>' not in line:
                line = fh.readline()
            if line and '<TEXT>' in line:
                continue
            else:
                break
        # asIsIndex(text, dnum)
        createIndex(text, dnum, type)
        docidToid[dnum] = doc_id
        dnum += 1
        dcount += 1
        if dcount > 1000:
            print "1000"
            tempFileCount += 1
            writeToFile(tempFileCount)
            index_dict.clear()
            dcount = 1
    fh.close()

def createIndex(text, dnum, type):
    if type == 1:
        asIsIndex(text, dnum)
    elif type == 2:
        stopWordRemoveIndex(text, dnum)
    elif type == 3:
        stemIndex(text, dnum)
    else:
        stemStopWordRemoveIndex(text, dnum)

def writeToFile(tempFileCount):
    """
    create the index and catalog file. The index file store the index_dict which is an inverted list
    the catalog file store the begin position and length of each term in index file bytes
    The index file format is id tf poses, which poses seperate by ","
    :param tempFileCount: The file name
    :return: None
    """
    index_output = TEMPPATH + "/" + str(tempFileCount)
    catalog_output = CATALOGPATH + "/" + str(tempFileCount)
    index = open(index_output, "w")
    cata = open(catalog_output, "w")
    begin_pos = 0
    for word in sorted(index_dict):
        tmplist = []
        tmplist.append(word)
        # print word
        # fh.write('%s '%(word))
        for doc in index_dict[word]:
            pos_string = ",".join(map(str, doc['offset']))
            # tmplist.extend([str(doc['doc_id']), str(doc['tf']), pos_string])
            tmplist.extend([str(doc['doc_id']), pos_string])
            # fh.write('%d %d %s '%(doc['doc_id'], doc['tf'], pos_string))
        # tmplist.append("\n")
        text_string = " ".join(tmplist)
        text_string = text_string + "\n"
        offset = len(text_string)
        index.write(text_string)
        cata.write('%s %d %d\n'%(word, begin_pos, offset))
        begin_pos += offset
    index.close()
    cata.close()

def writeDocLen(type):
    if type == 1:
        filename = "as_is"
    elif type == 2:
        filename = "stop"
    elif type == 3:
        filename = "stem"
    elif type == 4:
        filename = "stop_stem"
    output = HOMEPATH + "doclength_" + filename
    fh = open(output, "w")
    for id in sorted(doclen):
        fh.write('%d %d\n'%(id, doclen[id]))
    fh.close()

def writeDocUniq(type):
    if type == 1:
        filename = "as_is"
    elif type == 2:
        filename = "stop"
    elif type == 3:
        filename = "stem"
    elif type == 4:
        filename = "stop_stem"
    output = HOMEPATH + "doc_uniterm_length_" + filename
    fh = open(output, "w")
    for id in sorted(docuniq):
        fh.write('%d %d\n'%(id, docuniq[id]))
    fh.close()

def writeDocId():
    output = HOMEPATH + "id_doc_id"
    fh = open(output, "w")
    for id in sorted(docidToid):
        fh.write('%d %s\n'%(id, docidToid[id]))
    fh.close()

def main():
    global dcount
    global tempFileCount
    type = 4
    # tempFileCount = 0
    for f in os.listdir(FILEPATH):
        if 'ap' in f:
            filename = FILEPATH + "/" + f
            indexFile(filename,type)
            print filename
    if dcount != 1:
        tempFileCount += 1
        writeToFile(tempFileCount)
        # dcount = 0
    writeDocLen(type)
    writeDocUniq(type)
    writeDocId()
    # mergeIndex()



if __name__ == '__main__':
    main()





