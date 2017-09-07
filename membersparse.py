#!/user/bin/env python
# -*- coding: utf8 -*-
"""
@file    membersparse.py
@author  Cecilia M.
@date    2017-09-02
@version $Id: membersparse.py 04 2017-09-07 11:44: behrisch $

This script acts as a web crawler to aggregate all members'
info of Japanese version from the wiki page
decaf.kouhi.me/lovelive/index.php?title=List_of_Events

There is Future work left to be polished.
1. animating member's file downloading progress
"""

import os
import codecs
from bs4 import BeautifulSoup
import requests
import argparse
import sys
import re
from datetime import date, datetime
import time

from constants import *

MEMBERFOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'member')
nameMap2Fullname = {}	# map from given name to full name, key is given name
memberurls = {}			# key is full name, e.g., Ayase Eli
pointSR = ''
rankSR = ''

def get_options():
	parser = argparse.ArgumentParser(description='SIF member files\' parser')
	parser.add_argument('member', nargs='*', default=US+AQOURS, help='specify which member\'s file to fetch')
	args = parser.parse_args()

	if not args.member:
		print('Error: need to specify at least a member name')
		sys.exit(1)

	for member in args.member:
		if not member in US + AQOURS:
			print('Error: invalid member name "%s"' % member)
			sys.exit(1)

	return args

def init():
	if not os.path.exists(WEBPAGEFILE):
		os.system('python parse.py')

	htmlf = codecs.open(WEBPAGEFILE, 'r', encoding='utf-8-sig')
	soup = BeautifulSoup(htmlf, "html.parser")
	htmlf.close()

	usinfo = soup.find('div', id='p-.CE.BC.27s')
	aqoursinfo = soup.find('div', id='p-Aqours')

	for li in usinfo.findAll('li'):
		member = li['id'][2:]
		memberurls[member] = li.a['href']
		nameMap2Fullname[member.split('-')[1]] = member

	for li in aqoursinfo.findAll('li'):
		member = li['id'][2:]
		memberurls[member] = li.a['href']
		nameMap2Fullname[member.split('-')[1]] = member

	if not os.path.exists(MEMBERFOLDER):
		os.mkdir(MEMBERFOLDER)

	lasteventrow = soup.findAll('tr')[2]
	ths = lasteventrow.findAll('td')
	pointSR = ths[2].text.strip()
	rankSR = ths[3].text.strip()

	del soup

def fetchwebpage(name=None):
	if name == None:
		return

	fullname = nameMap2Fullname[name]
	url = memberurls[fullname]
	filename = os.path.join(MEMBERFOLDER, fullname.encode('ascii') + '.html')

	url = BASEURL + memberurls[fullname]
	try:
		req = requests.get(url, stream=True)
	except requests.exceptions.ConnectionError:
		print('Connection Failed. Please try again.')
		sys.exit(1)
	last_modified = datetime.strptime(req.headers['Last-Modified'], '%a, %d %b %Y %H:%M:%S %Z')

	if not os.path.exists(filename) or os.stat(filename).st_size == 0L or datetime.utcfromtimestamp(os.path.getmtime(filename)) < last_modified:
		print('\nRetriving %s\'s file ...' % fullname)	# Future work: animating with progress
		with codecs.open(filename, 'w', encoding='utf-8') as f:
			f.write(req.text)
	else:
		print('\n%s\'s file is up-to-date.' % fullname)
		
def li2xml(li):
	tag = li.b.string.split(':')[0].replace(' ', '_')
	context = li.text.split(':')[1].strip()
	return '%s<%s>%s</%s>\n' % ('	', tag, context, tag)

