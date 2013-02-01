import searching
import os

from sys import argv
from crawler import Crawler

help_msg = """Usage:
python main.py [seed] [max_pages] [max_depth] [sleep time]"""

def main():
    if len(argv) != 5:
        print help_msg
    else:
        crawler = Crawler(argv[1], argv[2], argv[3], argv[4])
        crawler.crawl_web()

if __name__ == '__main__':
	main()


