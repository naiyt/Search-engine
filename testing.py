from crawler import Crawler
my_crawler = Crawler('http://google.com', 4, 10)
my_crawler.crawl_web()
my_crawler.compute_ranks()