def parse(name=None, write=False):
	if name == None:
		return

	color2attribute = {
		'red': 'Smile',
		'green': 'Pure',
		'blue': 'Cool'
	}

	fullname = nameMap2Fullname[name]
	htmlfile = os.path.join(MEMBERFOLDER, fullname + '.html')
	basicfile = os.path.join(MEMBERFOLDER, fullname + MEMBERPROFILESUFFIX)	# a xml file
	parsedfile = os.path.join(MEMBERFOLDER, fullname + '.txt')
	
	if not os.path.exists(htmlfile):
		fetchwebpage(name)

	membersoup = BeautifulSoup(codecs.open(htmlfile, 'r', encoding='utf-8-sig'), "html.parser")

	# member basic info file, only created once
	if not os.path.exists(basicfile) or os.stat(basicfile).st_size == 0L:
		print('Parsing %s\'s character profile to %s ...' % (fullname, fullname + MEMBERPROFILESUFFIX))

		with codecs.open(basicfile, 'w', encoding='utf-8') as f:
			f.write(XMLHEADER + '\n')
			f.write('<characterprofile>\n')
			for li in membersoup.table.findAll('li'):
				f.write(li2xml(li))
			f.write('%s<%s>%s</%s>\n' % ('	', 'description', membersoup.table.find('p').getText().strip(), 'description'))
			f.write('</characterprofile>\n')

	if not os.path.exists(parsedfile) or os.stat(parsedfile).st_size == 0L or os.path.getmtime(htmlfile) > os.path.getmtime(parsedfile):
		print('Parsing %s\'s cards profile to %s ...' % (fullname, fullname + '.txt'))
		
		# parse cards - find all tags between #Cards and #Side_Stories
		tags = []
		for tag in membersoup.find('span', id='Cards').find_parent().next_siblings:
			# next_siblings can be a bs4.element.Tag or a bs4.element.NavigableString (i.e. with only one child string)
			if tag.string == '\n':
				continue
			if tag.find('span', id='Side_Stories'):
				break
			tags.append(tag)

		with codecs.open(parsedfile, 'w', encoding='utf-8') as f:
			# write csv header
			f.write('cardid;rank;attribute;smile;pure;cool;skill;effect;leaderskill;leadereffect;version;realeasedate')

			rank = ''	# current rank for current cards, since rank appears before all cards under it
			isprevdate = True	# each release date coming after one card if any, a flag to show whether the last row is a release date

			for tag in tags:
				if tag.name == 'h3':
					rank = tag.string[:-1]
				elif tag.name == 'table':
					rows = tag.findAll('tr')
					header = rows[0].th.span
					attribute = color2attribute[header['style'].split(';')[0].split(':')[1].strip()]
					cardid = header.string.split('[')[1].split(']')[0].split(' ')[-1]
					version = 'N/A'
					version_match = re.search('\((.*)\)', header.string)
					if version_match:
						version = version_match.group(1)
					# print(version.encode('cp932', 'ignore').decode('cp932'))
					
					# row[1] - two images (3 row/each), Max level: 60(4 col)
					if rows[1].td.text.find('This card comes pre') > -1:
						version = 'pretransformed'

					# row[2] - hp, smile, pure, cool
					smile, pure, cool = [int(td.span.string) for td in rows[2].findAll('td')[1:]]

					# row[3] - skills, two sets in <p> tags under the only <td>, in between there is <p><br /></p> each
					skillsets = rows[3].findAll('p')[0::2]
					try:
						skill = skillsets[0].contents[2].string.split(':')[1].strip()
					except:
						skill = skillsets[0].contents[2].text.split(':')[1].strip()
					effect = skillsets[0].contents[4].strip()
					leaderskill = skillsets[1].contents[2].string.split(':')[1].strip()
					leadereffect = skillsets[1].contents[4].strip()
				
					if not isprevdate:
						f.write('N/A')	# last card's release date is not specified, give it a N/A

					f.write('\n%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;' % (cardid, rank, attribute, smile, pure, cool, skill, effect, leaderskill, leadereffect, version))

					isprevdate = False

				elif tag.name == 'p':
					isprevdate = True
					if not tag.i:
						# print(tag, tag.previous_element, tag.next_element)
						continue
					if tag.i.string:
						# print(tag.i.string)
						releasetext = tag.i.string
					else:
						# print(tag.i.text)
						releasetext = tag.i.text
					
					if releasetext.find('Added on') > -1:
						match = re.search(r'Added on (\w+ \d+, \d+)\.', releasetext)
						timestamp = time.mktime(time.strptime(match.group(1), '%B %d, %Y'))
						releasedate = date.fromtimestamp(timestamp)
					elif releasetext.find('Initially awarded as a prize during') > -1:
						# releasedate = 'Event Reward'
						releasedate = releasetext[7:]
					elif releasetext.find('Bundled with') > -1:
						# releasedate = 'Bundled Bonus'
						releasedate = releasetext[7:]
					elif releasetext.find('Exchanged') > -1:
						releasedate = releasetext[7:]
					elif releasetext.find('Added to Seal Shop on') > -1:
						match = re.search(r'Added to Seal Shop on (\w+ \d+, \d+)\W+', releasetext)
						try:
							timestamp = time.mktime(time.strptime(match.group(1), '%B %d, %Y'))
							releasedate = date.fromtimestamp(timestamp)
						except:
							print(releasetext)
					elif releasetext.find('Awarded') > -1:
						releasedate = releasetext[7:]
					else:
						print(releasetext)
						sys.exit()
					
					# print(releasedate)
					f.write('%s' % releasedate)
					
				# print(tag.prettify().encode('cp932','ignore').decode('cp932'))

def main():
	args = get_options()
	init()
	for member in args.member:
		fetchwebpage(member)
		parse(member)

if __name__ == '__main__':
	main()