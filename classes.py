#!/user/bin/env python
# -*- coding: utf8 -*-
"""
@file    classes.py
@author  Cecilia M.
@date    2017-09-01
@version $Id: classes.py 03 2017-09-08 18:51: behrisch $

This script descrbes the basic component that appears 
in the SIF game.
"""

import re
from datetime import date

from constants import *
from random import random

class Card(object):
	""" Base Class for all cards in the game"""
	def __init__(self, cid, name, attribute, rank, normalimagelink, idolizedimagelink, maxsmile=0, maxpure=0, maxcool=0, skill='None', effect='', leaderskill='None', leadereffect='', version='N/A', releasedate='N/A'):
		super(Card, self).__init__()
		self.id = int(cid[1:])	# id of card across the game, cid is of format #\d+
		self.name = name	# member name of the card
		self.attribute = attribute	# smile, pure, or cool
		self.rank = rank	# N, R, SR, SSR, UR
		self.image1 = normalimagelink 	# 'N/A' for pre-transformed cards
		self.image2 = idolizedimagelink	# idolized image link (both include BASEURL)
		self.maxsmile = int(maxsmile)	# attribute point when reaching max level when idolized
		self.maxpure = int(maxpure)
		self.maxcool = int(maxcool)


		# skill fields are None and '' for N cards
		self.skill = skill	# skill name of the card
		self.effect = effect	# detail of the skill effects
		self.leaderskill = leaderskill	# leader skill name of the card
		self.leadereffect = leadereffect	# detail of leader skill effects

		# card version is not presented in R card
		self.version = version

		# release date may be missing for some cards that is distributed in special method
		self.releasedate = 'N/A'
		if re.search(r'^\d\d\d\d-\d\d-\d\d$', releasedate):
			y, m, d = [int(s) for s in releasedate.split('-')]
			self.releasedate = date(y, m, d)
		else:
			self.notation = releasedate

		# common attributes
		self.isidolized = False
		self.ismaxbond = False
		self.ismaxlevel = False

		# common numerical details
		self.level = 1
		self.bond = 0

		# different numerical details based on card rank and if card is idolized
		self.maxlevel = 0
		self.maxbond = 0
		self.skillslot = 0
		self.maxskillslot = 0

	# comparator: http://pythoncentral.io/how-to-sort-python-dictionaries-by-key-or-value/
	def __cmp__(self, other):
		# print(self.get_maxpoint(), other.get_maxpoint())
		return self.get_maxpoint().__cmp__(other.get_maxpoint())

	# representation of object
	def __repr__(self):
		return '{}: {}\t#{}\t{}{}{}\t{} ({},{},{})\t{}\t{}\n\timage(normal): {}\n\timage(idolized): {}'.format(self.__class__.__name__,
			self.name,
			self.id,
			self.rank,
			' ' * (4 - len(self.rank)),
			self.attribute,
			self.get_maxpoint(),
			self.maxsmile,
			self.maxpure,
			self.maxcool,
			self.releasedate if self.releasedate != 'N/A' else self.notation,
			self.version,
			self.image1,
			self.image2,
			)

	def get_maxpoint(self):
		if self.attribute == 'Smile':
			return self.maxsmile
		elif self.attribute == 'Pure':
			return self.maxpure
		else:
			return self.maxcool

	def idolize(self, card=None):
		self.maxbond *= 2
		if self.rank == 'N':
			self.maxlevel += 10
		else:
			self.maxlevel += 20
		if card:
			if not self.isidolized:
				self.skillslot += 1
			else:
				self.skillslot += 2
			self.skillslot = min(self.maxskillslot, self.skillslot)

		self.isidolized = True

	def practice(self, exprience):
		pass

class NCard(Card):
	"""Class for N Card"""
	def __init__(self, cid, name, attribute, normalimagelink, idolizedimagelink, maxsmile, maxpure, maxcool):
		super(NCard, self).__init__(cid, name, attribute, 'N', normalimagelink, idolizedimagelink, maxsmile, maxpure, maxcool)
		self.maxlevel = 30
		self.maxbond = 25
		
