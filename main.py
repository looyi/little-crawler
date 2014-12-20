#!/usr/bin/python
#coding:utf-8

from HomeParser import HomeParser
from RestrainParser import RestrainParser
from SkillParser import SkillParser
import urllib.request

restrainUrl = 'http://wiki.52poke.com/wiki/%E5%B1%9E%E6%80%A7%E7%9B%B8%E6%80%A7%E8%A1%A8'
restrainHtml = urllib.request.urlopen(restrainUrl)
parser = RestrainParser()
parser.feed(restrainHtml.read().decode('utf-8'))
del parser

skillUrl = 'http://wiki.52poke.com/wiki/%E6%8A%80%E8%83%BD%E5%88%97%E8%A1%A8'
skillHtml = urllib.request.urlopen(skillUrl)
parser = SkillParser()
parser.feed(skillHtml.read().decode('utf-8'))
del parser


catalog = 'http://wiki.52poke.com/wiki/%E7%A5%9E%E5%A5%87%E5%AE%9D%E8%B4%9D%E5%88%97%E8%A1%A8%EF%BC%88%E6%8C%89%E5%85%A8%E5%9B%BD%E5%9B%BE%E9%89%B4%E7%BC%96%E5%8F%B7%EF%BC%89/%E7%AE%80%E5%8D%95%E7%89%88'

homeHtml = urllib.request.urlopen(catalog)
parser = HomeParser()
parser.feed(homeHtml.read().decode('utf-8'))
del parser

