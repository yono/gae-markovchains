#!/opt/local/bin/python2.5
# -*- coding:utf-8 -*-

import sys
stdin = sys.stdin
stdout = sys.stdout
reload(sys)
sys.setdefaultencoding('utf-8')
sys.stdin = stdin
sys.stdout = stdout

import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template
from google.appengine.ext import db

import wakati
import extractword
from markovchains import MarkovChains

class ChainNode(db.Model):
    preword1 = db.StringProperty()
    preword2 = db.StringProperty()
    postword = db.StringProperty()
    count = db.IntegerProperty()

# 受け取ったデータを分解してマルコフに使える形に
class TalkHandler(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'talk.html')
        self.response.out.write(template.render(path, {}))

    def post(self):
        path = os.path.join(os.path.dirname(__file__), 'talk.html')
        if self.request.get('sentences'):
            m = MarkovChains()
            text = self.request.get('sentences')
            m.analyze_sentence(text)
            result = m.make_sentence()
            values = {'result':result}
            self.response.out.write(template.render(path, values))
        else:
            values = {'result':''}
            self.response.out.write(template.render(path, values))
        

def main():
    application = webapp.WSGIApplication([
        ('/', TalkHandler),
        ], debug=False)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
