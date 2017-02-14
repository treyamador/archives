# scraper for metal archives web site
from scrutility import get_links, get_links_destructive, tag_to_text
from scrutility import clean_deposit_mongo, clean_extract_mongo
from scrutility import initialize, connect, pprint_safe
from discography import Discography
import re


class Scraper:


    def __init__(self,url):
        self.defurl = url
        initialize(self.defurl)


    def artist_info(self,soup):
        artist = soup.find('div',{'id':'band_info'})
        if artist:
            artist_tag = artist.find('h1',{'class':'band_name'})
            if artist_tag:
                artist_text = tag_to_text(artist_tag)
            location_tag = artist.find('dl',{'class':'float_left'}).find('a')
            if location_tag:
                location_text = tag_to_text(location_tag)
            genre_tag = artist.find('dl',{'class':'float_right'}).find('dd')
            if genre_tag:
                genre_text = re.split(r',\s',tag_to_text(genre_tag))
            return [artist_text,genre_text,location_text]


    def get_id(self,res):
        url = res.url
        if isinstance(url,str):
            return url.rsplit('/',1)[-1]


    def find_discog(self,soup):
        tab = soup.find('div',{'id':'band_disco'})
        if tab:
            for link in get_links_destructive(tab):
                if 'all' in link:
                    return connect(link)


    def collect_discog(self,soup,id,artist,genre,location):
        discog = Discography(id,artist,genre,location)
        for entry in soup.find('tbody').find_all('tr'):
            elements = [clean_deposit_mongo(e) for e in entry.find_all('td') if e]
            if elements:
                elements[3:] = [e for e in re.split(r'[(|)|\s]',elements[-1]) if e]
                discog.add(*self.prep_list(elements))
        return discog


    def prep_list(self,elems):
        while len(elems) < 5:
            elems.append('')
        return elems


    def scrape(self,url):
        soup,res = connect(url)
        if soup:
            id = self.get_id(res)
            artist,genre,location = self.artist_info(soup)
            discog_soup,res = self.find_discog(soup)
            if discog_soup:
                return self.collect_discog(discog_soup,id,artist,genre,location)

