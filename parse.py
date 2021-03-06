#!/user/bin/env python
# -*- coding: utf8 -*-
"""
@file    parse.py
@author  Cecilia M.
@date    2017-08-29
@version $Id: sifevents.py 03 2017-09-02 16:40: behrisch $

This script acts as a web crawler to aggregate the past
events of Japanese version from the wiki page
decaf.kouhi.me/lovelive/index.php?title=List_of_Events
"""

import requests
import os
import re
from bs4 import BeautifulSoup
import codecs
from datetime import datetime, date, timedelta

from constants import *

def fetchwebpage():
	r = requests.get(URL)
	htmltext = r.text
	with codecs.open(WEBPAGEFILE, 'w', encoding='utf-8') as f:
		f.write(htmltext)
		f.close()

if not os.path.exists(WEBPAGEFILE):
	fetchwebpage()

# check if local webpagefile is up to date
r = requests.get(URL, stream=True)
last_modified = r.headers['Last-Modified']
last_modified = datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S %Z')
if datetime.utcfromtimestamp(os.path.getmtime(WEBPAGEFILE)) < last_modified:
	fetchwebpage()

# update parsed.txt only when no file exits or webpagefile has been recently updated
if not os.path.exists(PARSEDFILE) or os.path.getmtime(WEBPAGEFILE) > os.path.getmtime(PARSEDFILE):

	htmlf = codecs.open(WEBPAGEFILE, 'r', encoding='utf-8-sig')
	soup = BeautifulSoup(htmlf, "html.parser")
	htmlf.close()

	with codecs.open(PARSEDFILE, 'w', encoding='utf-8') as f:	
		rows = soup.findAll('tr')
		headers = rows[0:2]

		# deal with headers
		col_cnt = 0
		headertext = []
		secondrow_colindex = []

		for th in headers[0].findAll('th'):
			if th.attrs:
				col_cnt += 1
				if 'rowspan' in th.attrs:
					headertext.append(th.text.strip())
				if 'colspan' in th.attrs:
					for i in range(int(th['colspan'])):
						secondrow_colindex.append(col_cnt - 1 + i)
						headertext.append(u''.join(th.text.strip().split(' ')))
					col_cnt += int(th['colspan']) - 1

		ths = headers[1].findAll('th')
		if len(secondrow_colindex) != len(ths):
			raise RuntimeError('second row of headers does not match with first rows col spans')
		for i in range(len(ths)):
			th = ths[i]
			headertext[secondrow_colindex[i]] += '_' + th.text.strip()

		headertext = u';'.join(headertext)
		print(headertext + '\n')

		# real header for the file gathering the info
		f.write("period; name; eventlink; pointsSR; pointsSRLink; rankingSR; rankingSRLink; note\n")

		# events information from wiki
		rank_cutoff_leftrows_1 = 0; last_rank_cutoff_1 = 0
		rank_cutoff_leftrows_2 = 0; last_rank_cutoff_2 = 0
		rank_cutoff_leftrows_3 = 0; last_rank_cutoff_3 = 0
		for row in rows[2:]:
			cols = row.findAll('td')
			try:
				"""
				period, eventname, pointsSR, rankingSR(na until 2016/06/05), (4)
				1stPointCutoff,1stRankCutoff(optional),2ndPointCutoff,2ndRankCutoff(optional),3rdPointCutoff,3rdRankCutoff(optional), (6)
				Notes (1)
				"""
				period = cols[0].text.strip()
				name = cols[1].text.strip()
				eventlink = cols[1].a['href']
				pointsSR = cols[2].text.strip()
				pointsSRLink = cols[2].a['href']

				current_colindex = 3
				if period > "2016/06/05":
					# beginning of Aqour's first round event with two SR rewarded each time
					rankingSR = cols[3].text.strip()
					rankingSRLink = cols[3].a['href']
					current_colindex = 4
				else:
					rankingSR = u'N/A'
					rankingSRLink = u'N/A'
				cols = cols[current_colindex:]
				
				note = u'N/A'
				try:
					int(cols[-1].text.strip())
				except:
					note = cols[-1].text.strip()
					if note != '-':
						cols = cols[:-1]

				# cols are left with only the 1st, 2nd, and 3rd's point and rank cutoff, special case for rank cutoff	
				current_colindex = 0

				point_cutoff_1 = cols[0].text.strip()
				current_colindex += 1
				if rank_cutoff_leftrows_1 == 0:
					if 'rowspan' in cols[current_colindex].attrs:
						rank_cutoff_leftrows_1 = int(cols[current_colindex]['rowspan'])
					else:
						rank_cutoff_leftrows_1 = 1
					last_rank_cutoff_1 = cols[current_colindex].text.strip()
					current_colindex += 1
				rank_cutoff_1 = last_rank_cutoff_1
				rank_cutoff_leftrows_1 -= 1

				point_cutoff_2 = cols[current_colindex].text.strip()
				current_colindex += 1
				if rank_cutoff_leftrows_2 == 0:
					if 'rowspan' in cols[current_colindex].attrs:
						rank_cutoff_leftrows_2 = int(cols[current_colindex]['rowspan'])
					else:
						rank_cutoff_leftrows_2 = 1
					last_rank_cutoff_2 = cols[current_colindex].text.strip()
					current_colindex += 1
				rank_cutoff_2 = last_rank_cutoff_2
				rank_cutoff_leftrows_2 -= 1

				# third tier point cut off is not available until 2016/6/5, i.e. when double SR rewards begins
				point_cutoff_3 = cols[current_colindex].text.strip()
				current_colindex += 1
				if rank_cutoff_leftrows_3 == 0:
					if 'rowspan' in cols[current_colindex].attrs:
						rank_cutoff_leftrows_3 = int(cols[current_colindex]['rowspan'])
					else:
						rank_cutoff_leftrows_3 = 1
					last_rank_cutoff_3 = cols[current_colindex].text.strip()
					current_colindex += 1
				rank_cutoff_3 = last_rank_cutoff_3
				rank_cutoff_leftrows_3 -= 1

				f.write("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s\n" % (period, name.encode('cp932','ignore').decode('cp932'), eventlink, pointsSR, pointsSRLink, rankingSR, rankingSRLink, point_cutoff_1, rank_cutoff_1, point_cutoff_2, rank_cutoff_2, point_cutoff_3,rank_cutoff_3, note))
			except:
				print("%d cols for cutoffs, %s %s" % (len(cols), period, name))
				print(rank_cutoff_leftrows_1, rank_cutoff_leftrows_2, rank_cutoff_leftrows_3, point_cutoff_1, rank_cutoff_1, point_cutoff_2, rank_cutoff_2, point_cutoff_3,rank_cutoff_3)
				break

# working from parsed file, can start from a new file