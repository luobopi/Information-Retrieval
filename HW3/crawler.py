#! user/bin/python
# -*- coding: utf-8 -*-
__author__ = 'yixing'

from urlparse import urlparse
import urllib2
from lxml import etree
import time
from frontier import Frontier
from Parser import ParserTarget
# from elasticsearch import Elasticsearch
from storer import Store
import requests
import os


OUTPATH = '/Users/yixing/Documents/CS6200/Homework3/'
MAX_COUNT = 22000

class Crawler:
    '''
    This Crawler class will implement crawling the website, get the text the links in page
    '''

    def __init__(self):
        self.frontier = Frontier()
        self.count = 0
        self.last_domain = ''
        self.store = Store()

    def crawl(self):
        '''
        pop a url from frontier and get the header, html, text and out links and push the out links
        into frontier and insert them into elasticsearch
        :return: None
        '''
        while True and self.count < MAX_COUNT:
            url = self.frontier.pop_url()

            try:
                current_domain = urlparse(url).netloc

                if current_domain not in self.frontier.robot_dict and self.frontier.no_robot:
                    self.frontier.add_robot_dict(url)

                if current_domain in self.frontier.robot_dict and not (self.frontier.robot_dict[current_domain].can_fetch('*', url)):
                    continue

            except Exception, e:
                print 'current_domain_exception'.format(e)
                continue

            print 'current url {}'.format(url)

            if current_domain == self.last_domain:
                time.sleep(1)
            else:
                self.last_domain = current_domain

            try:
                header, raw_html = self.downloader(url)
            except Exception, e:
                print 'downloader exception'.format(e)
                continue

            try:
                text, title, links = self.parse_url(url, raw_html)
            except Exception, e:
                print e
                continue

            if text or links:
                self.count += 1
                self.push_links_to_frontier(url, links)

                print 'FINISHED: {}'.format(self.count)

                self.store.insert(self.count, url, header, title, text, raw_html, links)

                print 'PQ len: {}'.format(len(self.frontier.pq))

                self.write_to_file(url)
            else:
                continue

    def downloader(self,url):
        '''
        get the response of the url, only keep the page language is english and has text
        :param url: response url
        :return: header, raw html
        '''
        try:
            response = urllib2.urlopen(url, timeout=3)
            # response = requests.get(url, timeout=3)
        except Exception, e:
            print 'urlopen exception {} | {}'.format(url, e)
            raise Exception

        try:
            # code = response.status_code
            code = response.getcode()
            if code != 200:
                # print 'code != 200 {}'.format(url)
                raise Exception

            # header = response.headers
            header = response.info()
            if not header:
                # print 'header exception {}'.format(url)
                raise Exception

            if 'content-language' in header:
                if 'en' not in header['content-language']:
                    raise Exception

            if 'content-type' in header:
                if 'text' not in header['content-type']:
                    raise Exception

        except Exception, e:
            print e
            raise Exception

        try:
            # raw_html = response.text
            raw_html = response.read()
            raw_html = raw_html.decode('utf-8', 'ignore')
        except Exception, e:
            print 'raw_html {} | {}'.format(url, e)
            raise Exception
        return str(header), raw_html

    def parse_url(self, url, html):
        '''
        parse the html get it title, cleaned, text and canonicalized links
        :param url: url open the html
        :param html: parse html
        :return: text, title, links
        '''

        try:
            parser = etree.HTMLParser(target=ParserTarget(url), remove_blank_text=True, remove_comments=True)
            etree.HTML(html, parser=parser)
            text = ' '.join(parser.target.text_lines)
            title = parser.target.title
            links = parser.target.links
        except Exception, e:
            print e
            raise Exception
        return text, title, links

    def push_links_to_frontier(self, url, links):
        '''
        check and push every link in links list into frontier
        :param url: the parent url
        :param links: the out links in url page
        :return: None
        '''
        for link in links:
            try:
                self.frontier.check_push_url(link, url)
            except Exception, e:
                continue

    def write_to_file(self, url):
        output = OUTPATH + 'out_links.txt'
        if not os.path.exists(output):
            fh = open(output, "w")
        else:
            fh = open(output, "a")
        # fh.write('%s\n'%'<DOC>')
        fh.write('%s\n'%('<DOCNO>' + url + '</DOCNO>'))
        # fh.write('%s\n'%url)
        # fh.write('%s\n'%'<OUT-LINKS>')
        # for link in links:
        #     fh.write('%s\n'%link)
        # fh.write('%s\n'%'</OUT-LINKS>')
        # fh.write('%s\n'%'</DOC>')
        fh.close()


    def initial_seeds(self):
        self.frontier.initial_queue()

def main():
    c = Crawler()
    c.initial_seeds()
    c.crawl()



if __name__ == '__main__':
    main()