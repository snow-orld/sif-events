#!/user/bin/env python
# -*- coding: utf8 -*-
"""
@file    analyze.py
@author  Cecilia M.
@date    2017-08-30
@version $Id: analyze.py 04 2017-09-08 18:51: behrisch $

This script analyzes the past events of Japanese version 
based on a local parsed file with info from the wiki page
decaf.kouhi.me/lovelive/index.php?title=List_of_Events
"""

import os
import re
import codecs
import webbrowser
from datetime import date, timedelta
import argparse
import urllib
import sys
import xml.etree.ElementTree as ET
import calendar

from constants import *
from classes import *
import membersparse as mp

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

	def __repr__(self):
		return '{}: {}/{}/{} - {}/{}/{}'.format(self.__class__.__name__,
			self.__startdate.year,
			self.__startdate.month,
			self.__startdate.day,
			self.__enddate.year,
			self.__enddate.month,
			self.__enddate.day)

	def __cmp__(self, other):
		return self.get_startdate().__cmp__(other.get_startdate())

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

		if pointsSR in US:
			self.__unit = "u's" # µ's
		elif pointsSR in AQOURS:
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

	def __repr__(self):
		return '{}: '.format(self.__class__.__name__,
			self.__period,
			self.__unit,
			self.__name,
			self.__type,
			self.__times,
			self.__pointsSR,
			self.__rankingSR,
			)

	def __cmp__(self, other):
		return self.get_event_startdate().__cmp__(other.get_event_startdate())
	
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
		
	def load_events(self):
		with codecs.open(PARSEDFILE, 'r', encoding='utf-8') as f:
			header = f.readline().split('\n')[0]
			print("Loading events ...")
			# print("%s" % (header.replace(';', ' |')))

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

				self.add_event(event)

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

	def get_events(self, etype, startdate=date.min, enddate=date.today()):
		events = {}
		# note, dictionary does not preserver order regardless of inserted order
		if etype.lower() == 'all' or etype.lower() == 'a':
			for key in sorted(self.__events.keys()):
				if key >= startdate and key <= enddate:
					events[key] = self.__events[key]
		elif etype.lower() in [t.lower().replace(' ', '') for t in self.__eventtypes]:
			print([t.lower() for t in self.__eventtypes])
			events = {}
			for key in sorted(self.__events.keys()):
				if key >= startdate and key <= enddate and self.__events[key].get_event_type().lower().replace(' ','') == etype.lower():
					events[key] = self.__events[key]
		elif etype.lower() in GROUPS + ["u's", "us"]:
			if etype.lower() in ["u's", "us"]:
				etype = GROUPS[0]
			events = {}
			print(etype.encode('latin1').decode('latin1'))
			for key in sorted(self.__events.keys()):
				if key >= startdate and key <= enddate and self.__events[key].get_event_unit().lower() == etype.lower():
					events[key] = self.__events[key]
		return events

	def open_link(self, link):
		webbrowser.open(BASEURL + link)

	def get_event_pattern(self, months=12):
		"""output each month's events in one row, with event type and event unit only, in latest 12 months"""
		today = date.today()
		startdates = sorted(self.__events.keys())[max(-int(months)*2,-len(self.__events)):]
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

