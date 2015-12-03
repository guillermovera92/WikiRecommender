#!/usr/bin/python
import re

def create_cleaned_set(articles):
    out = []
    for article in articles:
        obj = re.match(r'.*is a[^\\.]*(singer|songwriter|album|song|record|musician|performer).*', article, re.I)
        if obj != None:
            out.append(article)
    return out

all_articles = [] # This will hook into Guillermo's code

cleanedArticles = create_cleaned_set(all_articles)





def get_freq_words(filename='words.txt'):
    for line in open(filename):
        words = line.split()
        return set(words)

words_set = get_freq_words()
