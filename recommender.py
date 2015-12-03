#!/usr/bin/python
import re
from collections import defaultdict

def create_cleaned_set(articles):
    out = []
    for article in articles:
        obj = re.match(r'.*is a[^\\.]*(singer|songwriter|album|song|record|musician|performer).*', article.body, re.I)
        if obj != None:
            out.append(article)
    return out

def calc_doc_counts(docs):
    def split(s):
        return re.split('\W+', s.lower())
        
    doc_count = defaultdict(int)
    for d in docs:
        seen = set()
        words = split(d.body)
        for word in words:
            if word in seen:
                continue
            seen.add(word)
            doc_count[word] += 1
    return doc_count

def generate_frequency_vector(a, b, blacklist):

all_articles = [] # This will hook into Guillermo's code

cleanedArticles = create_cleaned_set(all_articles)