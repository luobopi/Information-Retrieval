__author__ = 'yixing'

import mmh3
import string
import hashlib

QUERY_LIST = ['152101', '152102', '152103']
EVAL = '/Users/yixing/Documents/CS6200/Homework5/eval.txt'
QREL = '/Users/yixing/Documents/CS6200/Homework5/qrel.txt'
RANK = '/Users/yixing/Documents/CS6200/Homework5/rank.txt'

def read_eval():
    fh = open(EVAL, "r")
    qrel = open(QREL, "w")
    rank = open(RANK, "w")
    last_query_id = ''
    count = 1
    for line in fh.readlines():
        line = string.strip(line, "\n")
        query_id, url, grade = line.split("\t")
        if query_id == last_query_id:
            count += 1
        else:
            count = 1
        last_query_id = query_id
        print query_id, url, grade
        hash_url = hashlib.md5(url).hexdigest()
        qrel.write('%s %s %s %s\n'%(query_id, 'yi', hash_url, grade))
        # if count <= 200:
        #     rank.write('%s %s %s %d %s %s\n'%(query_id, 'Q0', hash_url, count, 'score', 'Exp'))
        # else:
        #     continue
        rank.write('%s %s %s %d %s %s\n'%(query_id, 'Q0', hash_url, count, 'score', 'Exp'))

    fh.close()
    qrel.close()
    rank.close()

def main():
    read_eval()


if __name__ == '__main__':
    main()

