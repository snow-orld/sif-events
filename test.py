from classes import *
import os
import calendar

import grequests
import workerpool
import urllib

full ='Kousaka-Honoka'

with open(os.path.join('member', full + '.txt')) as f:
	header = f.readline()
	row1 = f.readline()
	row2 = f.readline()

	cardid, rank, attribute, url1, url2, smile, pure, cool, skill, effect, leaderskill, leadereffect, version, releasedate = \
				row1.strip().split(';')
	c1 = Card(cardid, 'Ho', attribute, rank, url1, url2, smile, pure, cool, skill, effect, leaderskill, leadereffect, version, releasedate)
	
	cardid, rank, attribute, url1, url2, smile, pure, cool, skill, effect, leaderskill, leadereffect, version, releasedate = \
				row2.strip().split(';')
	c2 = Card(cardid, 'Ho', attribute, rank, url1, url2, smile, pure, cool, skill, effect, leaderskill, leadereffect, version, releasedate)

	print(c1)
	print(c2)

	# print(c1.__cmp__(c2))
	print(c1.__lt__(c2))

monthall2num = {abbr.lower(): num for num, abbr in enumerate(calendar.month_abbr) if num}
for num, name in enumerate(calendar.month_name):
	if num:
		monthall2num[name.lower()] = num
print(monthall2num)

# download1.py - Download many URLs using a single thread
import os
import urllib

# Loop over urls.txt and download the URL on each line
for url in open("urls.txt"):
    save_to = os.path.basename(url.split(':')[-1].strip().split('.')[0])
    print('Saving %s to %s' % (url, save_to))
    urllib.request.urlretrieve(url, save_to)