class Member(object):
	"""docstring for Member"""
	def __init__(self, name, grade, birthday, age):
		super(Member, self).__init__()
		self.__name = name
		self.__fullname = mp.nameMap2Fullname[name]
		self.__grade = grade
		self.__age = age
		self.__cardpool = {'R': {}, 'SR': {}, 'SSR': {}, 'UR': {}}

		# birthday string from character profile needs futher parsing to format date
		month2num = {name: num for num, name in enumerate(calendar.month_name) if num}
		match = re.search(r'(^\w+)\W(\d+)[a-z]*\W', birthday)
		month = int(month2num[match.group(1)])
		day = int(match.group(2))
		self.__birthday = date(date.today().year, month, day)

	def __repr__(self):
		return '{}: |{}|{}|{}|{}|{}|{}|{}|'.format(self.__class__.__name__,
			self.__fullname,
			' ' * (16 - len(self.__fullname)),
			self.__grade,
			' ' * (10 - len(self.__grade)),
			self.__birthday,
			' ' * (16 - len(self.__birthday)),
			self.get_cards_number())

	def add_card(self, card):
		rank = card.rank
		cardid = card.id
		if cardid in self.__cardpool[rank]:
			raise RuntimeError('Member add new card error: Duplicate card id')
		else:
			self.__cardpool[rank][cardid] = card

	def get_cards(self, cardid=None, rank=None, attribute=None, startdate=date.min, enddate=date.today()):
		if cardid != None and type(cardid) != int:
			raise RuntimeError('Get member cards error: invalid cardid type %s' % type(cardid))

		cards = {}
		if cardid:
			for rank in self.__cardpool:
				if cardid in self.__cardpool[rank]:
					cards[cardid] = self.__cardpool[rank][cardid]
					break
			if len(cards) and (rank or attribute):
				if rank:
					if cards[cardid].rank != rank:
						cards = {}
				if attribute:
					if cards[cardid].attribute != attribute:
						cards = {}
		else:
			# no cardid specified, return all cards matching rank and attribute if given
			if rank and attribute:
				for cardid in self.__cardpool[rank]:
					card = self.__cardpool[rank][cardid]
					if card.attribute == attribute:
						if type(card.releasedate) == str or (card.releasedate >= startdate and card.releasedate <= enddate):
							cards[cardid] = card
			elif rank and not attribute:
				for cardid in self.__cardpool[rank]:
					card = self.__cardpool[rank][cardid]
					if type(card.releasedate) == str or (card.releasedate >= startdate and card.releasedate <= enddate):
						cards[cardid] = card
			elif not rank and attribute:
				for rank in self.__cardpool:
					for cardid in self.__cardpool[rank]:
						card = self.__cardpool[rank][cardid]
						if card.attribute == attribute:
							if type(card.releasedate) == str or (card.releasedate >= startdate and card.releasedate <= enddate):
								cards[cardid] = card
			else:
				print('No cardid, rank, or attribut specified to pick cards. Nothing can be selected.')

		return cards

	def get_cards_number(self):
		return 'R: %d, SR: %d, SSR: %d, UR: %d' % (len(self.__cardpool['R']), len(self.__cardpool['SR']), len(self.__cardpool['SSR']), len(self.__cardpool['UR']))

	def get_name(self):
		return self.__name

	def get_grade(self):
		return self.__grade

	def get_birthday(self):
		return self.__birthday

