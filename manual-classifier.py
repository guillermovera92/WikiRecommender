#!/usr/bin/python
import json
import sys

# This scrip was used to manually classify Wikipedia articles to use them as a training
# set for the classifier. The pages have already been downloaded and stored as JSON.
# This script will add a true/false field that contains the result of the manual
# classification.
def classify(s, n):
    json_ = json.load(open('wikidb.json'))
    json_ = json_[s:n]
    for i in range(s, n):
        print '>>> ' + json_[i]['name']
        ins = str(raw_input('Is this good? '))
        while True:
            if ins == 'y':
                json_[i]['is_good'] = True
                break
            elif ins == 'n':
                json_[i]['is_good'] = False
                break
            elif ins == 'u':
                print '\tURL: ' + json_[i]['url']
                ins = str(raw_input('Is this good? '))
            elif ins == 'h':
                print '\tHeaders: '
                for h in json_[i]['headers']:
                    print '\t\t' + h
                if len(json_[i]['headers']):
                    print '\t\tNo headers'
                ins = str(raw_input('Is this good? '))
            elif ins == 'f':
                body = json_[i]['body'].split('.')
                print '\tFirst line: \n\t\t' + body[0]
                ins = str(raw_input('Is this good? '))
            else:
                ins = str(raw_input('(options: y, n, f, h, u) '))
        print '\n========================'
    output_file = open('wiki-classified-G-' + str(s) + '-' + str(n) + '.json', mode='w')
    output_file.write(json.dumps(json_))
    # print type(json_)



if __name__ == '__main__':
    print 'Instructions'
    print 'y for a good recommendation, n for a bad one'
    print 'u for the url, h for the headers, f for the first line of the body'
    classify(int(sys.argv[1]), int(sys.argv[2]))
