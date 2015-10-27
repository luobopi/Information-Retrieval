__author__ = 'yixing'

import math
import operator
import string
import re
CRAWLED = '/Users/yixing/Documents/CS6200/Homework4/link_file.txt'
OTHER = '/Users/yixing/Documents/CS6200/Homework4/wt2g_inlinks.txt'
LAMBDA = 0.15

CRAWLED_OUTPUT = '/Users/yixing/Documents/CS6200/Homework4/crawled_top500.txt'
OTHER_OUTPUT = '/Users/yixing/Documents/CS6200/Homework4/other_top500.txt'

THRESHOLD = 1

class PageRank():
    def __init__(self, adjacent_list, out_links, type):
        self.adjacent_list = adjacent_list
        self.out_links = out_links
        self.node_list = sorted(self.adjacent_list.keys())
        self.size = len(self.node_list)
        self.last_vector = {key: 1.0/self.size for key in self.node_list}
        # self.current_vector = {}
        self.sink_links = self.get_sink_links()
        self.LAMBDA = 0.15
        # print self.last_vector
        self.type = type
        print len(self.sink_links)



    def get_sink_links(self):
        sink_links = []
        for node in self.node_list:
            if node not in self.out_links:
                sink_links.append(node)
        return sink_links


    def rank(self):
        count = 0
        prev_perplexity = 0
        cur_perplexity = self.perplexity(self.last_vector)
        while not self.coverage(prev_perplexity, cur_perplexity):

            # current_vector.fromkeys(self.node_list, self.LAMBDA)
            sinkPR = 0
            for node in self.sink_links:
                sinkPR += self.last_vector[node]
            print "The sink PR is", sinkPR
            current_vector = {key: (self.LAMBDA + (1-self.LAMBDA) * sinkPR)/self.size for key in self.node_list}
            for node in self.node_list:
                # print "Now is node:", node
                in_links = self.adjacent_list[node]
                for in_link in in_links:
                    out_links_len = self.out_links[in_link]
                    pagerank = self.last_vector[in_link]
                    # print "out links lenth is", out_links_len
                    # print "last PR is:", pagerank
                    # if current_vector[node]:
                    #     print "node exist in current_vector, the value is ", current_vector[node]
                    # else:
                    #     print "error"
                    current_vector[node] += (1-self.LAMBDA) * (pagerank/out_links_len)
            vector_sum = sum(current_vector.values())
            for node in current_vector:
                current_vector[node] = current_vector[node]/vector_sum
            prev_perplexity = cur_perplexity
            cur_perplexity = self.perplexity(current_vector)
            print "the previous perplexity is", prev_perplexity
            print "the current perplexity is", cur_perplexity
            self.last_vector = current_vector
            # counter += 1
            print "this is the ", count
            count += 1


    def output_result(self):
        output = sorted(self.last_vector.items(), key=operator.itemgetter(1), reverse = True)
        if self.type == 'other':
            fh = open(OTHER_OUTPUT, "w")
        else:
            fh = open(CRAWLED_OUTPUT, "w")
        for i in range(500):
            node = output[i][0]
            rank = output[i][1]
            fh.write('%s %s\n'%(node,str(rank)))


    def perplexity(self, vector):
        s = 0
        for node in vector:
            p = vector[node]
            s += p * math.log(p, 2)
        return pow(2, (-1 * s))

    def coverage(self, prev_perplex, cur_perplex):
        diff = abs(prev_perplex - cur_perplex)
        return diff < THRESHOLD

def get_crawled_adjacent_list():
    fh = open(CRAWLED, "r")
    adjacent_list = {}
    out_links = {}
    # node_list = []
    for line in fh.readlines():
        # print line
        newline = string.strip(line, "\n")
        newline = string.strip(newline, "\t")
        # print newline
        node = newline.split("\t")[0]
        out_links_len = int(newline.split("\t")[1])
        print out_links_len
        in_links = newline.split("\t")[2:]
        # print in_links
        adjacent_list[node] = in_links
        if out_links_len != 0:
            out_links[node] = out_links_len

        # newline = string.strip(line, " \n")
        # print newline
        # # node = ''
        # # out_links_len = 0
        #
        # pre_node = newline.split("http")[1].split()[:-1]
        # print pre_node
        # if len(pre_node) > 1:
        #     node = "http" + (" ").join(pre_node)
        # else:
        #     node = "http" + pre_node[0]
        # out_links_len = int(newline.split("http")[1].split()[-1])
        #
        # in_links = ["http" + link for link in newline.split("http")[2:]]
        #
        # adjacent_list[node] = in_links
        # if out_links_len != 0:
        #     out_links[node] = out_links_len
    print len(out_links)," has out links"
        # node_list.append(node)
    # node_list.sort()
    print "finish input step"
    fh.close()
    return adjacent_list, out_links # , node_list

def get_other_adjacent_list():
    fh = open(OTHER, "r")
    adjacent_list = {}
    out_links = {}
    for line in fh.readlines():
        node  = line.split()[0]
        in_links = line.split()[1:]
        adjacent_list[node] = in_links
        for link in in_links:
            if link in out_links:
                out_links[link] += 1
            else:
                out_links[link] = 1
    fh.close()
    return adjacent_list, out_links

def main():
    other_ad, other_out = get_other_adjacent_list()
    pr1 = PageRank(other_ad, other_out, 'other')
    # print s.last_vector
    pr1.rank()
    pr1.output_result()

    crawl_ad, crawl_out = get_crawled_adjacent_list()
    pr2 = PageRank(crawl_ad, crawl_out, 'crawl')
    pr2.rank()
    pr2.output_result()

if __name__ == '__main__':
    main()