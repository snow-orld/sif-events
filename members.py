#!/user/bin/env python
# -*- coding: utf8 -*-
"""
@file    members.py
@author  Cecilia M.
@date    2017-09-02
@version $Id: sifevents.py 01 2017-09-02 20:56: behrisch $

This script acts as a web crawler to aggregate all members'
info of Japanese version from the wiki page
decaf.kouhi.me/lovelive/index.php?title=List_of_Events

There is Future work left to be polished.
1. animating member's file downloading progress
"""

import os
import codecs
from bs4 import BeautifulSoup
import urllib
import argparse

from constants import *

if not os.path.exists(WEBPAGEFILE):
	os.system('python parse.py')

htmlf = codecs.open(WEBPAGEFILE, 'r', encoding='utf-8-sig')
soup = BeautifulSoup(htmlf, "html.parser")
htmlf.close()

usinfo = soup.find('div', {'id': 'p-.CE.BC.27s'})
aqoursinfo = soup.find('div', {'id': 'p-Aqours'})

nameMap2Fullname = {}	# map from given name to full name, key is given name
memberurls = {}			# key is full name, e.g., Ayase Eli

for li in usinfo.findAll('li'):
	member = li['id'][2:]
	memberurls[member] = li.a['href']
	nameMap2Fullname[member.split('-')[1]] = member

for li in aqoursinfo.findAll('li'):
	member = li['id'][2:]
	memberurls[member] = li.a['href']
	nameMap2Fullname[member.split('-')[1]] = member

MEMBERFOLDER = 'member/'
if not os.path.exists(MEMBERFOLDER):
	os.mkdir(MEMBERFOLDER)

choices = US + AQOURS
parser = argparse.ArgumentParser(description='SIF members downloader.')
parser.add_argument('member', help='specify which member\'s webpage to download', choices=choices)
args = parser.parse_args()

if not args.member:
	print('Specify a member to download her file.')
	os._exit(1)

if not os.path.exists(MEMBERFOLDER + args.member + '.html') or os.path.getmtime(WEBPAGEFILE) > os.path.getmtime(MEMBERFOLDER + args.member + '.html'):
	with open(MEMBERFOLDER + args.member + '.html', 'w') as f:
		print('Retriving %s\'s file ...' % args.member)	# Future work: animating with progress
		url = BASEURL + memberurls[nameMap2Fullname[args.member]]
		remotef = urllib.urlopen(url)
		f.write(remotef.read())
		remotef.close()

