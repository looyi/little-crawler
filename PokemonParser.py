#!/usr/bin/python
#coding:utf-8

from html.parser import HTMLParser
import sqlite3
import urllib.request
from html.entities import entitydefs

class PokemonParser(HTMLParser):
    def __init__(self, Pnum, con, cur):
        HTMLParser.__init__(self)
        self.Pnum = Pnum
        self.divNum = 0
        self.tdNum = 0
        self.trNum = 0
        self.tableNum = 0
        self.aNum = 0
        self.exact = 0
        self.properties = ''
        self.character = ''
        self.skill = ''
        self.con = con
        self.cur = cur
        self.queryProperty = "select id from restraintable where name='"
        self.querySkill = "select id from skilltable where name='"

        self.starttag_dic = dict()
        self.starttag_dic[1] = self.__handlePicture
        self.starttag_dic[2] = self.__handleProperty_starttag
        self.starttag_dic[4] = self.__handleCharacter_starttag
        self.starttag_dic[6] = self.__handleSkill_starttag

        self.data_dic = dict()
        self.data_dic[1] = self.__handleNothing
        self.data_dic[2] = self.__handleProperty_data
        self.data_dic[4] = self.__handleCharacter_data
        self.data_dic[6] = self.__handleSkill_data

        self.endtag_dic = dict()
        self.endtag_dic[1] = self.__handleNothing
        self.endtag_dic[2] = self.__handleProperty_endtag
        self.endtag_dic[4] = self.__handleCharacter_endtag
        self.endtag_dic[6] = self.__handleSkill_endtag

        no = [3, 5]
        for num in no:
            self.starttag_dic[num] = self.__handleNothing
            self.data_dic[num] = self.__handleNothing
            self.endtag_dic[num] = self.__handleNothing

        self.skillDic = dict()
        self.skillDic['火焰襲擊'] = '火焰袭击'
        self.skillDic['幻象術'] = '幻象术'

    def handle_starttag(self, tag, attrs):
        if self.tableNum < 5:
            if self.tableNum > 0:
                self.starttag_dic[self.tableNum](tag, attrs)
        
            if tag == 'table' and attrs and attrs[0][1] == 'roundy bgwhite fulltable':
                self.tableNum += 1
        elif self.tableNum == 6:
            self.starttag_dic[self.tableNum](tag, attrs)
        elif tag == 'table' and attrs and 'alignt-center align-center roundy' in attrs[0][1]:
            self.tableNum += 1

    def handle_data(self, data):
        if self.tableNum > 0 and self.tableNum < 7:
            self.data_dic[self.tableNum](data)
        
    def handle_endtag(self, tag):
        if self.tableNum > 0 and self.tableNum < 7:
            self.endtag_dic[self.tableNum](tag)
        
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
        pass

    def __handleNothing(self, *arg):
        return 

    def __handlePicture(self, tag, attrs):
        if self.divNum == 1 and tag == 'img':
            urllib.request.urlretrieve(attrs[-1][1], './picture/' + str(self.Pnum) + '.png')
            self.divNum = 0
            self.exact = 1
        if tag == 'div' and attrs and attrs[0][1] == 'tabber':
            self.divNum = 1

    def __handleProperty_starttag(self, tag, attrs):
        if self.tdNum == 1 and tag == 'a':
            self.aNum = 1
        if self.exact == 1 and tag == 'td':
            self.tdNum += 1
    def __handleProperty_endtag(self, tag):
        if self.aNum == 1 and tag == 'a':
            self.aNum = 0
        if self.exact == 1 and tag == 'td':
            self.tdNum = 0
            self.exact = 2
    def __handleProperty_data(self, data):
        if self.aNum == 1 and data != '\xa0' and data != ' ' and data != '\n':
            if len(data) == 3:
                data = data[0:2]
            self.cur.execute(self.queryProperty + data + "'")
            num, = self.cur.fetchone()
            if self.properties:
                self.properties += ' ' + str(num)
            else:
                self.properties = str(num)

    def __handleCharacter_starttag(self, tag, attrs):
        if self.exact == 2:
            if self.trNum == 1 and tag == 'a':
                self.aNum = 1
            if tag == 'tr':
                self.trNum = 1
    def __handleCharacter_endtag(self, tag):
        if tag == 'a':
            self.aNum = 0
        if tag == 'tr' and self.exact == 2:
            self.trNum = 0
            self.exact = 3
            self.aNum = 0
    def __handleCharacter_data(self, data):
        if self.aNum == 1:
            if self.character:
                self.character += ' ' + data
            else:
                self.character = data

    def __handleSkill_starttag(self, tag, attrs):
        if self.tdNum == 0:
            if tag == 'td' and attrs and attrs[0][1] == 'border:1px solid#D8D8D8':
                self.tdNum += 1
        elif self.tdNum == 1:
            if tag == 'a' and attrs and '技能' in attrs[1][1]:
                self.tdNum = 2
        if tag == 'span' and attrs and attrs[0][1] == 'mw-headline':
            self.tableNum += 1
    def __handleSkill_endtag(self, tag):
        if self.tdNum == 3 and tag == 'tr':
            self.tdNum = 0
    def __handleSkill_data(self, data):
        if self.tdNum == 2:
            temp = self.skillDic.get(data)
            if temp:
                data = temp
            self.cur.execute(self.querySkill + data + "'")
            num, = self.cur.fetchone()
            if self.skill:
                self.skill += ' ' + str(num)
            else:
                self.skill = str(num)
            self.tdNum += 1

