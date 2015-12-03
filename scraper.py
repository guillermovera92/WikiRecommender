from wikiapi import WikiApi
from bs4 import BeautifulSoup
from Queue import Queue
import re

class Scraper:

    prohibited_headers = set(['Contents', 'See also', 'References'])

    def __init__(self):
        self.wiki = WikiApi()

    def scrape(self, start_url, max):
        finished = set()
        queue = Queue()
        pages = []
        queue.put(start_url)

        for i in range(max):
            if queue.empty():
                break
            current_url = queue.get()
            (page, urls) = self.process_page(current_url)
            finished.add(current_url)
            pages.append(page)
            for u in urls:
                if u not in finished:
                    queue.put(u)
        return pages
        
    def process_page(self, url):
        html = self.wiki.get(url)

        soup = BeautifulSoup(html)
        body_html = soup.find(id='mw-content-text')
        title = soup.find(id='firstHeading').string

        urls = self.find_urls(body_html)
        (clean_text, headers) = self.clean_html(body_html)
        page = Page(url, title, clean_text, headers)
        return (page, urls)

    def find_urls(self, html):
        link_list = []
        good_link = re.compile('/wiki/*')
        bad_link = re.compile('.*:.*|.*\..*')
        for l in html.find_all('a'):
            link = l.get('href')
            if good_link.match(link) and not bad_link.match(link):
                link_list.append('https://en.wikipedia.org' + link)
        return link_list


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
            array[i] = re.sub(r'\[\d\]', '', str(array[i]))
        return array


class Page:

    def __init__(self, url, name, body, headers):
        self.url = url
        self.name = name
        self.body = body
        self.headers = headers

    def print_info(self):
        print "==== Page info. ===="
        print 'URL: ' + self.url
        print 'Name: ' + self.name
        print 'Body sample: ' + self.body[0:100] + '...'
        print 'Headers: ' + ', '.join(self.headers)
        print "====================\n"



if __name__ == "__main__":
    scraper = Scraper()
    results = scraper.scrape("https://en.wikipedia.org/wiki/Bleep_censor", 10)
    print 'Scraped ' + str(len(results)) + ' pages'
    for page in results:
        page.print_info()
