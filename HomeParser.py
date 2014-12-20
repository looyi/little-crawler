#!/usr/bin/python
#coding:utf-8

from html.parser import HTMLParser
from PokemonParser import PokemonParser
import urllib.request
import sqlite3

class HomeParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.url = 'http://wiki.52poke.com'
        self.spanNum = 0
        self.linkNum = 0
        self.exact = 0
        self.con = sqlite3.connect('pokemon.db')
        self.cur = self.con.cursor()
        sql = 'drop table if exists pokemontable'
        self.cur.execute(sql)
        sql = 'create table pokemontable(id integer primary key, timenum integer, name text, url text, properties text, character text, skill text)'
        self.cur.execute(sql)
        self.con.commit()
        self.insert = 'insert into pokemontable values(?, ?, ?, ?, ?, ?, ?)'

    def handle_starttag(self, tag, attrs):
        if tag == 'span' and attrs and attrs[0][1] == 'mw-headline':
            self.spanNum += 1
            if self.spanNum == 6:
                self.spanNum = 0
        if self.spanNum > 0 and tag == 'a':
            self.linkNum += 1
            self.link = self.url + attrs[0][1]
            self.exact = 1

    def handle_data(self, data):
        if self.linkNum > 0 and self.exact == 1:
            pokemonParser = PokemonParser(self.linkNum, self.con, self.cur)
            html = urllib.request.urlopen(self.link)
            pokemonParser.feed(html.read().decode('utf-8'))
            self.cur.execute(self.insert, (self.linkNum, self.spanNum, data, self.link, pokemonParser.properties, pokemonParser.character, pokemonParser.skill))
            del pokemonParser
            print(self.linkNum)
    def handle_endtag(self, tag):
        if tag == 'a':
            self.exact = 0

    def __del__(self):
        self.con.commit()
        self.cur.close()
        self.con.close()

