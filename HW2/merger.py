#! user/bin/python

import heapq
import os
import gzip
CATALOG = '/Users/yixing/Documents/CS6200/Homework2/catalog'
# CATALOG = '/Users/yixing/Documents/CS6200/Homework2/catalog_stop_stem'
# CATALOG = '/Users/yixing/Documents/CS6200/Homework2/catalog_as_is'

TEMPINDEX = '/Users/yixing/Documents/CS6200/Homework2/tempindex'
# TEMPINDEX = '/Users/yixing/Documents/CS6200/Homework2/tempindex_stop_stem'
# TEMPINDEX = '/Users/yixing/Documents/CS6200/Homework2/tempindex_as_is'

RESULT = '/Users/yixing/Documents/CS6200/Homework2/result'

hp = []
total_catalog = {}
tmp_list = []
start_pos = 0
def init_heap():
    """
    initialize a priority queue store 85 item which are the first item in each catalog
    :return: None
    """
    pos = 0
    for f in sorted(total_catalog):
        term = getTermInCatalog(f, pos)
        heapq.heappush(hp, (term, f, pos))

def init_catalog_map():
    """
    initialize a dictionary which contain 85 ge temp catalog
    :return: None
    """
    for f in os.listdir(CATALOG):
        if '.' in f:
            continue
        # catalog = {}
        catalog = []
        filename = CATALOG + "/" + f
        fh = open(filename, "r")
        for line in fh.readlines():
            catalog.append(line[:-1])
        total_catalog[f] = catalog


def getTermFromIndex(filename,pos):
    """
    read the index from temp index file, which the start pos and length come from catalog dictionary
    :param filename: temp index filename
    :param pos: index in catalog map in that which key is filename
    :return: a string has ids, and poses
    """
    index_file = TEMPINDEX + "/" + filename
    fh = open(index_file, "r")
    start, length = getStartPos(filename, pos)
    fh.seek(start)
    tmp_string = fh.read(length).split(" ", 1)[1][:-1]
    return tmp_string

def getStartPos(filename, pos):
    """
    get the start and length from catalog dictionary
    :param filename: catalog filename and the same with the dictionary key
    :param pos: the list in value index
    :return: integer, the start and length
    """
    cata = total_catalog[filename][pos]
    # print cata
    start = cata.split(" ")[1]
    length = cata.split(" ")[2]
    # print start, length
    return int(start), int(length)

def getTermInCatalog(file, pos):
    """
    get the term in catalog dictionary
    :param file: catalog key
    :param pos: index of list in value
    :return: a word
    """
    cata = total_catalog[file][pos]
    term = cata.split(" ")[0]
    return term

def mergeIndex():
    """
    merge the temp index to a final index use the priority queue
    :return: None
    """
    while hp:
        entry = heapq.heappop(hp)
        term = entry[0]
        filename = entry[1]
        pos = entry[2]
        # indexname = TEMPINDEX + "/" + filename
        # fh = open(indexname, "r")
        tmp_string = getTermFromIndex(filename,pos)
        if len(tmp_list) == 0:
            tmp_list.append(term)
            tmp_list.append(tmp_string)
        else:
            if term == tmp_list[0]:
                tmp_list.append(tmp_string)
            else:
                writeToIndex()
                del tmp_list[:]
                tmp_list.append(term)
                tmp_list.append(tmp_string)
        next_pos = pos + 1
        if len(total_catalog[filename]) > next_pos:
            term = getTermInCatalog(filename, next_pos)
            heapq.heappush(hp, (term, filename, next_pos))

def writeToIndex():
    """
    write the final index to the index file without the term, only have doc_id and poses
    :return: None
    """
    filename = RESULT + "/" + "index"
    if not os.path.exists(filename):
        fh = open(filename, "w")
    else:
        fh = open(filename, "a")
    term = tmp_list[0]
    # tmp_string = " ".join(tmp_list) + "\n"
    tmp_string = " ".join(tmp_list[1:]) + "\n"
    # tmp_string += "\n"
    length = len(tmp_string)
    fh.write(tmp_string)
    fh.close()
    writeToCata(term, length)

def writeToCata(term, length):
    """
    write the final catalog to the catalog file with term, start pos, length
    :param term: term
    :param length: string length in index
    :return: None
    """
    global start_pos
    filename = RESULT + "/" + "catalog"
    if not os.path.exists(filename):
        fh = open(filename, "w")
    else:
        fh = open(filename, "a")
    tmp = [term, start_pos, length]
    tmp_string = " ".join(map(str, tmp))+"\n"
    fh.write(tmp_string)
    fh.close()
    start_pos += length
    print start_pos

def main():
    init_catalog_map()
    # print total_catalog
    init_heap()
    mergeIndex()

if __name__ == '__main__':
    main()