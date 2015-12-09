import json
from scraper import Scraper
import sys
import re
import time


def build_db(starting_query, max_articles, file_name):
	db = open(file_name, mode='w+')
	scraper = Scraper()
	count = 0
	db.write('[')
	for page in scraper.stream(starting_query, max_articles):
		print 'page #%5d: %s' % (count+1, page.name)
		count += 1
		db.write(page.to_json())
		if count == max_articles:
			db.write(']')
		else:
			db.write(',')

	db.close()

if __name__ == '__main__':
	if len(sys.argv) != 4:
		print "Usage:"
		print "python wiki-db-build.py [start search string] [max links] [output file name]"
	else:
		file_name = sys.argv[3]
		if file_name[-5:] != '.json':
			file_name += '.json'
		start = time.time()
		build_db(sys.argv[1], int(sys.argv[2]), file_name)
		end = time.time()
		print 'scrapped %d pages in %.2f seconds' % (int(sys.argv[2]), end-start)
	