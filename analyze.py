#!/user/bin/env python
# -*- coding: utf8 -*-
"""
@file    analysis.py
@author  Cecilia M.
@date    2017-08-30
@version $Id: sifevents.py 01 2017-08-30 15:14: behrisch $

This script analyzes the past events of Japanese version 
based on a local parsed file with info from the wiki page
decaf.kouhi.me/lovelive/index.php?title=List_of_Events
"""

import os
import re
import codecs
import webbrowser
from datetime import date

from constants import *

class Period(object):
	"""Class Period parsing from the string format year/month/day - month/day"""
	def __init__(self, periodstr):
		super(Period, self).__init__()
		start, end = periodstr.split('-')[:2]
		if len(end.split('/')) < len(start.split('/')):
			end = u'/'.join((start.split('/')[0], end.strip()))
		year, month, day = [int(e) for e in start.split('/')]
		self.__startdate = date(year, month, day)
		year, month, day = [int(e) for e in end.split('/')]
		self.__enddate = date(year, month, day)

	def get_startdate(self):
		return self.__startdate
	def get_enddate(self):
		return self.__enddate

	def contains(self, datestr):
		# if the datestr in the format yyyy/mm/dd is within this period
		if len(datestr.strip().split('/')) != 3:
			raise RuntimeError('invalid date string format %s (%s expected)' % (datestr, 'yyyy/mm/dd'))
		year, month, day = [int(e) for e in datestr.strip().split('/')]
		return date(year, month, day) >= self.__startdate and datestr <= self.__enddate

class Event(object):
	def __init__(self, period, name, eventlink, pointsSR, pointsSRLink, rankingSR, rankingSRLink, point_cutoff_1, rank_cutoff_1, point_cutoff_2, rank_cutoff_2, point_cutoff_3,rank_cutoff_3, note):
		super(Event, self).__init__()
		self.__period = Period(period)
		self.__name = name
		self.__eventlink = eventlink
		self.__pointsSR = pointsSR
		self.__pointsSRLink = pointsSRLink
		self.__rankingSR = rankingSR 
		self.__rankingSRLink = rankingSRLink
		self.__note = note

		if name.find('Round') == -1:
			self.__type = EVENTTYPES[0]
			self.__times = None
		else:
			self.__type = name[:name.find('Round')].strip()
			self.__times = int(name[name.find('Round') + 5:].strip())

		if self.__pointsSR in US:
			self.__unit = "u's" # µ's
		elif self.__pointsSR in AQOURS:
			self.__unit = "Aqours"
		else:
			self.__unit = 'Unknown'

		self.__cutoff = {}
		if len(point_cutoff_1) and point_cutoff_1 != '-':
			self.__cutoff['point1'] = int(point_cutoff_1)
		else:
			self.__cutoff['point1'] = None
		self.__cutoff['rank1'] = int(rank_cutoff_1)
		if len(point_cutoff_2) and point_cutoff_2 != '-':
			self.__cutoff['point2'] = int(point_cutoff_2)
		else:
			self.__cutoff['point2'] = None
		self.__cutoff['rank2'] = int(rank_cutoff_2)
		if len(point_cutoff_3) and point_cutoff_3 != '-':
			self.__cutoff['point3'] = int(point_cutoff_3)
		else:
			self.__cutoff['point3'] = None
		self.__cutoff['rank3'] = int(rank_cutoff_3)

	def get_event_name(self):
		return self.__name

	def get_event_link(self):
		return self.__eventlink

	def get_event_type(self):
		return self.__type

	def get_event_times(self):
		return self.__times

	def set_event_times(self, times):
		if self.__type == EVENTTYPES[0]:
			self.__times = times
		else:
			print('Event type is %s. Cannot change event times of type other than Collection Event' % (self.__type))

	def get_event_startdate(self):
		return self.__period.get_startdate()

	def get_event_enddate(self):
		return self.__period.get_enddate()

	def get_event_pointsSR(self):
		return self.__pointsSR

	def get_event_pointsSR_link(self):
		return self.__pointsSRLink

	def get_event_unit(self):
		return self.__unit

	def get_event_cutoff(self):
		return self.__cutoff

