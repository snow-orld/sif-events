#!/user/bin/env python
# -*- coding: utf8 -*-
"""
@file    imgdownload.py
@author  Cecilia M.
@date    2017-09-11
@version $Id: imgdownload.py 01 2017-09-11 18:51: behrisch $

This script parses and downloads the card image file from
Japanese version based on a local parsed file with info from the wiki page
decaf.kouhi.me/lovelive/index.php?title=[Member_Name]

The original imgdownloader is first finished on 9/09/17 but mistakenly 
deleted due to a miss-hard-reset. The problem of the original script is
it takes an average of 5 or more seconds to parse the dest image link,
6 or more seconds to download each file.

Future Work:
Workerpool may halt at some point that cannot exit by CTRL-C.
Try to use threading instead or multiprocessing module of workerpool.
"""

import os
import sys
import argparse
import codecs
import requests, urllib.request
from bs4 import BeautifulSoup
from datetime import datetime
import workerpool

from constants import *
import membersparse as mp

IMAGEFOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'member', 'img')
WORKER_NUM = 5

def get_options():
	parser = argparse.ArgumentParser(description='Card Image Downloader.')
	parser.add_argument('member', nargs='+', help='Specify the member(s)\' of whose cards to download', choices=US+AQOURS+['a', 'all'])
	parser.add_argument('-r', '--rank', nargs='*', help='Specify the rank(s) of cards to download', choices=['R', 'SR', 'SSR', 'UR'])
	parser.add_argument('-a', '--attribute', nargs='*', help='Specify the attribute(s) of cards to download', choices=CARDATTRIBUTES)
	parser.add_argument('-w', '--worker', type=int, default=WORKER_NUM, help='Specify the number of workers')
	
	args = parser.parse_args()
	return args

def init(args):
	mp.init()

	# member/ folder is created in mp.init() if necessary
	if not os.path.exists(IMAGEFOLDER):
		os.mkdir(IMAGEFOLDER)

	# make sure parsed member file exists to read 1st level image link pointing to image page
	for member in args.member:
		mp.fetchwebpage(member)
		mp.parse(member)

		fullname = mp.nameMap2Fullname[member]
		memberimgfolder = os.path.join(IMAGEFOLDER, fullname)

		if not os.path.exists(memberimgfolder):
			os.mkdir(memberimgfolder)

def get_image_urls(name, ranks, attributes):
	# return the links specified by name, ranks, and attributes
	start = datetime.utcnow()

	fullname = mp.nameMap2Fullname[name]
	parsedfile = os.path.join(mp.MEMBERFOLDER, fullname + '.txt')

	urls = []
	with codecs.open(parsedfile, 'r', encoding='utf-8') as f:
		header = f.readline()
		for line in f:
			rank, attribute, url1, url2 = line.split(';')[1:5]
			if rank in ranks and attribute in attributes:
				if url1 != 'N/A':
					urls.append(url1)
				urls.append(url2)

	end = datetime.utcnow()
	print('Got %s\'s %s %s pre-parsed imgurls in: %s' % (name, ranks, attributes, abs(end - start)))
	
	return urls

def parse_image_url(imgurl):
	# batch process local-file-parsed card img urls (including BASE) of a specified member to return the links of actual original image - called in mass_download
	start = datetime.utcnow()

	req = requests.get(imgurl)
	soup = BeautifulSoup(req.content, "html.parser")
	link = soup.find('div', id='file').a['href']

	del soup

	end = datetime.utcnow()
	print('Parsed %s\'s image urls in: %s' % (imgurl, abs(end - start)))

	return link

def mass_download(name, imgurls):
	# download img file by processing imgurls
	start = datetime.utcnow()

	fullname = mp.nameMap2Fullname[name]
	memberimgfolder = os.path.join(IMAGEFOLDER, fullname)

	class DownloadJob(workerpool.Job):
		def __init__(self, imgurl):
			self.url = imgurl
		def run(self):
			filename = os.path.join(memberimgfolder, self.url.split('File:')[-1])
			if not os.path.exists(filename):
				try:
					link = parse_image_url(self.url)
					urllib.request.urlretrieve(BASEURL+link, filename)
				except requests.exceptions.ConnectionError:
					print('Downloading %s aborted. UnknownProtocol(HTTP 0.0/)\nPlease try again' % self.url)
					pool.terminate()
					pool.join()
				except KeyboardInterrupt:
					print('Called KeyboardInterrupt, terminaing workers')
					pool.terminate()
					pool.join()
			else:
				print('%s already exists' % os.path.relpath(filename))

	pool = workerpool.WorkerPool(size=WORKER_NUM, maxjobs=WORKER_NUM)
	for url in imgurls:
		job = DownloadJob(url)
		pool.put(job)

	# Send shutdown jobs to all threads, and wait until all the jobs have been completed
	pool.shutdown()
	pool.wait()
	del pool

	end = datetime.utcnow()
	print('Downloaded %d %s\s images in: %s' % (len(imgurls), name, abs(end - start)))

def main():
	args = get_options()

	if args.worker:
		WORKER_NUM = args.worker
	if not args.attribute:
		args.attribute = CARDATTRIBUTES
	if not args.rank:
		args.rank = CARDRANKS
	if 'a' in args.member or 'all' in args.member:
		args.member = US+AQOURS

	init(args)

	for member in args.member:
		imageurls = get_image_urls(member, args.rank, args.attribute)
		mass_download(member, imageurls)

if __name__ == '__main__':
	main()