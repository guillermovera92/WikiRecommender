#!/usr/bin/python
import re
from collections import defaultdict
from math import log

def create_cleaned_set(articles):
    out = []
    for article in articles:
        obj = re.match(r'.*is a[^\\.]*(singer|songwriter|album|song|record|musician|performer).*', article.body, re.I)
        if obj != None:
            out.append(article)
    return out

def get_freq_words(filename='words.txt'):
    for line in open(filename):
        words = line.split()
        return set(words)

words_set = get_freq_words()

def split(s):
    return re.split('\W+', s.lower())

def calc_doc_counts(docs, blacklist):
    doc_count = defaultdict(int)
    for d in docs:
        seen = set()
        words = split(d.body)
        for word in words:
            if word in seen or word in blacklist:
                continue
            seen.add(word)
            doc_count[word] += 1
    return doc_count

DOC_CONST = 0.5
def generate_frequency_vectors(docs, blacklist, doc_counts):
    def calc_TF_IDF(term, doc_words, term_counts):
        tf = term_counts[term] / float(len(doc_words))
        idf = log(len(docs) / doc_counts[term])
        return tf * (idf + DOC_CONST)

    for doc in docs:
        doc_words = split(doc.body)
        term_counts = defaultdict(int)
        for word in doc_words:
            term_counts[word] += 1

        # Create the vector using TF-IDF
        vector = {}
        for word, count in term_counts.iteritems():
            if word in blacklist:
                continue
            tfidf = calc_TF_IDF(word, doc_words, term_counts)
            vector[word] = tfidf
        doc.frequency_vector = vector

all_articles = [] # This will hook into Guillermo's code

cleaned_articles = create_cleaned_set(all_articles)
generate_frequency_vectors(cleaned_articles, words_set, calc_doc_counts(cleaned_articles, words_set))

# From here do cosine similarity...
