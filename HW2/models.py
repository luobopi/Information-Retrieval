#!/user/bin/python
# Author: Yi Xing, Date: 05/28/2015

import os
import sys
import math
import operator
import heapq


OUTPATH = '/Users/yixing/Documents/CS6200/Homework2/models/'
# es=elasticsearch.Elasticsearch()

DOCLEN_FILE = '/Users/yixing/Documents/CS6200/Homework2/doc_uniterm_length_stop_stem'
# DOCLEN_FILE = '/Users/yixing/Documents/CS6200/Homework2/doc_uniterm_length_as_is'

DOCID_PATH = '/Users/yixing/Documents/CS6200/Homework2/id_doc_id'
RESULT = '/Users/yixing/Documents/CS6200/Homework2/result'

class QueryModel:
    """
    This class calculate IR models
    """
    def __init__(self):
        self.docIdDict = self.getDocId()
        self.vsize, self.catalog = self.getVsize()
        self.count, self.avgd, self.doc_len_dict = self.getDocLenDict()
        self.outputPath = OUTPATH

        print "The total document numbers is: " + str(self.count)
        print "The average length of documents is: " + str(self.avgd)
        print "The vocabulary size is: " + str(self.vsize)

    def getDocId(self):
        """
        read the doc id file and build a map for id and real doc id, the key is id and value is doc id
        :return: a doc id map
        """
        fh = open(DOCID_PATH, "r")
        doc_id_dict = {}
        for line in fh.readlines():
            id = line.split(" ")[0]
            doc_id = line.split(" ")[1][:-1]
            doc_id_dict[id] = doc_id
        fh.close()
        return doc_id_dict

    def getDocLenDict(self):
        doc_len_dict = {}
        total_length = 0
        fh = open(DOCLEN_FILE, "r")
        for line in fh.readlines():
            id = line.split(" ")[0]
            length = int(line.split(" ")[1][:-1])
            doc_id = self.docIdDict[id]
            doc_len_dict[doc_id] = length
            total_length += length
        dcount = len(doc_len_dict)
        avglen = float(total_length) / float(dcount)
        print "the doc count is:" + str(dcount)
        print "the doc average length" + str(avglen)
        return dcount, avglen, doc_len_dict


    def getVsize(self):
        filename = RESULT + "/" + "catalog"
        catalog = {}
        vsize = 0
        fh = open(filename, "r")
        for line in fh.readlines():
            term = line.split(" ")[0]
            start = line.split(" ")[1]
            length = line.split(" ")[2][:-1]
            catalog[term] = [start, length]
            vsize += 1
        return vsize, catalog

    def getTermIndex(self, term):
        start = int(self.catalog[term][0])
        length = int(self.catalog[term][1])
        filename = RESULT + "/" + "index"
        fh = open(filename, "r")
        fh.seek(start)
        term_index = fh.read(length)[:-1].split(" ")
        # term_index = fh.read(length).split(" ",1)[1][:-1].split(" ")
        fh.close()
        tf = {}
        df = 0
        pos_dict = {}
        sum_doclen = 0
        sum_tf = 0
        for i in range(len(term_index)):
            # if i % 3 == 0:
            if i % 2 == 0:
                id = term_index[i]
                doc_id = self.docIdDict[id]
                df += 1
            # elif i % 3 == 1:
            #     doc_tf = float(term_index[i])
            #     tf[doc_id] = doc_tf
            #     sum_tf += doc_tf
            # elif i % 3 == 2:
            #     poses = map(int, term_index[i].split(","))
            #     pos_dict[doc_id] = poses
            elif i % 2 == 1:
                poses = map(int, term_index[i].split(","))
                pos_dict[doc_id] = poses
                doc_tf = float(len(poses))
                tf[doc_id] = doc_tf
                sum_tf += doc_tf
            sum_doclen += self.doc_len_dict[doc_id]
        return df, tf, sum_doclen, sum_tf, pos_dict


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
            df, tfs, sumlen, sumtf, _ = self.getTermIndex(word)
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

        self.writeFile("okapitf", query_num, okapi_tf_sigma)
        self.writeFile("tfidf", query_num, tf_idf_sigma)
        self.writeFile("bm25", query_num, bm25_sigma)
        self.writeFile("lmlaplace", query_num, lm_laplace)
        self.writeFile("lmjm", query_num, lm_jm)
        # print sorted_okapi_tf_sigma
        # self.bordaCount(query_num, sorted_okapi_tf_sigma, sorted_tf_idf_sigma,sorted_bm25_sigma,
        #     sorted_lm_laplace, sorted_lm_jm)

        # return sorted_okapi_tf_sigma, sorted_tf_idf_sigma, sorted_bm25_sigma, sorted_lm_laplace, sorted_lm_jm

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
        # print tf, doc_len, sum_tf, sum_len,lam
        p_jm = lam * (tf/doc_len) + (1- lam)*((sum_tf - tf)/(sum_len - doc_len))
        # print p_jm
        return math.log(p_jm)

    def writeFile(self,filename,query_num,query_result):
        """
        Write the result in given name file
        :param filename: the output filename
        :param query_num: query number
        :param query_result: a dictionary stores the query reuslt
        :return: None
        """
        sorted_query_result = sorted(query_result.items(), key=operator.itemgetter(1), reverse = True)
        output = self.outputPath + filename
        if not os.path.exists(output):
            f=open(output, "w")
        else :
            f=open(output, "a")
        count = 1
        for k in sorted_query_result:
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
        # sorted_bordacount = sorted(bordacount.items(), key=operator.itemgetter(1), reverse = True)
        # self.writeFile("bordacount", query_num, sorted_bordacount)
        self.writeFile("bordacount", query_num, bordacount)

    def addDoc(self, doc, point, bordacount):
        if doc in bordacount:
            bordacount[doc] += point
        else: 
            bordacount[doc] = point
        return bordacount

    def proximity_model(self, query, num):
        doc_term_pos_dict = {}
        for word in query:
            _, _, _, _, pos_dict = self.getTermIndex(word)
            # word_pos_dict[word]
            for id in pos_dict.keys():
                if id in doc_term_pos_dict:
                    doc_term_pos_dict[id].append({word: pos_dict[id]})
                else:
                    doc_term_pos_dict[id] = [{word: pos_dict[id]}]
            # print doc_term_pos_dict
                # print doc_term_pos_dict
        doc_score_dict = {}
        for id in doc_term_pos_dict.keys():
            term_pos_list = doc_term_pos_dict[id]
            print term_pos_list
            if len(term_pos_list) == 1:
                score = 0
            else:
                score = self.getProximityScore(term_pos_list, id)
            doc_score_dict[id] = score
        self.writeFile("proximity", num, doc_score_dict)

    def getProximityScore(self, term_pos_list, id):
        c = 1500
        doc_len = self.doc_len_dict[id]
        min_span = doc_len
        num_word = len(term_pos_list)
        hp = []
        for i in range(len(term_pos_list)):
            word = term_pos_list[i].keys()[0]
            pos = term_pos_list[i][word][0]
            heapq.heappush(hp, (pos, i, 0))
        while len(hp)>= num_word:
            largest = heapq.nlargest(1, hp)[0][0]
            smallest = heapq.nsmallest(1, hp)[0][0]
            span = largest - smallest
            if span < min_span:
                min_span = span
            tmp_tuple = heapq.heappop(hp)
            i = tmp_tuple[1]
            word = term_pos_list[i].keys()[0]
            next_list_pos = tmp_tuple[2] + 1
            if next_list_pos >= len(term_pos_list[i][word]):
                continue
            else:
                pos = term_pos_list[i][word][next_list_pos]
                heapq.heappush(hp, (pos, i, next_list_pos))
        score = float((c - min_span) * num_word) / (doc_len + self.vsize)
        return score

