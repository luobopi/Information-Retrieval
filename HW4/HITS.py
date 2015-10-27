__author__ = 'yixing'

import string
import math
import operator

TOP1000 = '/Users/yixing/Documents/CS6200/Homework4/top1000.urls.txt'
INLINKS = '/Users/yixing/Documents/CS6200/Homework4/link_file.txt'
TOPHUB = '/Users/yixing/Documents/CS6200/Homework4/top500_hub.txt'
TOPAUT = '/Users/yixing/Documents/CS6200/Homework4/top500_aut.txt'

root = []
base = set()
all_in_links_map = {}
in_links_map = {}
out_links_map = {}
D = 50
THRESHOLD = 0.1

def create_root_set():
    global base
    fh = open(TOP1000, "r")
    for line in fh.readlines():
        line = string.strip(line, '\n')
        root.append(line)
    fh.close()
    base = set(root)
    # print len(root)
    # print root[1000]

def read_in_links_file():
    fh = open(INLINKS, "r")
    for line in fh.readlines():
        # print line
        line = string.strip(line, "\n")
        newline = string.strip(line, "\t")
        node = newline.split("\t")[0]
        in_links = newline.split("\t")[2:]
        all_in_links_map[node] = in_links
    print len(all_in_links_map)
    fh.close()


def create_base_set():
    add_out_links()
    add_in_links()
    create_in_links_map()

def create_in_links_map():
    for node in base:
        in_links = all_in_links_map[node]
        # in_links_map[node] = []
        for in_link in in_links:
            if in_link in root:
                if node not in in_links_map:
                    in_links_map[node] = []
                    in_links_map[node].append(in_link)
                else:
                    in_links_map[node].append(in_link)
    print "the in links map is", len(in_links_map)


def add_out_links():
    for node in all_in_links_map:
        in_links = all_in_links_map[node]
        for in_link in in_links:
            if in_link in root:
                # print "add", in_link, "out links"
                # if in_link not in out_links_map.keys():
                if in_link not in out_links_map:
                    out_links_map[in_link] = set()
                    out_links_map[in_link].add(node)
                else:
                    out_links_map[in_link].add(node)
                base.add(node)
    print "the out links map is", len(out_links_map)
    print "add", len(base), "out links to base"

def add_in_links():
    global D
    for node in all_in_links_map:
        if node in root:
            # print "add",node, "in links"
            in_links = all_in_links_map[node]
            if len(in_links) > 50:
                for i in range(50):
                    base.add(in_links[i])
            else:
                for link in in_links:
                    base.add(link)
    print "add", len(base), "in links to base"

def rank():

    # pre_hub = {key: 1.0 for key in out_links_map}
    # pre_aut = {key: 1.0 for key in in_links_map}
    hub = {key: 1.0 for key in out_links_map}
    aut = {key: 1.0 for key in in_links_map}
    # prev_hub_diff = 0
    # prev_aut_diff = 0
    counter = 0
    pre_hub_perplexity = 0
    pre_aut_perplexity = 0
    cur_hub_perplexity = perplexity(hub)
    cur_aut_perplexity = perplexity(aut)
    while not convergence(pre_hub_perplexity, cur_hub_perplexity, pre_aut_perplexity, cur_aut_perplexity):
        # new_hub = {key: 0.0 for key in out_links_map}
        # new_aut = {key: 0.0 for key in in_links_map}
        # new_hub = {}
        # new_aut = {}
        for node in aut:
        # for node in pre_aut:
            # for link in in_links_map[node]:
            #     if link in pre_hub:
            #         new_aut[node] += pre_hub[link]
            # new_aut[node] = sum(pre_hub[link] for link in in_links_map)
            # new_aut[node] = sum(pre_hub[link] for link in in_links_map[node])
            aut[node] = sum(hub[link] for link in in_links_map[node])
        # new_aut = normalize(new_aut)
        aut = normalize(aut)
        for node in hub:
        # for node in pre_hub:
            # for link in out_links_map[node]:
            #     if link in pre_aut:
            #         new_hub[node] += pre_aut[link]
            # new_hub[node] = sum(pre_aut[link] for link in out_links_map)
            # new_hub[node] = sum(new_aut[link] for link in out_links_map[node])
            hub[node] = sum(aut[link] for link in out_links_map[node])
        # print "The new hub is", new_hub
        # print "The new aut is", new_aut

        # new_hub = normalize(new_hub)
        hub = normalize(hub)
        # convergence=calculate_convergence(pre_hub,pre_aut, new_hub, new_aut)
        pre_hub_perplexity = cur_hub_perplexity
        pre_aut_perplexity = cur_aut_perplexity
        # cur_hub_perplexity = perplexity(new_hub)
        # cur_aut_perplexity = perplexity(new_aut)
        cur_hub_perplexity = perplexity(hub)
        cur_aut_perplexity = perplexity(aut)
        # pre_hub = new_hub
        # pre_aut = new_aut
        print "This is turn", counter
        counter += 1
    # output_result(pre_hub, pre_aut)
    output_result(hub, aut)
# def calculate_diff(old, new):
#     diff = 0
#     for node in old:
#         diff += (old[node]-new[node])**2
#     return diff
#
# def calculate_convergence(pre_hub,pre_aut, new_hub, new_aut):
#     hub_diff = calculate_diff(pre_hub, new_hub)
#     aut_diff = calculate_diff(pre_aut, new_aut)
#     print "the aut diff is", aut_diff
#     print "the hub diff is", hub_diff
#     return max(hub_diff, aut_diff) < THRESHOLD

def perplexity(vector):
    s = 0
    for node in vector:
        p = vector[node] ** 2
        # print "the p is", p
        s += p * math.log(p, 2)
    return pow(2, (-1 * s))

def convergence(pre_hub_perplexity, cur_hub_perplexity, pre_aut_perplexity, cur_aut_perplexity):
    print "the pre hub, pre aut is", pre_hub_perplexity, pre_aut_perplexity
    print "the cur hub, cur aut is", cur_hub_perplexity, cur_aut_perplexity
    diff_hub = abs(pre_hub_perplexity - cur_hub_perplexity)
    diff_aut = abs(pre_aut_perplexity - cur_aut_perplexity)

    return max(diff_aut, diff_hub) < THRESHOLD

def normalize(vector):
    # sum_m = sum(x ** 2 for x in vector.values())
    sum_m = 0
    for node in vector:
        sum_m += vector[node] ** 2
    norm = math.sqrt(sum_m)
    for node in vector:
        norm_value = float(vector[node])/norm
        vector[node]=norm_value
    return vector


def output_result(hub, aut):
    sort_hub = sorted(hub.items(), key=operator.itemgetter(1), reverse = True)
    sort_aut = sorted(aut.items(), key=operator.itemgetter(1), reverse = True)
    hubfile = open(TOPHUB, "w")
    for i in range(500):
        node = sort_hub[i][0]
        score = sort_hub[i][1]
        hubfile.write('%s\t%s\n'%(node,score))
    autfile = open(TOPAUT,"w")
    for i in range(500):
        node = sort_aut[i][0]
        score = sort_aut[i][1]
        autfile.write('%s\t%s\n'%(node, score))
    hubfile.close()
    autfile.close()


def main():
    create_root_set()
    read_in_links_file()
    create_base_set()

    rank()
    # output_result()

if __name__ == '__main__':
    main()