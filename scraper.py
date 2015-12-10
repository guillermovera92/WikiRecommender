from wikiapi import WikiApi
from bs4 import BeautifulSoup
from Queue import Queue
import re
import sys
import time
from collections import defaultdict as dd
import json

class Scraper:

    prohibited_headers = set(['Contents', 'See also', 'References'])

    def __init__(self):
        self.wiki = WikiApi()

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

    def scrape(self, start_term, maxLinks):
        finished, queue, search_results = self.scrape_common(start_term)
        pages = []

        for i in range(maxLinks):
            if queue.empty():
                break
            current_url = queue.get()
            while current_url in finished:
                current_url = queue.get()
            (page, urls) = self.process_page(current_url)
            finished.add(current_url)
            pages.append(page)
            for u in urls:
                queue.put(u)
        return pages

    def scrape_common(self, start_term):
        finished = set()
        queue = Queue()
        search_results = self.wiki.find(start_term)
        if not search_results:
            print 'No pages found. Try a different term'
        else:
            queue.put('https://en.wikipedia.org/wiki/' + search_results[0])
        return finished, queue, search_results

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


    def clean_html(self, html):
        paragraphs = html.find_all('p')
        headers = html.find_all(re.compile('h\d'))
        clean_text = ''.join(self.extract_content(paragraphs))
        headers_list = self.clean_headers(headers)
        return (clean_text, headers_list)

    def clean_headers(self, array):
        raw_headers = self.extract_content(array)
        final_headers = []
        for h in raw_headers:
            if h not in Scraper.prohibited_headers:
                final_headers.append(h)
        return final_headers

    def extract_content(self, array):
        for i in range(len(array)):
            array[i] = re.sub(r'<[^>]*>', '', str(array[i]))
            array[i] = re.sub(r'\[edit\]', '', str(array[i]))
            array[i] = re.sub(r'\[\d*\]', '', str(array[i]))
            array[i] = re.sub(r'\^', '', str(array[i]))

        return array


class Page:

    def __init__(self, url, name, body, headers, links, audio_image_count):
        self.url = url
        self.name = name
        self.body = body
        self.headers = headers
        self.links = links # Map of link_text -> count
        self.audio_image_count = audio_image_count

    def print_info(self):
        print "==== Page info. ===="
        print 'URL: ' + self.url
        print 'Name: ' + self.name
        print 'Body sample: ' + self.body[0:100] + '...'
        print 'Headers: ' + ', '.join(self.headers)
        print "====================\n"

    def to_json(self):
        return json.dumps(self.__dict__)


if __name__ == "__main__":
    scraper = Scraper()
    start = time.time()
    results = scraper.scrape("One Direction", int(sys.argv[1]))
    end = time.time()
    total_time = end - start
    print 'Scraped ' + str(len(results)) + ' pages in ' + str(total_time) + ' seconds'
    if len(sys.argv) >= 3 and (sys.argv[2] == 'true' or sys.argv[2] == 't'):
        for page in results:
            page.print_info()
            page.to_json()
