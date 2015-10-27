__author__ = 'yixing'

from elasticsearch import Elasticsearch
import os
import re
import random

PATH = '/Users/yixing/Documents/trec07p/data'
TRAIN = 'train'
TEST = 'test'
INDEX = 'spam'
DOC_TYPE = 'document'
RESULT_PATH = '/Users/yixing/Documents/CS6200/Homework7/result'

def build_index(es):
    filenamelist=os.listdir(PATH)
    train_set = RESULT_PATH + '/' + 'train_set'
    test_set = RESULT_PATH + '/' + 'test_set'
    train_fh = open(train_set, "w")
    test_fh = open(test_set, "w")
    count = 0
    train_count = 0
    test_count = 0
    for x in filenamelist:
        if 'inmail' in x:
            text = parse_file(x)
            class_set = random_set()
            es.index(index = INDEX, doc_type = DOC_TYPE, id = x, body={"class": class_set, "text": text})
            print x
            if class_set == TRAIN:
                train_count += 1
                train_fh.write('%s\n'%x)
            else:
                test_count += 1
                test_fh.write('%s\n'%x)
            count += 1
    train_fh.close()
    test_fh.close()
    print count


def parse_file(filename):
    filepath = PATH + '/' + filename
    fh = open(filepath, "r")
    clean_text = []
    content_begin = False
    for line in fh.readlines():
        try:
            line = line.replace('\n', '').replace('_','').replace('\t','')
            line = line.encode('utf-8')
            line = line.lower()
        except:
            line = ''
        if line.startswith('subject'):
            clean_text.append(line)
        elif line.startswith('line') or len(line) == 0 or line == '\n':
            content_begin = True
        elif content_begin:
            if ' ' not in line and len(line) > 20:
                continue
            if line.startswith('----'):
                continue
            if line.startswith('content-type'):
                continue
            if line.startswith('content-transfer-encoding'):
                continue
            clean_text.append(line)
    # print clean_text
    regression = re.compile(r'<(.*?)>')
    text = ' '.join(clean_text)
    res = regression.subn('',text)
    new_content = res[0]
    # print new_content
    new_content = new_content.replace('=','')
    # print new_content
    fh.close()
    return new_content

def random_set():
    num = random.randint(1,10)
    if num <= 8:
        return TRAIN
    else:
        return TEST

def main():
    es = Elasticsearch()
    build_index(es)



if __name__ == '__main__':
    main()