class MemberManager(object):
	"""docstring for MemberManager"""
	def __init__(self):
		super(MemberManager, self).__init__()
		self.__members = {}
	
	def load_member(self, name):
		if not name in US+AQOURS:
			raise RuntimeError('Load member error: invalid member name %s' % name)

		fullname = mp.nameMap2Fullname[name]
		profilefile = os.path.join('member', fullname + MEMBERPROFILESUFFIX)	# profile is of xml
		cardfile = os.path.join('member', fullname + '.txt')

		# basic info
		print('Loading %s\'s basic info ...' % name)
		profile = ET.parse(profilefile).getroot()
		age = profile[1].text
		birthday = profile[2].text
		grade = re.search(r'\s(\w+-year)\s', profile[-1].text).group(1).replace('-', ' ').replace('first', '1st').replace('second', '2nd').replace('third', '3rd').replace('year', 'Year')
		
		member = Member(name, grade, birthday, age)

		# card
		with open(cardfile, 'rU') as f:
			# print('\nLoading %s\'s cards ...' % name)
			header = f.readline().strip().replace(';', ' | ')
			# print(header + '\n')

			for line in f:
				cardid, rank, attribute, normalimagelink, idolizedimagelink, smile, pure, cool, skill, effect, leaderskill, leadereffect, version, releasedate = \
					line.strip().split(';')
				# print(cardid, rank, attribute, smile, pure, cool, skill, effect, leaderskill, leadereffect, version, releasedate)

				if rank == 'Rare':
					card = RCard(cardid, name, attribute, normalimagelink, idolizedimagelink, smile, pure, cool, skill, effect, leaderskill, leadereffect, version, releasedate)
				if rank == 'Super Rare':
					card = SRCard(cardid, name, attribute, normalimagelink, idolizedimagelink, smile, pure, cool, skill, effect, leaderskill, leadereffect, version, releasedate)
				if rank == 'Super Super Rare':
					card = SSRCard(cardid, name, attribute, normalimagelink, idolizedimagelink, smile, pure, cool, skill, effect, leaderskill, leadereffect, version, releasedate)
				if rank == 'Ultra Rare' and version != 'pretransformed':
					card = URCard(cardid, name, attribute, normalimagelink, idolizedimagelink, smile, pure, cool, skill, effect, leaderskill, leadereffect, version, releasedate)
				if rank == 'Ultra Rare' and version == 'pretransformed':
					card = URGiftCard(cardid, name, attribute, normalimagelink, idolizedimagelink, smile, pure, cool, skill, effect, leaderskill, leadereffect, version, releasedate)
				
				member.add_card(card)

		self.add_member(member)

	def add_member(self, memeber):
		name = memeber.get_name()
		if name in self.__members:
			raise RuntimeError('Add member error: Duplicate member')
		else:
			self.__members[name] = memeber

	def loaded_member(self, name):
		return name in self.__members

	def get_member(self, name):
		try:
			return self.__members[name]
		except:
			return None

	def get_coming_birthday(self, months=None):
		# show birthday in the coming year starting from today if months not specified, or
		# show birthday in given months, which is array of integer from 1 to 12
		today = date.today()
		birthdays = []
		for name in US+AQOURS:
			if not self.loaded_member(name):
				mp.parse(name)
				self.load_member(name)

			birthday = self.get_member(name).get_birthday()

			if birthday < today:
				birthday = birthday.replace(year=today.year + 1)

			if not months or (months and birthday.month in months):
				birthdays.append((name, birthday))

		return sorted(birthdays, key=lambda name2birthday: name2birthday[1])

def get_options():
	# handle arguments
	parser = argparse.ArgumentParser(description='SIF events analyzer.')
	parser.add_argument('genere', nargs='?', default='event', help='analyzer genere', choices=['event', 'member'])
	parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
	parser.add_argument('-T', '--type', help='event: get all events by event or unit type')
	parser.add_argument('-B', '--month', metavar='M', default=12, help='event: the number of latest months to investigate')
	parser.add_argument('-P', '--patern', action='store_true', help='event: show latest 12 months events pattern')
	parser.add_argument('-t', '--test', action='store_true', help='event: run eventmanager\' test methods')
	parser.add_argument('-m', '--member', metavar='name', nargs='*', default=[], choices=US+AQOURS, help='member: pre-load members\' files to perform further quries')
	parser.add_argument('-b', '--birthday', action='store_true', help='member: show birthday, more fine granularity control with --birthday-xxx options')
	parser.add_argument('--birthday-member', nargs='+', choices=US+AQOURS+['a','all'], help='member: display birthday of (a) member(s)')
	parser.add_argument('--birthday-month', nargs='+', choices=list(calendar.month_name)+list(calendar.month_abbr), help='member: show member with birthday in speicified month')
	parser.add_argument('-c', '--card', nargs='+', help='member: select member cards by rank or cardid or attribute')
	parser.add_argument('--before-date', help='if specified, only events or cards before specified date is investigated')
	parser.add_argument('--after-date', help='if specified, only events or cards after specified date is investigated ')
	
	args = parser.parse_args()

	return args

def parse_date(datestring):
	if datestring == None:
		return None
	match = re.search(r'(\d+)\W(\d+)\W(\d+)', datestring)
	if match:
		y, m, d = int(match.group(1)), int(match.group(2)), int(match.group(3))
		# print y, m, d
		return date(y, m, d)
	else:
		raise RuntimeError('Parse date error: invalid date format "{}"'.format(datestring))


