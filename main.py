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

from markovchains import MarkovChains


class TalkHandler(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'talk.html')
        self.response.out.write(template.render(path, {}))

    def post(self):
        path = os.path.join(os.path.dirname(__file__), 'talk.html')
        if self.request.get('sentences'):
            text = self.request.get('sentences')
            m = MarkovChains('gquery')
            m.analyze_sentence(text)
            result = m.make_sentence()
            values = {'result':result}
            self.response.out.write(template.render(path, values))
        else:
            values = {'result':''}
            self.response.out.write(template.render(path, values))


class LearnHandler(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'learn.html')
        m = MarkovChains()
        m.load_db('gquery')
        chains = m.db.get_allchain()
        values = {'chains': chains}
        self.response.out.write(template.render(path, values))

    def post(self):
        path = os.path.join(os.path.dirname(__file__), 'learn.html')
        text = self.request.get('sentences')
        m = MarkovChains()
        m.analyze_sentence(text)
        m.load_db('gquery')
        m.register_data()
        chains = m.db.chain.all()
        values = {'chains': chains}
        self.response.out.write(template.render(path, values))
        

def main():
    application = webapp.WSGIApplication([
        ('/', TalkHandler),
        ('/learn', LearnHandler),
        ], debug=False)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