class RCard(Card):
	"""Class for R Card"""
	def __init__(self, cid, name, attribute, normalimagelink, idolizedimagelink, maxsmile, maxpure, maxcool, skill, effect, leaderskill, leadereffect, version, releasedate):
		super(RCard, self).__init__(cid, name, attribute, 'R', normalimagelink, idolizedimagelink, maxsmile, maxpure, maxcool, skill, effect, leaderskill, leadereffect, version, releasedate)
		self.maxlevel = 40
		self.maxbond = 100
		self.skillslot = 1
		self.maxskillslot = 2

class SRCard(Card):
	"""Class for SR Card"""
	def __init__(self, cid, name, attribute, normalimagelink, idolizedimagelink, maxsmile, maxpure, maxcool, skill, effect, leaderskill, leadereffect, version, releasedate):
		super(SRCard, self).__init__(cid, name, attribute, 'SR', normalimagelink, idolizedimagelink, maxsmile, maxpure, maxcool, skill, effect, leaderskill, leadereffect, version, releasedate)
		self.maxlevel = 60
		self.maxbond = 250
		self.skillslot = 2
		self.maxskillslot = 4
		
class SSRCard(Card):
	"""Class for SSR Card"""
	def __init__(self, cid, name, attribute, normalimagelink, idolizedimagelink, maxsmile, maxpure, maxcool, skill, effect, leaderskill, leadereffect, version, releasedate):
		super(SSRCard, self).__init__(cid, name, attribute, 'SSR', normalimagelink, idolizedimagelink, maxsmile, maxpure, maxcool, skill, effect, leaderskill, leadereffect, version, releasedate)
		self.maxlevel = 70
		self.maxbond = 375
		self.skillslot = 3
		self.maxskillslot = 6
		
class URCard(Card):
	"""Class for UR Card"""
	def __init__(self, cid, name, attribute, normalimagelink, idolizedimagelink, maxsmile, maxpure, maxcool, skill, effect, leaderskill, leadereffect, version, releasedate):
		super(URCard, self).__init__(cid, name, attribute, 'UR', normalimagelink, idolizedimagelink, maxsmile, maxpure, maxcool, skill, effect, leaderskill, leadereffect, version, releasedate)
		self.maxlevel = 80
		self.maxbond = 500
		self.skillslot = 4
		self.maxskillslot = 8

class URGiftCard(URCard):
	"""Class for UR Card given as a gift"""
	def __init__(self, cid, name, attribute, normalimagelink, idolizedimagelink, maxsmile, maxpure, maxcool, skill, effect, leaderskill, leadereffect, version, releasedate):
		super(URGiftCard, self).__init__(cid, name, attribute, normalimagelink, idolizedimagelink, maxsmile, maxpure, maxcool, skill, effect, leaderskill, leadereffect, version, releasedate)
		self.idolize()
		self.skillslot = 2
		self.maxskillslot = 2

if __name__ == '__main__':
	# unit test
	for rank in CARDRANKS:
		cid = '#0'
		name = US[int(random() * len(US))]
		attribute = CARDATTRIBUTES[int(random() * len(CARDATTRIBUTES))]
		if rank == 'N':
			card = NCard(cid, name, attribute, 'N/A', 'N/A', 0, 0, 0)
		if rank == 'R':
			card = RCard(cid, name, attribute, 'N/A', 'N/A', 1, 1, 1, '', '', '', '', '', '')
		if rank == 'SR':
			card = SRCard(cid, name, attribute, 'N/A', 'N/A', 2, 2, 2, '', '', '', '', '', '')
		if rank == 'SSR':
			card = SSRCard(cid, name, attribute, 'N/A', 'N/A', 3, 3, 3, '', '', '', '', '', '')
		if rank == 'UR':
			card = URCard(cid, name, attribute, 'N/A', 'N/A', 4, 4, 4, '', '', '', '', '', '')
		if rank == 'UR-GIFT':
			card = URGiftCard(cid, name, attribute, 'N/A', 'N/A', 4, 4, 4, '', '', '', '', '', '')
		print('%s\t#%d%s%s\t%s\tmax %d|%d,%d,%d\tlevel %d/%d\tbond %d/%d\tskillslot %d/%d' % (card.name, card.id, ' ' * (7-len(str(card.id))), card.rank, card.attribute, card.get_maxpoint(), card.maxsmile, card.maxpure, card.maxcool, card.level, card.maxlevel, card.bond, card.maxbond, card.skillslot, card.maxskillslot))
