import datastore
import searching
import jinja2
import os
import webapp2
import cProfile, pstats

from sys import argv
from crawler import Crawler
from google.appengine.api import taskqueue
from google.appengine.api import users

jinja_env = jinja2.Environment(autoescape=True,
	loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

class Handler(webapp2.RequestHandler):
	"""Base class that handles writing and rendering (from Steve Huffman, CS 253, Udacity)"""
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, ** params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class MainHandler(Handler):

	def get(self):
		self.write("Hello!")

class CrawlWorker(Handler):
	def post(self):
		seed = self.request.get('seed')
		maxpages = int(self.request.get('maxpages'))
		maxdepth = int(self.request.get('maxdepth'))
		rest = int(self.request.get('rest'))
		my_crawler = Crawler(seed, maxpages, maxdepth, rest)
		my_crawler.crawl_web()
		my_crawler.compute_ranks()

class AdminHandler(Handler):
	def get(self):
		user = users.get_current_user()
		if not user:
			self.response.out.write("<a href='%s'>Sign in</a>" % users.create_login_url())

		else:
			self.render('admin.html')

	def post(self):
		seed = self.request.get('seed')
		maxpages = self.request.get('maxpages')
		maxdepth = self.request.get('maxdepth')
		rest = self.request.get('rest')

		my_params = {'seed': seed, 'maxpages': maxpages, 'maxdepth': maxdepth, 'rest': rest}

		taskqueue.add(url='/crawlworker', params={'seed': seed, 'maxpages': maxpages, 'maxdepth': maxdepth, 'rest': rest})
		self.redirect('/')

app = webapp2.WSGIApplication([('/', MainHandler),
							   ('/crawlworker', CrawlWorker),
							   ('/admin', AdminHandler)],
								debug=True)


def main():
	run_wsgi_app(app)

if __name__ == '__main__':
	main()


