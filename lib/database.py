#!/usr/bin/env python
# -*- coding:utf-8 -*-
from google.appengine.ext import db
import random
import re
import sys
import copy
import time
import sys

from extractword import Sentence


class User(db.Model):
    name = db.StringProperty()


class Chain(db.Model):
    preword1 = db.StringProperty()
    preword2 = db.StringProperty()
    postword = db.StringProperty()
    count = db.IntegerProperty()
    isstart = db.BooleanProperty()


class UserChain(db.Model):
    preword1 = db.StringProperty()
    preword2 = db.StringProperty()
    postword = db.StringProperty()
    user = db.ReferenceProperty(User)
    count = db.IntegerProperty()
    isstart = db.BooleanProperty()


class Word(object):

    def __init__(self, word, count):
        self.name = word
        self.count = count


class Database(object):

    @classmethod
    def create(cls, dbkind, dbname='default'):
        if dbkind == 'gquery':
            return GQuery(dbname)
        elif dbkind == 'gquery2':
            return GQuery2(dbname)


class GQuery2(object):

    punctuations = {u'。':0, u'．':0, u'？':0, u'！':0, u'!':0, u'?':0,
                    u'ｗ':0, u'…':0}

    ps = None

    def __init__(self, dbname):
        if db:
            self.s = Sentence()
            pass
        else:
            raise BaseException

    def load_db(self):
        self.chain = Chain
        self.uchain = UserChain

    def _split_sentences(self, text):
        if self.ps is None:
            self.ps = re.compile(u'[%s]' %\
                    ('|'.join(self.punctuations.keys())))   
        return self.ps.split(text)


    def _get_kname(self, words):
        knames = []
        for i in xrange(len(words)):
            if words[i] == ' ':
                knames.append('<SPACE>')
            else:
                knames.append(words[i])
        kname = "id" + '__'.join(knames)
        return kname


    def store_sentence(self, _text):
        sentences = self._split_sentences(_text)
        text = u'%s。' % (sentences[0])
        for i in xrange(1, len(sentences)):
            if len(u'%s%s。' % (text, sentences[i])) < 400:
                text = u'%s%s。' % (text, sentences[i])
            else:
                self.s.analysis_text(text)
                words = self.s.get_words()
                isstart = False
                tmp_words = []
                isstart = False
                for j in xrange(len(words)):
                    if len(tmp_words) == 3:
                        if j == 0 or\
                            (j > 0 and words[j-1] in self.punctuations):
                            isstart = True
                        else:
                            isstart = False
                        kname = self._get_kname(tmp_words)
                        obj = db.get(db.Key.from_path("Chain", kname))
                        if not obj:
                            obj = Chain(key_name = kname, 
                                        preword1 = tmp_words[0],
                                        preword2 = tmp_words[1],
                                        postword = tmp_words[2],
                                        count = 1,
                                        isstart = isstart)
                        else:
                            obj.count += 1
                            obj.isstart = obj.isstart or isstart
                        obj.put()
                        
                        tmp_words.pop(0)
                    else:
                        pass
                    tmp_words.append(words[j])


