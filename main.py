#!/opt/local/bin/python2.5
# -*- coding:utf-8 -*-
import sys
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template
from google.appengine.api.labs import taskqueue
from google.appengine.ext import db

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
from database import Chain

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'views')

def get_path(filename):
    return os.path.join(TEMPLATE_DIR, filename)


class ShowHandler(webapp.RequestHandler):
    path = get_path('show.html')
    def get(self):
        m = MarkovChains()
        m.load_db('gquery2')
        word = self.request.get('word', default_value=None)
        text = m.db.fetch_new_sentence()
        taskqueue.add(url='/task/talk')
        values = {'text': text}
        self.response.out.write(template.render(self.path, values))


class TalkHandler(webapp.RequestHandler):
    path = get_path('talk.html')
    def get(self):
        self.response.out.write(template.render(self.path, {}))

    def post(self):
        if self.request.get('sentences'):
            text = self.request.get('sentences')
            m = MarkovChains()
            m.analyze_sentence(text)
            word = self.request.get('word', default_value=None)
            result = m.make_sentence(word=word)
            _chaindic = m.chaindic
            chaindic = []
            for prewords in _chaindic:
                for postword in _chaindic[prewords]:
                    if _chaindic[prewords][postword].isstart:
                        chaindic.append((prewords[0],prewords[1],postword)) 
            values = {'result':result, 'chaindic':chaindic, 'original':text}
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
        m.load_db('gquery2')
        m.db.store_sentence(text)
        values = {}
        self.response.out.write(template.render(self.path, values))


class LearnTask(webapp.RequestHandler):
    def post(self):
        text = self.request.get('sentences')
        user = self.request.get('user')
        m = MarkovChains()
        m.load_db('gquery2')
        m.db.store_sentence(text)


class ApiSentenceHandler(webapp.RequestHandler):
    path = get_path('sentence.xml')
    def post(self):
        if self.request.get('sentences'):
            text = self.request.get('sentences')
            m = MarkovChains()
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


class ApiDbSentenceLearnTask(webapp.RequestHandler):
    def post(self):
        text = self.request.get('sentences')
        user = self.request.get('user', default_value=None)
        m = MarkovChains()
        m.load_db('gquery2')
        m.db.store_sentence(text)


class ApiDbSentenceTalkTask(webapp.RequestHandler):
    def get(self):
        m = MarkovChains()
        m.load_db('gquery2')
        m.db.store_new_sentence()

    def post(self):
        m = MarkovChains()
        m.load_db('gquery2')
        m.db.store_new_sentence()


class ApiDbSentenceHandler(webapp.RequestHandler):
    def get(self):
        filename = os.path.join('db','sentence_get.xml')
        path = get_path(filename)
        m = MarkovChains()
        m.load_db('gquery2')
        word = self.request.get('first_word', default_value=None)
        user = self.request.get('user', default_value=None)
        text = m.db.fetch_new_sentence()
        taskqueue.add(url='/task/talk')
        values = {'text': text}
        self.response.headers['Content-Type'] = 'text/xml'
        self.response.out.write(template.render(path, values))

    def post(self):
        filename = os.path.join('db','sentence_post.xml')
        path = get_path(filename)
        text = self.request.get('sentences')
        user = self.request.get('user', default_value=None)
        taskqueue.add(url='/task/learn', 
                params={'sentences': text, 'user': user})
        self.response.headers['Content-Type'] = 'text/xml'
        self.response.out.write(template.render(path, {}))


class ApiDbUserHandler(webapp.RequestHandler):
    filename = os.path.join('os', 'user.xml')
    path = get_path(filename)
    def get(self):
        m = MarkovChains()
        m.load_db('gquery2')
        users = m.db.get_users()
        values = {'users': users}
        self.response.headers['Content-Type'] = 'text/xml'
        self.response.out.write(template.render(self.path, values))


class DeleteHandler(webapp.RequestHandler):
    def get(self):
        from google.appengine.api import memcache
        memcache.flush_all()


def main():
#def real_main():
    application = webapp.WSGIApplication([
        ('/', TalkHandler),
        ('/learn', LearnHandler),
        ('/show', ShowHandler),
        ('/api/sentence', ApiSentenceHandler),
        ('/api/db/sentence', ApiDbSentenceHandler),
        ('/api/db/users', ApiDbUserHandler),
        ('/task/learn', ApiDbSentenceLearnTask),
        ('/task/talk', ApiDbSentenceTalkTask),
        ('/delete', DeleteHandler),
        ], debug=False)
    util.run_wsgi_app(application)

def profile_main():
    import cProfile, pstats, StringIO, logging

    prof = cProfile.Profile().runctx("real_main()", globals(), locals())

    stream = StringIO.StringIO()
    stats = pstats.Stats(prof, stream=stream).strip_dirs()
    stats.sort_stats("cumulative")
    stats.print_stats('from*')
    logging.info("Profile data:\n%s", stream.getvalue())


if __name__ == '__main__':
    main()
    #profile_main()
