# entry point
from discography import Discography
from database import Database
from scraper import Scraper
from scrutility import pprint_safe


def driver():
    url = 'http://www.metal-archives.com/band/random'
    db = Database()
    scraper = Scraper(url)

    for i in range(1000):
        discog = scraper.scrape(url)
        if discog:
            db.insert(discog)


if __name__ == '__main__':
    driver()


