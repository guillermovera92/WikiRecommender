#!/usr/bin/python
from wikiapi import WikiApi
from bs4 import BeautifulSoup
from Queue import Queue
import re
import time
from collections import defaultdict as dd
import json
import classifier 
from page import Page
import sys

# This class scrapes Wikipedia using the wikiapi https://github.com/richardasaurus/wiki-api
class Scraper:

    prohibited_headers = set(['Contents', 'See also', 'References'])

    # The scraper uses the classifier to only send out articles that are more likely to
    # be music related
    def __init__(self):
        self.classifier = classifier.Classifier()
        self.wiki = WikiApi()
        self.bad_urls = set([p['url'] for p in self.classifier.non_accepted_pages])

    # The stream method is used for scraping a large number of maximum links.
    # This method does not implement the classifier filtering because its main
    # purpose is for building the database of pages for manual classification
    def stream(self, start_term, maxLinks):
        finished, queue, search_results = self.scrape_common(start_term)

        for i in range(maxLinks):
            if queue.empty():
                break
            current_url = queue.get()
            while current_url in finished:
                current_url = queue.get()
            (page, urls) = self.process_page(current_url)
            finished.add(current_url)
            for u in urls:
                queue.put(u)
            yield page

    # The scrape method is used for a smaller number of maximum links. It performs
    # a breadth first search given an initial term. It uses a queue to keep track
    # of the pages to be scraped and a set of the already scraped to prevent 
    # duplicates
    def scrape(self, start_term, maxLinks):
        finished, queue, search_results = self.scrape_common(start_term)
        pages = []

        while len(pages) < maxLinks:
            if queue.empty():
                break
            current_url = queue.get()
            while current_url in finished:
                current_url = queue.get()
            (page, urls) = self.process_page(current_url)
            finished.add(current_url)

            # Only if the classifier predicts it as a good page, a page will
            # be added to the pages list which is returned at the end
            if self.classifier.classify(page) == 1 and page.url not in self.bad_urls:
                pages.append(page)
                print page.name
            for u in urls:
                queue.put(u)
        return pages

    # Common code for both methods that crawl wikipedia
    def scrape_common(self, start_term):
        finished = set()
        queue = Queue()
        search_results = self.wiki.find(start_term)
        if not search_results:
            print 'No pages found. Try a different term'
        else:
            queue.put('https://en.wikipedia.org/wiki/' + search_results[0])
        return finished, queue, search_results

    # Process a page's HTML using BeautifulSoup to extract useful information
    def process_page(self, url):
        html = self.wiki.get(url)

        soup = BeautifulSoup(html)
        body_html = soup.find(id='mw-content-text')
        title_tag = soup.find(id='firstHeading')
        if title_tag.string == None:
            contents = title_tag.contents
            string_contents = []
            for c in contents:
                if type(c) != str:
                    string_contents.append(c.string)
                else:
                    string_contents.append(c)
            title = ''.join(string_contents)
        else:
            title = title_tag.string

        urls, links_text, media_link_count = self.find_urls(body_html)
        (clean_text, headers) = self.clean_html(body_html)
        page = Page(url, title, clean_text, headers, links_text, media_link_count)
        return (page, urls)

    # Find all URLs in a given HTML that redirect to another article in Wikipedia
    # Page links and media links (pictures, audio) are stored in different lists
    # but are both used.
    def find_urls(self, html):
        link_urls = []
        good_link = re.compile('/wiki/')
        bad_link = re.compile('.*:.*|.*\..*|.*\(disambiguation\)')
        media_link = re.compile('.*\.jpg|.*\.ogg')
        media_link_count = 0
        media_found = set()
        links_text = dd(int)

        all_links = html.find_all('a')
        for l in all_links:
            link = l.get('href')
            content = self.extract_content([l])[0]
            if good_link.match(link) and not bad_link.match(link):
                link_urls.append('https://en.wikipedia.org' + link)

                if str(content) != '':
                    links_text[content] = links_text[content] + 1

            elif media_link.match(link):
                if link not in media_found:
                    media_link_count += 1
                    media_found.add(link)

                if str(content) != '':
                    links_text[content] = links_text[content] + 1

        return (link_urls, links_text, media_link_count)

    # Fucntion to extract the body and the headers of an article
    def clean_html(self, html):
        paragraphs = html.find_all('p')
        headers = html.find_all(re.compile('h\d'))
        clean_text = ''.join(self.extract_content(paragraphs))
        headers_list = self.clean_headers(headers)
        return (clean_text, headers_list)

    # Clean the list of headers of the prohibited, common headers
    def clean_headers(self, array):
        raw_headers = self.extract_content(array)
        final_headers = []
        for h in raw_headers:
            if h not in Scraper.prohibited_headers:
                final_headers.append(h)
        return final_headers

    # Fuction to clean the HTML body of a page. It removes common links that 
    # would cause noise in our system such as [edit] buttons and reference numbers
    # e.g. [2]. 
    def extract_content(self, array):
        for i in range(len(array)):
            array[i] = re.sub(r'<[^>]*>', '', str(array[i]))
            array[i] = re.sub(r'\[edit\]', '', str(array[i]))
            array[i] = re.sub(r'\[\d*\]', '', str(array[i]))
            array[i] = re.sub(r'\^', '', str(array[i]))
        return array

# If ran as main, this script will scrape wikipedia starting with Lady Gaga
# and it will try to find 10 links that are music related, starting 
if __name__ == "__main__":
    scraper = Scraper()
    start = time.time()
    results = scraper.scrape(sys.argv[1], int(sys.argv[2]))
    end = time.time()
    total_time = end - start
    print 'Scraped ' + str(len(results)) + ' pages in ' + str(total_time) + ' seconds'
    for page in results:
        page.print_info()
        page.to_json()
