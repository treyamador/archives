# a literary review scraper
import requests, socket, time, datetime
from bs4 import BeautifulSoup, Tag
from requests import exceptions
from urllib import request



def connect(url):

    def request_error(err):
        print(err)
        time.sleep(5)

    def success(res):
        print('Connected to',res.url,'\n')
        return BeautifulSoup(res.text,'lxml'), res

    err_count = 0
    while err_count < 5:
        try:
            res = requests.get(url)
            res.raise_for_status()
        except requests.ConnectTimeout as err:
            request_error(err)
        except requests.ConnectionError as err:
            request_error(err)
        except requests.ReadTimeout as err:
            request_error(err)
        except socket.timeout as err:
            request_error(err)
        except requests.RequestException as err:
            request_error(err)
        except requests.HTTPError as err:
            request_error(err)
        except requests.Timeout as err:
            request_error(err)
        except requests.TooManyRedirects as err:
            request_error(err)
        except requests.URLRequired as err:
            request_error(err)
        except socket.error as err:
            request_error(err)
        else:
            return success(res)
        finally:
            err_count += 1



def gather_journal_links(soup,url):
    links = []
    base_url = url.rsplit('/',1)[0]
    for entry in soup.find_all('h2',{'class','field-content'}):
        anchor = entry.find('a')
        if anchor.has_attr('href'):
            links.append(base_url+anchor['href'])
    return links



def get_link(soup):
    try:
        anchor = soup.find('a')
        if anchor.has_attr('href'):
            return anchor['href']
    except (AttributeError,TypeError,ValueError):
        return None



def get_text(soup):
    try:
        text = soup.get_text()
    except (AttributeError,TypeError,ValueError):
        return None
    else:
        return text



def get_field(soup,field_name):
    try:
        field_tag = soup.find('div',{'class',field_name})
        field_text = field_tag.find('div',{'class','field-item'})
        return field_text.get_text()
    except (AttributeError,TypeError,ValueError):
        return None



class Journal:

    def __init__(self,title,site,pay,circ,solic,fee):
        self.title = self.stringify(title)
        self.website = self.stringify(site)
        self.payment = self.stringify(pay)
        self.circulation = self.stringify(circ)
        self.unsolicited = self.stringify(solic)
        self.fee = self.stringify(fee)

    def stringify(self,var):
        if var is None:
            return '*'
        return var


def init_journal(title,site,pay,circ,solic,fee):

    def stringify(var):
        if var is None:
            return ''
        return var

    return {
        'title':stringify(title),
        'website':stringify(site),
        'payment':stringify(pay),
        'circulation':stringify(circ),
        'unsolicited':stringify(solic),
        'fee':stringify(fee)
    }


def journal_info(url):
    soup,res = connect(url)
    title = get_text(soup.find('h1',{'class','title'}))
    website = get_link(soup.find('div',{'class','field-name-field-website'}))
    payment = get_field(soup,'field-name-field-pay')
    circulation = get_field(soup,'field-name-field-circulation')
    unsolicited = get_field(soup,'field-name-field-unsolicited-submissions')
    fee = get_field(soup,'field-name-field-reading-fee')
    #return Journal(title,website,payment,circulation,unsolicited,fee)
    return init_journal(title,website,payment,circulation,unsolicited,fee)



def scrape(url):
    soup,res = connect(url)
    links = gather_journal_links(soup,url)
    for link in links[100:105]:
        journal = journal_info(link)
        print('Title:',journal['title'])
        print('Website:',journal['website'])
        print('Circulation:',journal['circulation'])
        print('Payment:',journal['payment'])
        print('Unsolicited:',journal['unsolicited'])
        print('Fee:',journal['fee'])
        print('\n')



def driver():
    lit_url = ''+\
        'https://www.pw.org/literary_magazines'+\
        '?field_genres_value=All'+\
        '&taxonomy_vocabulary_20_tid=All'+\
        '&simsubs=All&items_per_page=All'

    scrape(lit_url)


driver()