def main():
	
	args = get_options()

	startdate = parse_date(args.after_date)
	enddate = parse_date(args.before_date)
	if not startdate:
		startdate = date.min
	if not enddate:
		enddate = date.today()

	if args.genere == 'event':

		# update local parsed file if necessary
		os.system("python parse.py")

		eventmanager = EventManager()
		eventmanager.load_events()

		if args.patern:
			eventmanager.get_event_pattern(months=args.month)

		if args.type:
			events = eventmanager.get_events(args.type, startdate, enddate)
			for startdate in sorted(events.keys()):
				event = events[startdate]
				print('%s %s %s %s' % (startdate, event.get_event_unit(), event.get_event_name(), event.get_event_times() if event.get_event_type() == 'Collection Event' else ''))

		if args.test:
			eventmanager.test()

	if args.genere == 'member':

		if args.member or args.birthday or args.card:
			mp.init()
			membermanager = MemberManager()
		else:
			return

		# update local pasrsed file if necessary
		for member in args.member:
			mp.fetchwebpage(member)
			mp.parse(member)

			membermanager.load_member(member)

		if args.birthday:
			if not args.birthday_member and not args.birthday_month:
				print('Get member birthday information.\nUsage: %s member -b --birthday-member [name [name...]] or --birthday-month [month [month ...]]' % __file__)

			elif args.birthday_member:
				if 'a' in args.birthday_member or 'all' in args.birthday_member:
					birthdaylist = membermanager.get_coming_birthday()
					# returned in format [('name', 'birthday'), ...]
					print('\nUpcoming birthdays ...')
					for name, birthday in birthdaylist:
						print('%s  %s' % (birthday, name))
				else:
					for name in args.birthday:
						if not name in args.member:
							mp.parse(name)
							membermanager.load_member(name)

						# birthday in type date, in current year
						birthday = membermanager.get_member(name).get_birthday()
						print('%s  %s' % (birthday, name))
			elif args.birthday_month:
				months = set()
				
				# pre-parsing Abbreviate or Fullname month to integer from 1 to 12
				monthall2num = {abbr: num for num, abbr in enumerate(calendar.month_abbr) if num}
				for num, name in enumerate(calendar.month_name):
					if num:
						monthall2num[name] = num

				for month in args.birthday_month:
					months.add(monthall2num[month])

				# returned in format [('name', 'birthday'), ...]
				birthdaylist = membermanager.get_coming_birthday(months)
				print('\n%d member(s) with Birthday in %s' % (len(birthdaylist), args.birthday_month))
				for name, birthday in birthdaylist:
					print('%s  %s' % (birthday, name))

		if args.card:
			name = None
			attribute = None
			rank = None
			cardid = None

			for cardarg in args.card:
				if cardarg in US+AQOURS:
					name = cardarg
				if cardarg[0] == '#':
					cardid = int(cardarg[1:])
				if cardarg in CARDATTRIBUTES:
					attribute = cardarg
				if cardarg in CARDRANKS:
					rank = cardarg

			print('selecting cards with (name=%s, cardid=%s, rank=%s, attribute=%s) from %s to %s' % (name, cardid, rank, attribute, startdate, enddate))

			if name in US+AQOURS:
				if not membermanager.loaded_member(name):
					mp.fetchwebpage(name)
					mp.parse(name)
					membermanager.load_member(name)

				cards = membermanager.get_member(name).get_cards(cardid, rank, attribute, startdate, enddate)
				print('Found %d %s %s %s card(s)%s.' % (len(cards), attribute if attribute else '', rank if rank else '', name, 'width id #' + str(cardid) if cardid else ''))

				for card in sorted(cards.values(), reverse=True):
					print(card)
			else:
				print('Get member cards error: invalid member name "%s".' % name)

if __name__ == '__main__':
	main()