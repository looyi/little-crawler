#!/usr/bin/python
#coding:utf-8

from html.parser import HTMLParser
import sqlite3
import urllib.request
from html.entities import entitydefs

class SkillParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.spanNum = -1
        self.tdNum = 0
        self.trNum = 0
        self.aNum = 0
        self.trHead = 0
        self.exact = 0
        self.end = 0
        self.con = sqlite3.connect('pokemon.db')
        self.cur = self.con.cursor()
        sql = 'drop table if exists skilltable'
        self.cur.execute(sql)
        sql = 'create table skilltable(id integer primary key, name text, property integer, type text, power integer, hitrate integer, pp integer)'
        self.cur.execute(sql)
        self.con.commit()
        self.insert = 'insert into skilltable values(?, ?, ?, ?, ?, ?, ?)'
        self.skill = [None, ]
        self.query = "select id from restraintable where name='"
        self.propertyDic = dict()
        self.propertyDic['惡'] = '恶'
        self.propertyDic['格鬥'] = '格斗'
        self.propertyDic['電'] = '电'
        self.propertyDic['飛行'] = '飞行'

        self.skillDic = dict()
        self.skillDic['憤怒之粉'] = '愤怒之粉'
        self.skillDic['盤卷'] = '盘卷'
        self.skillDic['你先請'] = '你先请'
        self.skillDic['報復'] = '报复'
        self.skillDic['特技演員'] = '特技演员'
        self.skillDic['懲罰'] = '惩罚'
        self.skillDic['投擲'] = '投掷'
        self.skillDic['討敵'] = '讨敌'
        self.skillDic['泥漿波'] = '泥浆波'
        self.skillDic['火焰襲擊'] = '火焰袭击'
        self.skillDic['同步干擾'] = '同步干扰'
        self.skillDic['幻象攻擊'] = '幻象攻击'
        self.skillDic['清除迷霧'] = '清除迷雾'
        self.skillDic['防禦交換'] = '防御交换'
        self.skillDic['愛心搗擊'] = '爱心捣击'
        self.skillDic['迴音'] = '回音'
        self.skillDic['詐欺'] = '诈欺'
        self.skillDic['延後'] = '延后'
        self.skillDic['徵收'] = '征收'
        self.skillDic['回復阻擋'] = '回复阻挡'
        self.skillDic['瘋狂伏特'] = '疯狂伏特'
        self.skillDic['毒液攻擊'] = '毒液攻击'
        self.skillDic['掃巴掌'] = '扫巴掌'
        self.skillDic['冰凍世界'] = '冰冻世界'
        self.skillDic['寒冷閃光'] = '寒冷闪光'
        self.skillDic['破壞技術'] = '破坏技术'

    def handle_starttag(self, tag, attrs):
        if self.spanNum > 0 and self.end == 0:
            if self.tdNum > 1 and tag == 'a':
                self.aNum = 1
            if self.trNum > 0 and tag == 'td':
                self.tdNum += 1
                if self.tdNum > 6:
                    self.exact = 1
            if tag == 'tr' and self.trHead == 1:
                if self.trNum > 0:
                    self.cur.execute(self.insert, self.skill)
                    self.skill = [None, ]
                self.trNum += 1
        if tag == 'span' and attrs and attrs[0][1] == 'mw-headline':
            self.spanNum += 1
            self.trHead = 0
    def handle_data(self, data):
        if self.spanNum > 0 and self.end == 0:
            if self.aNum == 1:
                if self.tdNum == 5:
                    #将超能力转化为超能，因为属性存的是超能而不是超能力
                    temp = self.propertyDic.get(data)
                    if temp:
                        data = temp
                    elif len(data) == 3:
                        data = data[0:2]
                    self.cur.execute(self.query+data+"'")
                    num, = self.cur.fetchone()
                    self.skill.append(num)
                else:
                    if self.tdNum == 2:
                        temp = self.skillDic.get(data)
                        if temp:
                            data = temp
                    self.skill.append(data)
            if self.tdNum > 6 and self.exact == 1:
                if len(data) > 1:
                    if data[1] > '0' and data[1] <= '9':
                        try:
                            self.skill.append(int(data))
                        except ValueError:
                            pass
                    elif '—' in data:
                        self.skill.append(0)
                    elif '变化' in data:
                        self.skill.append(300)
                    elif '技能' in data:
                        self.skill.append(301)
                    else:
                        pass
    def handle_endtag(self, tag):
        if self.spanNum == 7:
            if tag == 'table':
                self.end = 1
        if self.spanNum > 0 and self.end == 0:
            if self.tdNum > 1:
                if tag == 'a':
                    self.aNum = 0
                if self.tdNum > 6:
                    self.exact = 0
            if tag == 'tr':
                if self.trHead == 0:
                    self.trHead = 1
                if self.tdNum > 0:
                    self.tdNum = 0
        
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
        self.cur.execute(self.insert, self.skill)
        self.con.commit()
        self.cur.close()
        self.con.close()
    