class GQuery(object):
 
    def __init__(self, dbname):
        if db:
            pass
        else:
            raise BaseException

    def load_db(self):
        self.chain = Chain
        self.uchain = UserChain

    """
    データ挿入 & 更新
    """
    def update_chain(self, _chain):
        chains = Chain.gql("WHERE preword1 = :1 and preword2 = :2 and "
                           "postword = :3 limit 1", _chain[0], _chain[1],
                                                    _chain[2])
        chain = chains.get()
        chain.count += _chain[3]
        chain.isstart = chain.isstart or _chain[4]
        chain.put()

    def insert_chain(self, _chain):
        chain = Chain(preword1=_chain[0], preword2=_chain[1],
                      postword=_chain[2], count=_chain[3],
                      isstart=_chain[4])
        chain.put()

    def update_userchain(self, _chain):
        chains = UserChain.gql("WHERE preword1 = :1 and preword2 = :2 and "
                               "postword = :3 and user = :4 limit 1",
                               _chain[0], _chain[1], _chain[2], _chain[3])
        chain = chains.get()
        chain.count += _chain[4]
        chain.isstart = chain.isstart or _chain[5]
        chain.put()
    
    def insert_userchain(self, _chain):
        chain = UserChain(preword1=_chain[0], preword2=_chain[1],
                          postword=_chain[2], user=_chain[3],
                          count=_chain[4], isstart=_chain[5])
        chain.put()

    def update_user(self, _user):
        users = User.gql("WHERE name = :1", _user)
        user = users.get()
        if user is None:
            user = User(name=_user)
            user.put()
        return user
    
    """
    データ取得
    """
    def get_nextwords(self, words, user=None):
        if user:
            _user = User.gql("WHERE name = :1", user).get()
            chains = UserChain.gql("WHERE preword1 = :1 and preword2 = :2 "
                                   "and user = :3",
                                    words[1].name, words[2].name, _user)
        else:
            chains = Chain.gql("WHERE preword1 = :1 and preword2 = :2",
                              words[1].name, words[2].name)
        return chains.fetch(1000)

    def select_nextword(self, words):
        sum_count = sum([x.count for x in words])
        probs = []
        for word in words:
            probs.append(Word(word.postword, 0))
            probs[-1].count = float(probs[-1].count) / sum_count
        probs.sort(lambda x, y: cmp(x.count, y.count), reverse=True)
        randnum = random.random()
        sum_prob = 0
        nextword = ''
        for i in xrange(len(probs)):
            sum_prob += probs[i].count
            if randnum < sum_prob:
                nextword = words[i]
                break
        else:
            nextword = probs[-1]
        return nextword 

    def get_startword(self, user=None, word=None):
        if user:
            _user = User.gql("WHERE name = :1", user).get()
        if user and word:
            words = UserChain.gql("WHERE user = :1 and preword1 = :2", 
                                  _user, word)
        elif user and not word:     
            words = UserChain.gql("WHERE isstart = True and user = :1", 
                                    _user)
        elif not user and word:
            words = Chain.gql("WHERE preword1 = :1", word)
        else:
            words = Chain.gql("WHERE isstart = True")
        return random.choice(words.fetch(1000))

    def get_users(self):
        return User.all()

    def get_allchain(self):
        _chains = Chain.all()
        chains = {}
        for chain in _chains:
            chains[(chain.preword1, chain.preword2, chain.postword)] = chain
        return chains
    
    def get_userchain(self):
        _chains = UserChain.all()
        chains = {}
        for chain in _chains:
            chains[(chain.preword1, chain.preword2, chain.postword,
                    chain.user.key())] = chain
        return chains

    def make_sentence(self, user=None, word=None):
        minimum = 1
        maximum = 100
        punctuations = {u'。': 0, u'．': 0, u'？': 0, u'！': 0,
                           u'!': 0, u'?': 0, u'w': 0, u'…': 0,}

        chain = self.get_startword(user=user,word=word)
        words = [Word(chain.preword1, chain.count), 
                Word(chain.preword2, chain.count), 
                Word(chain.postword, chain.count)]
        sentence = copy.copy(words)

        count = 0
        while True:
            end_cond = (count > minimum) and (words[-1].name in punctuations)
            if end_cond:
                break
                
            if count > maximum:
                break

            nextwords = self.get_nextwords(words, user=user)
            if len(nextwords) == 0:
                break
            nextchain = self.select_nextword(nextwords)
            nextword = Word(nextchain.name, nextchain.count)
            sentence.append(nextword)
            words.pop(0)
            words.append(nextword)
            count += 1
        
        return ''.join([x.name for x in sentence])

    def _cond_word(self, word):
        if word:
            return ' and preword1 = :word'
        else:
            return ''
