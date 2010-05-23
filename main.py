#!/opt/local/bin/python2.5
# -*- coding:utf-8 -*-
import sys
import os
from site import addsitedir

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template

"""
文字コードの設定
"""
stdin = sys.stdin
stdout = sys.stdout
reload(sys)
sys.setdefaultencoding('utf-8')
sys.stdin = stdin
sys.stdout = stdout

"""
自作モジュールの path 設定
"""
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))


from markovchains import MarkovChains

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'views')

def get_path(filename):
    return os.path.join(TEMPLATE_DIR, filename)


class ShowHandler(webapp.RequestHandler):
    path = get_path('show.html')
    def get(self):
        m = MarkovChains('gquery')
        m.load_db('gquery')
        word = self.request.get('word', default_value=None)
        text = m.db.make_sentence(word=word)
        values = {'text': text}
        self.response.out.write(template.render(self.path, values))


class TalkHandler(webapp.RequestHandler):
    path = get_path('talk.html')
    def get(self):
        self.response.out.write(template.render(self.path, {}))

    def post(self):
        if self.request.get('sentences'):
            text = self.request.get('sentences')
            m = MarkovChains('gquery')
            m.analyze_sentence(text)
            word = self.request.get('word', default_value=None)
            result = m.make_sentence(word=word)
            values = {'result':result}
            self.response.out.write(template.render(self.path, values))
        else:
            values = {'result':''}
            self.response.out.write(template.render(self.path, values))


class LearnHandler(webapp.RequestHandler):
    path = get_path('learn.html')
    def get(self):
        m = MarkovChains()
        m.load_db('gquery')
        user = self.request.get('user', default_value=None)
        if user:
            chains = m.db.uchain.all()
        else:
            chains = m.db.chain.all()
        values = {'chains': chains}
        self.response.out.write(template.render(self.path, values))

    def post(self):
        text = self.request.get('sentences')
        user = self.request.get('user', default_value=None)
        m = MarkovChains()
        m.analyze_sentence(text, user=user)
        m.load_db('gquery')
        m.register_data()
        if user:
            chains = m.db.uchain.all()
        else:
            chains = m.db.chain.all()
        values = {'chains': chains}
        self.response.out.write(template.render(self.path, values))


class ApiSentenceHandler(webapp.RequestHandler):
    path = get_path('sentence.xml')
    def post(self):
        if self.request.get('sentences'):
            text = self.request.get('sentences')
            m = MarkovChains('gquery')
            m.analyze_sentence(text)
            word = self.request.get('first_word', default_value=None)
            result = m.make_sentence(word=word)
            values = {'result':result}
            self.response.headers['Content-Type'] = 'text/xml'
            self.response.out.write(template.render(self.path, values))
        else:
            values = {'result':''}
            self.response.headers['Content-Type'] = 'text/xml'
            self.response.out.write(template.render(self.path, values))


class ApiDbSentenceHandler(webapp.RequestHandler):
    def get(self):
        filename = os.path.join('db','sentence_get.xml')
        path = get_path(filename)
        m = MarkovChains('gquery')
        m.load_db('gquery')
        word = self.request.get('first_word', default_value=None)
        user = self.request.get('user', default_value=None)
        text = m.db.make_sentence(word=word, user=user)
        values = {'text': text}
        self.response.headers['Content-Type'] = 'text/xml'
        self.response.out.write(template.render(path, values))

    def post(self):
        filename = os.path.join('db','sentence_post.xml')
        path = get_path(filename)
        text = self.request.get('sentences')
        user = self.request.get('user', default_value=None)
        m = MarkovChains()
        m.analyze_sentence(text, user=user)
        m.load_db('gquery')
        m.register_data()
        self.response.headers['Content-Type'] = 'text/xml'
        self.response.out.write(template.render(path, {}))


class ApiDbUserHandler(webapp.RequestHandler):
    filename = os.path.join('os', 'user.xml')
    path = get_path(filename)
    def get(self):
        m = MarkovChains('gquery')
        m.load_db('gquery')
        users = m.db.get_users()
        values = {'users': users}
        self.response.headers['Content-Type'] = 'text/xml'
        self.response.out.write(template.render(self.path, values))


def main():
    application = webapp.WSGIApplication([
        ('/', TalkHandler),
        ('/learn', LearnHandler),
        ('/show', ShowHandler),
        ('/api/sentence', ApiSentenceHandler),
        ('/api/db/sentence', ApiDbSentenceHandler),
        ('/api/db/users', ApiDbUserHandler),
        ], debug=False)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
