#!/user/bin/env python
# -*- coding: utf8 -*-
"""
@file    parse.py
@author  Cecilia M.
@date    2017-08-29
@version $Id: sifevents.py 02 2017-08-30 15:13: behrisch $

This script acts as a web crawler to aggregate the past
events of Japanese version from the wiki page
decaf.kouhi.me/lovelive/index.php?title=List_of_Events
"""

import urllib
import os
from bs4 import BeautifulSoup
import codecs
import time

from constants import *

if not os.path.exists(WEBPAGEFILE):
	f = urllib.urlopen(URL)
	htmltext = f.read()
	with open(WEBPAGEFILE, 'w') as f:
		f.write(htmltext)
		f.close()

htmlf = codecs.open(WEBPAGEFILE, 'r', encoding='utf-8-sig')
soup = BeautifulSoup(htmlf, "html.parser")
rows = soup.findAll('tr')
headers = rows[0:2]

f = codecs.open(PARSEDFILE, 'w', encoding='utf-8')

# deal with headers
col_cnt = 0
headertext = []
secondrow_colindex = []

for th in headers[0].findAll('th'):
	if th.attrs:
		col_cnt += 1
		if th.attrs.has_key('rowspan'):
			headertext.append(th.text.strip())
		if th.attrs.has_key('colspan'):
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
			if cols[current_colindex].attrs.has_key('rowspan'):
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
			if cols[current_colindex].attrs.has_key('rowspan'):
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
			if cols[current_colindex].attrs.has_key('rowspan'):
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

f.close()

# working from parsed file, can start from a new file