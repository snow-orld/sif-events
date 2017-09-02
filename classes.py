#!/user/bin/env python
# -*- coding: utf8 -*-
"""
@file    classes.py
@author  Cecilia M.
@date    2017-09-01
@version $Id: classes.py 01 2017-09-01 22:02: behrisch $

This script descrbes the basic component that appears 
in the SIF game.
"""

from constants import *
from random import random

class Card(object):
	""" Base Class for all cards in the game"""
	def __init__(self, cid, name, attribute, rank, maxpoint=0, skill='None', effect='', leaderskill='None', leadereffect=''):
		super(Card, self).__init__()
		self.id = int(cid)	# id of card across the game
		self.name = name	# member name of the card
		self.attribute = attribute	# smile, pure, or cool
		self.rank = rank	# N, R, SR, SSR, UR
		self.maxpoint = int(maxpoint)	# max attribute point when reaching max level when idolized

		# skill fields are None and '' for N cards
		self.skill = skill	# skill name of the card
		self.effect = effect	# detail of the skill effects
		self.leaderskill = leaderskill	# leader skill name of the card
		self.leadereffect = leadereffect	# detail of leader skill effects

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

	def addskill(self, skill):
		pass

class NCard(Card):
	"""Class for N Card"""
	def __init__(self, cid, name, attribute, maxpoint):
		super(NCard, self).__init__(cid, name, attribute, 'N', maxpoint)
		self.maxlevel = 30
		self.maxbond = 25
		
class RCard(Card):
	"""Class for R Card"""
	def __init__(self, cid, name, attribute, maxpoint, skill, effect, leaderskill, leadereffect):
		super(RCard, self).__init__(cid, name, attribute, 'R', maxpoint, skill, effect, leaderskill, leadereffect)
		self.maxlevel = 40
		self.maxbond = 100
		self.skillslot = 1
		self.maxskillslot = 2

class SRCard(Card):
	"""Class for SR Card"""
	def __init__(self, cid, name, attribute, maxpoint, skill, effect, leaderskill, leadereffect):
		super(SRCard, self).__init__(cid, name, attribute, 'SR', maxpoint, skill, effect, leaderskill, leadereffect)
		self.maxlevel = 60
		self.maxbond = 250
		self.skillslot = 2
		self.maxskillslot = 4
		
class SSRCard(Card):
	"""Class for SSR Card"""
	def __init__(self, cid, name, attribute, maxpoint, skill, effect, leaderskill, leadereffect):
		super(SSRCard, self).__init__(cid, name, attribute, 'SSR', maxpoint, skill, effect, leaderskill, leadereffect)
		self.maxlevel = 70
		self.maxbond = 375
		self.skillslot = 3
		self.maxskillslot = 6
		
class URCard(Card):
	"""Class for UR Card"""
	def __init__(self, cid, name, attribute, maxpoint, skill, effect, leaderskill, leadereffect):
		super(URCard, self).__init__(cid, name, attribute, 'UR', maxpoint, skill, effect, leaderskill, leadereffect)
		self.maxlevel = 80
		self.maxbond = 500
		self.skillslot = 4
		self.maxskillslot = 8

class URGiftCard(URCard):
	"""Class for UR Card given as a gift"""
	def __init__(self, cid, name, attribute, maxpoint, skill, effect, leaderskill, leadereffect):
		super(URGiftCard, self).__init__(cid, name, attribute, maxpoint, skill, effect, leaderskill, leadereffect)
		self.idolize()
		self.skillslot = 2
		self.maxskillslot = 2

if __name__ == '__main__':
	# unit test
	for rank in CARDRANKS:
		cid = 0
		name = US[int(random() * len(US))]
		attribute = CARDATTRIBUTES[int(random() * len(CARDATTRIBUTES))]
		if rank == 'N':
			card = NCard(cid, name, attribute, 0)
		if rank == 'R':
			card = RCard(cid, name, attribute, 0, '', '', '', '')
		if rank == 'SR':
			card = SRCard(cid, name, attribute, 0, '', '', '', '')
		if rank == 'SSR':
			card = SSRCard(cid, name, attribute, 0, '', '', '', '')
		if rank == 'UR':
			card = URCard(cid, name, attribute, 0, '', '', '', '')
		if rank == 'UR-GIFT':
			card = URGiftCard(cid, name, attribute, 0, '', '', '', '')
		print('%s\t#%d%s%s\t%s\tmax %d\tlevel %d/%d\tbond %d/%d\tskillslot %d/%d' % (card.name, card.id, ' ' * (7-len(str(card.id))), card.rank, card.attribute, card.maxpoint, card.level, card.maxlevel, card.bond, card.maxbond, card.skillslot, card.maxskillslot))
