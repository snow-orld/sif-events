#!/user/bin/env python
# -*- coding: utf8 -*-
"""
@file    constants.py
@author  Cecilia M.
@date    2017-08-30
@version $Id: sifevents.py 01 2017-08-30 15:14: behrisch $

This file contains constants used in the process of parsing and 
analyzing the past events of Japanese version 
based on a local parsed file with info from the wiki page
decaf.kouhi.me/lovelive/index.php?title=List_of_Events
"""

URL = "http://decaf.kouhi.me/lovelive/index.php?title=List_of_Events"
BASEURL = "http://decaf.kouhi.me"
WEBPAGEFILE = "events.html"
PARSEDFILE = "parsedevents.txt"

EVENTTYPES = ['Collection Event', 'Score Match', 'Medley Festival', 'Challenge Festival', 'Touring Rally', 'Friendly Match']

UNITS = [u"u's", u'aqours']
US = ['Honoka', 'Kotori', 'Umi', 'Hanayo', 'Rin', 'Maki', 'Eli', 'Nozomi', 'Nico']
AQOURS = ['Chika', 'You', 'Riko', 'Hanamaru', 'Ruby', 'Yoshiko', 'Dia', 'Kanan', 'Mari']