# Simple page object that contains all relevant information for the recommender
# about a page in Wikipedia
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