class EventManager(object):
	def __init__(self):
		self.__eventtypes = EVENTTYPES
		self.__events = {}
		self.__oldest_startdate = None
		self.__latest_startdate = None

	def has_eventtype(self, etype):
		return etype in self.__eventtypes

	def add_eventtype(self, etype):
		if etype not in EVENTTYPES:
			self.__eventtypes.append(etype)

	def get_all_event_types(self):
		return self.__eventtypes

	def add_event(self, event):
		startdate = event.get_event_startdate()
		etype = event.get_event_type()
		if self.__events.has_key(startdate):
			raise RuntimeError('Add new event error... Duplicate event start date')
			return
		else:
			self.__events[startdate] = event
			if etype not in self.__eventtypes:
				self.__eventtypes.append(etype)

		# update the min/max events in terms of startdate, i.e. keys
		if not self.__oldest_startdate:
			self.__oldest_startdate = startdate
		elif self.__oldest_startdate > startdate:
			self.__oldest_startdate = startdate
		if not self.__latest_startdate:
			self.__latest_startdate = startdate
		elif self.__latest_startdate < startdate:
			self.__latest_startdate = startdate

	def get_events(self, etype):
		events = {}
		# note, dictionary does not preserver order regardless of inserted order
		if etype.lower() == 'all' or etype.lower() == 'a':
			return self.__events
		elif etype.lower() in [t.lower() for t in self.__eventtypes]:
			print([t.lower() for t in self.__eventtypes])
			events = {}
			for key in sorted(self.__events.keys()):
				if self.__events[key].get_event_type().lower() == etype.lower():
					events[key] = self.__events[key]
		elif etype.lower() in UNITS + ["u's", "us"]:
			if etype.lower() in ["u's", "us"]:
				etype = UNITS[0]
			events = {}
			print(etype.encode('latin1').decode('latin1'))
			for key in sorted(self.__events.keys()):
				if self.__events[key].get_event_unit().lower() == etype.lower():
					events[key] = self.__events[key]
		return events

	def open_link(self, link):
		webbrowser.open(BASEURL + link)

	def get_event_pattern(self, months=12):
		"""output each month's events in one row, with event type and event unit only, in latest 12 months"""
		today = date.today()
		startdates = sorted(self.__events.keys())[max(-months*2, -len(self.__events)):]
		prevmonth = 0
		lastmonth_info = ""
		for startdate in startdates:
			event = self.__events[startdate]
			if prevmonth != startdate.month:
				print(lastmonth_info)
				print('\n\t\t\t%s / %s\n' % (startdate.year, startdate.month))
				lastmonth_info = ""
				prevmonth = startdate.month
			if startdate >= startdate.replace(day=15):
				# 2nd event in the month
				lastmonth_info += ' ' * (32 - len(lastmonth_info))
			lastmonth_info += '%s %d, %s' % (event.get_event_type(), event.get_event_times(), event.get_event_unit())
		# last month's info is not yet printed
		print(lastmonth_info)

	def test(self):
		events = self.get_events('us')
		for key in sorted(events.keys()):
			event = events[key]
			print("%s %s %s: %d" % (key, event.get_event_name(), event.get_event_type(), event.get_event_times()))
		self.get_event_pattern(months=6)

def main():
	if not os.path.exists(PARSEDFILE):
		os.system("python parse.py")

	eventmanager = EventManager()
	with codecs.open(PARSEDFILE, 'r', encoding='utf-8') as f:
		header = f.readline().split('\n')[0]
		print("%s (%d)" % (header.replace(';', ' |'), len(header.split(';'))))

		# bring lines in chronological order, for counting times of collection event only
		lines = []
		for line in f:
			lines.append(line)
		lines.reverse()

		collectioneventcnt = 0
		for line in lines:
			period, name, eventlink, pointsSR, pointsSRLink, rankingSR, rankingSRLink, point_cutoff_1, rank_cutoff_1, point_cutoff_2, rank_cutoff_2, point_cutoff_3,rank_cutoff_3, note = line.strip().split(u';')
			# print("%s | %s %s\n%s %s\n%s %s \n%s | %s | %s | %s | %s | %s\n%s" % (period, name, eventlink, pointsSR, pointsSRLink, rankingSR, rankingSRLink, point_cutoff_1, rank_cutoff_1, point_cutoff_2, rank_cutoff_2, point_cutoff_3,rank_cutoff_3, note))

			event = Event(period, name, eventlink, pointsSR, pointsSRLink, rankingSR, rankingSRLink, point_cutoff_1, rank_cutoff_1, point_cutoff_2, rank_cutoff_2, point_cutoff_3,rank_cutoff_3, note)
			# print("%s, %s %d" % (period, event.get_event_type(), event.get_event_times()))

			if event.get_event_type() == EVENTTYPES[0]:
				collectioneventcnt += 1
				event.set_event_times(collectioneventcnt)

			eventmanager.add_event(event)

		eventmanager.test()

if __name__ == '__main__':
	main()