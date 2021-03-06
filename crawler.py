import urllib2
import re
import time

from google.appengine.ext import db
from bs4 import BeautifulSoup
from urlparse import urljoin



def start_crawling():
	my_crawler = Crawler('http://google.com', 100, 10)
	my_crawler.crawl_web()
	my_crawler.compute_ranks()


class Links(db.Model):
	url = db.LinkProperty()
	meta_description = db.StringProperty()
	rank = db.FloatProperty()

class Keywords(db.Model):
	"""Key name is url and keyword concatenated. Parent is the link."""
	urls = db.StringListProperty(required = True)
	keyword = db.TextProperty(required = True)

class Crawler:

	def __init__(self, seed=None, max_pages=None, max_depth=None, sleep_time=None):
		self.seed, self.max_pages, self.max_depth, self.sleep_time = seed, max_pages, max_depth, sleep_time
		self.index = {}
		self.graph = {}
		self.ranks = {}

	def crawl_web(self, seed=None, max_depth=None, max_pages=None):
		if seed is None:
			seed = self.seed
		if max_depth is None:
			max_depth = self.max_depth
		if max_pages is None:
			max_pages = self.max_pages

		tocrawl = [[seed, 0]]
		crawled = []
		total_crawled = 0

		while tocrawl:
			page, depth = tocrawl.pop(0)

			if page not in crawled and depth <= max_depth:		
				page_content = self._open_url(page)
				soup = BeautifulSoup(page_content)
				self._add_page_to_index(page, soup)

				outlinks = []
				for link in soup.find_all('a'):
					new_url =  link.get('href')
					new_url = self._check_relative(new_url, page)
					if new_url is not None:
						tocrawl.append([new_url,depth+1])
						outlinks.append(new_url)

				crawled.append(page)
				total_crawled += 1
				time.sleep(self.sleep_time)
				self.graph[page] = outlinks

			if total_crawled >= max_pages:
				return



	def _open_url(self, url):
		"""Open a url with urllib2. Put here so it makes catching exceptions easier."""
		try:
			return urllib2.urlopen(url)
		except urllib2.URLError as e:
			print 'URLError = ' + str(e.reason)
		except urllib2.HTTPError as e:
			print 'HTTPError = ' + str(e.code)
		except ValueError as e:
			print 'Not a proper URL'


	def _check_relative(self, url, base_url):
		"""Checks if a url is relative. If so, uses urljoin to join it w/base_url"""
		url_re = r'http://.*'
		if url and not re.match(url_re, url):
			if 'javascript:void' in url:
				return None
			return urljoin(base_url, url)
		else:
			return url

	def _add_page_to_index(self, page, soup):
		meta_keywords = soup.find('meta', {'name': 'keywords'})
		meta_description = soup.find('meta', {'name': 'description'})

		page_rank = 0.0
		if page in self.ranks:
			page_rank = self.ranks[page]


		#Add to the database if it's a new link	
		new_key = page
		Links.get_or_insert(new_key,url=page,meta_description=meta_description['content'],rank=page_rank)

		if meta_keywords:
			meta_keywords =  meta_keywords['content']
			meta_keywords = meta_keywords.split(',')
			self._add_to_index(meta_keywords,page)

		if meta_description:
			meta_description = meta_description['content']
			meta_list_description = meta_description.split(',')
			self._add_to_index(meta_list_description,page)

		page_content = self._split_string(soup.get_text())
		if page_content:
			self._add_to_index(page_content,page)


	def _add_to_index(self, words, page):

		for word in words:
			keyword_cursor = Keywords.get_by_key_name(word)
			if not keyword_cursor:
				urls = [page]
				new_keyword = Keywords(keyword=word, urls=urls, key_name=word)
				new_keyword.put()
			else:
				if page not in keyword_cursor.urls:
					keyword_cursor.urls.append(page)
					keyword_cursor.put()


	def _split_string(self, source):
		splitlist = ' ,!".?<>|{}\'\\\(\)'
		for sep in splitlist[1:]:
			source = source.replace(sep, splitlist[0])
		source = source.split(splitlist[0])
		for word in source[:]:
			if word == '':
				source.remove(word)
		return source

	def compute_ranks(self):
		damping = 0.8
		num_loops = 10

		npages = len(self.graph)

		for page in self.graph:
			self.ranks[page] = 1.0 / npages

		for i in range(0, num_loops):
			newranks = {}
			for page in self.graph:
				newrank = (1 - damping) / npages
				for node in self.graph:
					if page in self.graph[node]:
						newrank = newrank + damping * (self.ranks[node] / len(self.graph[node]))
					newranks[page] = newrank
			self.ranks = newranks


	def _ancestor_key(self, kind, id_or_name):
		return db.Key.from_path(kind, id_or_name)

	def _get_parent(self, entity_id):
		return entity_id.key.parent().get()
