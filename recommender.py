#!/usr/bin/python
import re
from collections import defaultdict
from math import log
from scipy import spatial
import scraper


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

# From here do cosine similarity...
def calculate_cosine_similarity(docs):
    seed_article = docs[0]
    docs = docs[1:]
    cosine_similarities = defaultdict(float)
    for doc in docs:
        A, B = [], []
        for word in seed_article.frequency_vector:
            if word in doc.frequency_vector:
                A.append(seed_article.frequency_vector[word])
                B.append(doc.frequency_vector[word])
        cosine_similarity = 1 - spatial.distance.cosine(A, B)
        cosine_similarities[doc] = round(cosine_similarity, 4) # Rounding to 5 sig figs
    return cosine_similarities

# Calculate top pages
def calcualte_recommendations(cosine_similarities):
    cos_similarity_to_doc = {v: k for k, v in cosine_similarities.items()}
    recommended_docs = []
    for freq in reversed(sorted(cos_similarity_to_doc.keys())):
        recommended_docs.append(cos_similarity_to_doc[freq].name)
    return recommended_docs

def user_input():
    seed = str(raw_input('Please enter an artist or song you like: '))
    article_num = ''
    while not article_num.isdigit():
        article_num = raw_input('\nPlease enter the number of articles you would like to scan\n' + 
            '(20 is fast but less exhaustive, 100 is slow but more exhaustive): ')
        if not article_num.isdigit():
            print '\n>>> Please enter a whole number'
    
    print '\n+-------------+'
    print '| Scanning... |'
    print '+-------------+\n'
    return seed, int(article_num)


if __name__ == '__main__':
    print '+-------------------------------------------------------+'
    print '| Welcome to the WikiRecommender: A Texty New Approach! |'
    print '+-------------------------------------------------------+\n'
    print 'Setting up the classifier...'
    scrp = scraper.Scraper()

    all_articles = []
    
    while len(all_articles) == 0:
        seed, article_num = user_input()
        all_articles = scrp.scrape(seed, article_num)
    

    cleaned_articles = all_articles
    generate_frequency_vectors(cleaned_articles, words_set, calc_doc_counts(cleaned_articles, words_set))
    recommendations = calcualte_recommendations(calculate_cosine_similarity(cleaned_articles))
    print "\n+-----------------+"
    print "| Recommendations |"
    print "+-----------------+\n"
    for doc in recommendations:
        print doc
