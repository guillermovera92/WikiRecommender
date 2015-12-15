#!/usr/bin/python
import os
import json
from math import log
from sklearn import tree
from sklearn import cross_validation
from sklearn import svm
import numpy as np
from page import Page
import re
import random


class Classifier():

    def __init__(self):
        self.word_list = self.make_music_words()
        self.page_names = set()
        self.accepted_pages = []
        self.non_accepted_pages = []
        self.load_files()
        self.build_page_sets()
        self.labels, self.features = self.build_matrices()
        self.classifier = self.make_classifier()

    # Load mannually classfied pages to train and test classifier
    def load_files(self):
        os.chdir('./classified')
        for f_name in os.listdir(os.getcwd()):
            if f_name.endswith(".json"): 
                current_file = json.load(open(f_name))
                for page in current_file:
                    if page['name'] not in self.page_names:
                        self.page_names.add(page['name'])
                        if page['is_good']:
                            self.accepted_pages.append(page)
                        elif not page['is_good']:
                            self.non_accepted_pages.append(page)
        print 'Scanned pages: %d' % len(self.page_names)
        print 'Good pages: %d. Bad pages: %d' % (len(self.accepted_pages), len(self.non_accepted_pages))
        os.chdir('..')

    # Create the accepted and non accepted sets of pages with the manually classified data
    def build_page_sets(self):
        if len(self.accepted_pages) < len(self.non_accepted_pages):
            random.shuffle(self.non_accepted_pages)
            self.non_accepted_pages = self.non_accepted_pages[0:len(self.accepted_pages)]
        else:
            random.shuffle(self.accepted_pages)
            self.accepted_pages = self.accepted_pages[:len(self.non_accepted_pages)]
        print "Reduced page set: accepted = %d, non accpeted = %d\n" % (len(self.accepted_pages), len(self.non_accepted_pages))

    # Using the accepted and non accepted pages, build the X and Y matrices for the
    # classifier. The labels are weather the page is a good recommendation or not 
    # (the manual classification) and the features are:
    # - Number of Wikipedia links in the article
    # - Length of the body of the article
    # - Number of media links in the article (pictures, audio files, etc)
    # - Count of music related words (based on the music-words.txt file)
    # - Precense or absense of a set of keywords based on a regex (see below)
    def build_matrices(self):
        labels = [1] * len(self.accepted_pages) + [0] * len(self.non_accepted_pages)
        features = []
        music_words = self.word_list
        for p in self.accepted_pages + self.non_accepted_pages:
            link_map = p['links']
            n_links = sum(link_map.itervalues())
            media_count = p['audio_image_count']
            music_words_count = self.count_words(p['body'], music_words)
            regex_res = self.regex(p['body'].split('.')[0])
            features.append([len(p['body'].split()), n_links, media_count, music_words_count, regex_res])
        return labels, features

    # Create classifier from sklearn
    def make_classifier(self):
        tree_model = tree.DecisionTreeClassifier(max_depth=3)
        tree_model.fit(self.features, self.labels)
        return tree_model   

    # Helper function to cound the number of words that match words in music-words.txt
    def count_words(self, body, words):
        tokens = body.split()
        return len([w for w in tokens if w.strip().lower() in words])

    # Read music-words.txt file
    def make_music_words(self):
        f = open('music-words.txt')
        return set(line.strip().lower() for line in f if not line.startswith(';') and line.strip())

    # Fucntion to classify pages that are not given in the training set. This is the function
    # used by Scraper to clean the set of pages before passing it to the recommender
    def classify(self, page):
        body = page.body
        n_links = sum(page.links.itervalues())
        media_count = page.audio_image_count
        music_words_count = self.count_words(body, self.word_list)
        regex_res = self.regex(body.split('.')[0])
        return self.classifier.predict([log(len(body)), n_links, media_count, music_words_count, regex_res])

    # Simple regex function that matches one of these words (singer|songwriter|album|song|EP|musician|performer)
    # preceeded by 'is a' in the body of an article
    def regex(self, line):
        obj = re.match(r'.*is a[^\\.]*(singer|songwriter|album|song|EP|musician|performer).*', line, re.I)
        if obj != None:
            return 0
        else:
            return 1

# Running this scrip as main will create and test a classifier with the trainind data set
# This will print some information that is not available when running the recommender
# such as the precision and the accuracy of our model
if __name__ == '__main__':
    classifier = Classifier()
    tree_model = classifier.classifier
    X = classifier.features
    Y = classifier.labels
    accuracy = cross_validation.cross_val_score(tree_model, X, Y, scoring='accuracy') # avg. ~73%
    precision = cross_validation.cross_val_score(tree_model, X, Y, scoring='precision') # ~74%
    print 'Correlation accuracy (3 runs): ', accuracy
    print 'Correlation precision average: ', np.mean(accuracy), '\n'
    