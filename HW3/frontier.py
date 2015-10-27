#! user/bin/python]
# -*- coding: utf-8 -*-

__author__ = 'yixing'

import itertools
import urlparse
import robotparser
import heapq
PATH = '/Users/yixing/Documents/CS6200/Homework3/seeds'
FILTER = ['facebook', 'twitter', 'youtube', 'americanheritage']
MAX_LINKS = 1000

class Frontier:
    '''
    This class manages the frontier. The frontier is a priority queue, store the links prepare to crawl, when it need to
    pop a url out, according to their priorities, pop the most priority url out
    '''

    def __init__(self):
        self.pq = []
        self.entry_finder = {}
        self.REMOVED = '<removed-url>'
        self.domain_size = {}
        self.in_links = {}
        # self.out_links= {}
        self.level = 0
        self.counter = itertools.count()
        self.seed = PATH
        self.visited = set()
        self.robot_dict = {}
        self.filter = FILTER
        self.no_robot = set()

    def initial_queue(self):
        '''
        initialize the queue, put three seeds in the queue
        :return:
        '''
        in_links = MAX_LINKS
        count = 0
        fh = open(self.seed, "r")
        lines = fh.readlines()
        for line in lines:
            url = line[:-1]
            print 'initial url: {}'.format(url)
            # print line
            self.in_links[url] = in_links
            count = next(self.counter)
            entry = [self.level, -in_links, count, url]
            self.entry_finder[url] = entry
            heapq.heappush(self.pq, entry)

            # heapq.heappush(self.pq, (in_links, self.level, count, url))
            # count += 1
            self.add_robot_dict(url)
        print self.pq
        fh.close()

    def check_push_url(self, can_url, parent_url):
        '''
        check if the url could push into the frontier. The url should not be visited and should be english url
        also, it domain cannot be FILTER list
        :param can_url: url
        :param parent_url: it's parent url
        :return: None
        '''

        if can_url in self.visited:
            return None

        try:
            can_url.decode('ascii')
        except Exception,e:
            # print 'decode(ascii) excep: {} | {}'.format(url, e)
            return None

        for forbidden in self.filter:
            if forbidden in can_url:
                return None
        self.add_url(can_url)



    def add_url(self, url):
        '''
        add a url in the queue, if the url has been added in the queue, add a remove tag on the previous url
        and fresh the in links count and push the url in the queue
        :param url: the url should push the queue
        :return: None
        '''
        level = self.level
        if url in self.entry_finder:
            level = self.entry_finder[url][0]
            self.remove_url(url)
        if url in self.in_links:
            self.in_links[url] += 1
        else:
            self.in_links[url] = 1

        count = next(self.counter)
        entry = [level, -self.in_links[url], count, url]
        self.entry_finder[url] = entry
        # print url
        heapq.heappush(self.pq, entry)

    def remove_url(self, url):
        '''
        give an existing url a remove tag
        :param url: existing url
        :return: None
        '''
        entry = self.entry_finder.pop(url)
        entry[-1] = self.REMOVED

    def pop_url(self):
        '''
        pop the lowest priority url, raise KeyError if it is empty
        :return: the pop url
        '''
        while self.pq:
            self.level, in_links, count, url = heapq.heappop(self.pq)
            # print "The level is: ", level
            # print "It has ", in_links, "in links"
            # print "It enter at No. ", count
            if url is not self.REMOVED:
                print "The level is: ", self.level
                print "It has ", - in_links, "in links"
                print "It enter at No. ", count
                print url
                del self.entry_finder[url]
                self.visited.add(url)
                self.level += 1
                return url
        raise KeyError('pop from an empty priority queue')

    def add_robot_dict(self, url):
        '''
        if url domain has robot.txt, add it into robot dictionary, if not, add it in the no robot dictionary
        :param url: url will add domain in robot dictionary
        :return: None
        '''
        up = urlparse.urlparse(url)
        domain = up.netloc
        try:
            rp = robotparser.RobotFileParser()
            rp.set_url('http://' + domain + '/robots.txt')
            rp.read()
            print "read robots file for ", domain
            self.robot_dict[domain] = rp
        except:
            print "cannot find robot file for ", domain
            self.no_robot.add(domain)










s = Frontier()
# s. initial_queue()
