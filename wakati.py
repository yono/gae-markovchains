#!/usr/bin/env python
# -*- coding: utf-8 -*-
from xml.parsers.expat import ParserCreate
import yahoowakati

class Wakati(object):
    def __init__(self):
        self.p = ParserCreate()
        self.p.buffer_text = True
        self.p.StartElementHandler = self.start_element
        self.p.EndElementHandler = self.end_element
        self.p.CharacterDataHandler = self.char_data
        self.words = []

    def start_element(self, name, attrs):
        global flag
        flag = False
        if name == "Surface":
            flag = True

    def end_element(self, name):
        global flag
        flag = False

    def char_data(self, data):
        global flag
        if flag:
            self.words.append(data)

    def parse_text(self, text):
        self.p.ParseFile(yahoowakati.get_xml(text))

    def get_words(self):
        return self.words


if __name__=="__main__":
    import sys
    text = sys.argv[1]
    w = Wakati()
    w.parse_text(text)
    words = w.get_words()
    for word in words:
        print word
