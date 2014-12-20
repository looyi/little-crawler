#!/usr/bin/python
#coding:utf-8

from html.parser import HTMLParser
import sqlite3
import urllib.request
from html.entities import entitydefs

class RestrainParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.thNum = 0
        self.tdNum = 0
        self.trNum = -1
        self.aNum = 0
        self.trHead = 0
        self.exact = 0
        self.con = sqlite3.connect('pokemon.db')
        self.cur = self.con.cursor()
        sql = 'drop table if exists restraintable'
        self.cur.execute(sql)
        self.con.commit()
        self.insert = 'insert into restraintable values(?, '
        self.properties = []
        self.datalist = [None, ]

    def handle_starttag(self, tag, attrs):
        if self.trNum > -1:
            if tag == 'a':
                self.aNum = 1
            if tag == 'td':
                if attrs and attrs[0][1] == '20':
                    self.thNum = 0
                    self.trNum = -1
                elif self.trNum > 0:
                    self.tdNum = 1
        if self.thNum == 1 and tag == 'tr':
            self.trNum += 1
            if self.trNum == 1:
                sql = 'create table restraintable(id integer primary key, name text'
                for p in self.properties:
                    sql += ', ' + p
                    self.insert += '?, '
                sql += ')'
                self.insert += '?)'
                self.cur.execute(sql)
        if tag == 'th' and attrs and attrs[0][1] == '18':
            self.thNum = 1
    def handle_data(self, data):
        if self.aNum == 1:
            if self.trNum == 0:
                self.properties.append(data)
            else:
                self.datalist.append(data)
        elif self.trNum > 0 and self.tdNum > 0:
            if data[1] == '½':
                self.datalist.append(1)
            elif data[1] == '1':
                self.datalist.append(2)
            elif data[1] == '2':
                self.datalist.append(4)
            else:
                self.datalist.append(0)
    def handle_endtag(self, tag):
        if self.trNum > -1 and tag == 'a':
            self.aNum = 0
        if self.thNum == 1 and tag == 'td':
            self.tdNum = 0
        if self.thNum == 1 and self.trNum > 0 and tag == 'tr':
            self.cur.execute(self.insert, self.datalist)
            self.datalist = [None, ]
    def handle_entityref(self, name):
        if name in entitydefs:
            self.handle_data(entitydefs[name])
        else:
            self.handle_data('&' + name + ';')
    def handle_charref(self, name):
        try:
            charnum = int(name)
        except ValueError:
            return
        if charnum < 1 or charnum > 255:
            return
        self.handle_data(chr(charnum))

    def __del__(self):
        self.con.commit()
        self.cur.close()
        self.con.close()

