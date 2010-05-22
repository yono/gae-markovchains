#!/usr/bin/env python
# -*- coding:utf-8 -*-
from google.appengine.ext import db
import random
import sys


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
    user = db.StringProperty()
    count = db.IntegerProperty()
    isstart = db.BooleanProperty()


class Database(object):

    @classmethod
    def create(cls, dbkind, dbname='default'):
        if dbkind == 'gquery':
            return GQuery(dbname)


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
    
    """
    データ取得
    """
    def get_nextwords(self, words, user=None):
        if user:
            chains = UserChain.gql("WHERE preword1 = :1 and preword2 = :2 "
                                   "and user = :3",
                                    words[0], words[1], user)
        else:
            chains = Chain.gql("WHERE preword1 = :1 and preword2 = :2",
                              words[0], words[1])
        return chains


    def get_startword(self, user=None):
        if user:
            words = UserChain.gql("WHERE isstart = True and user = :1",user)
        else:     
            words = Chain.gql("WHERE isstart = True")
        return random.choice(words)

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
            chains[(chain.preword, chain.preword2, chain.postword,
                    chain.user)] = chain
        return chains

    def make_sentence(self, user=None, word=None):
        limit = 1
        punctuation_words = {u'。': 0, u'．': 0, u'？': 0, u'！': 0,
                           u'!': 0, u'?': 0, u'w': 0, u'…': 0,}


        chain = self.get_startword(user)
        words = [chain.prewords, chain.preword2, chain.postword]
        sentence = copy.copy(words)

        while True:
            enc_cond = (count > limit) and (words[-1].name in punctuations)
            if end_cond:
                break

            nextwords = self.get_nextwords(words)
            nextchain = self.select_nextword(nextwords)
            nextword = nextchain.postword 
            sentence.append(nextword)
            words.pop(0)
            words.append(nextword)
            count += 1
        
        return ''.join([x.name for x in sentence])
