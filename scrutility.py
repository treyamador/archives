import requests,pprint,socket,time,sys,re
from bs4 import BeautifulSoup,Tag
from requests.exceptions import *
from urllib3.exceptions import *
from collections import deque


class URLDirectory:

    def __init__(self):
        self.length = 100
        self._direct = deque(maxlen=self.length)

    def set_base_url(self,url):
        self.url = url

    def push_front(self,args):
        self._direct.append(args)

    def pop_front(self):
        return self._direct.pop()

    def push_back(self,args):
        self._direct.appendleft(args)

    def pop_back(self):
        return self._direct.popleft()

    def size(self):
        return len(self._direct)

    def is_full(self):
        return self.size() == self.length

    def is_empty(self):
        return self.size() == 0

    def front(self):
        element = self.pop_front()
        self.push_front(element)
        return element

    def back(self):
        element = self.pop_back()
        self.push_back(element)
        return element


directory = URLDirectory()
inited = False
def initialize(url):
    directory.set_base_url(url)
    inited = True


def directory_entries():
    return directory._direct


def connect(url):

    def handle_error(err,dur,tries):
        time.sleep(dur)
        print('Handling error after',tries,'tries:')
        print(err.args)

    def retry(err,dur,tries):
        handle_error(err,dur,tries)
        return tries + 1

    def redirect(err,dur,tries):
        handle_error(err,dur,tries)
        if not directory.is_empty():
            return directory.pop_front()
        elif directory.url:
            return directory.url
        else:
            print('System cannot redirect.')
            print('System exited.')
            sys.exit(1)

    def success(res,url):
        directory.push_front(res.url)
        print('Status code',res.status_code)
        return BeautifulSoup(res.text,'lxml'), res

    tries,max_tries = 0,100
    short_pause,long_pause = 15,30

    while tries < max_tries:
        try:
            res = requests.get(url,timeout=1.0)
            res.raise_for_status()
        except ConnectTimeout as err:
            tries = retry(err,short_pause,tries)
        except ReadTimeout as err:
            tries = retry(err,long_pause,tries)
        except socket.timeout as err:
            tries = retry(err,long_pause,tries)
        except Timeout as err:
            tries = retry(err,long_pause,tries)
        except ConnectTimeoutError as err:
            tries = retry(err,short_pause,tries)
        except ReadTimeoutError as err:
            tries = retry(err,long_pause,tries)
        except TimeoutError as err:
            tries = retry(err,long_pause,tries)
        except ConnectionError as err:
            tries = retry(err,short_pause,tries)
        except TooManyRedirects as err:
            url,tries = retry(err,short_pause,tries)
        except HTTPError as err:
            url,tries = retry(err,short_pause,tries)
        except URLRequired as err:
            url,tries = retry(err,short_pause,tries)
        except socket.error as err:
            tries = retry(err,long_pause,tries)
        except RequestException as err:
            handle_error(err,long_pause)
            return None, None
        else:
            return success(res,url)
    return None, None


def print_safe(*text,sep=' ',end='\n'):

    def unicode_print(text,sep=' ',end='\n'):
        try:
            if isinstance(text,str):
                print(text.encode('utf-8'),sep='',end=sep)
        except TypeError as err:
            exception_errs(err)
        except ValueError as err:
            exception_errs(err)
        except AttributeError as err:
            exception_errs(err)

    for txt in text:
        try:
            print(txt,sep='',end=sep)
        except UnicodeEncodeError as err:
            unicode_print(txt)
        except UnicodeDecodeError as err:
            unicode_print(txt)
        except UnicodeError as err:
            unicode_print(txt)
    print('',sep='',end=end)


# make higher fidelity!
def pprint_safe(obj):
    try:
        pprint.pprint(obj)
    except UnicodeEncodeError as err:
        print('Unicode encode error, entry skipped')
    except UnicodeError as err:
        print('Unicode error, entry skipped')
    except (ValueError,AttributeError):
        print('Unknown printing error')


# soup utils
def get_links_destructive(soup):
    links = get_links(soup)
    if soup:
        soup.decompose()
    return links


def get_links(soup):
    if soup:
        return [a['href'] for a in soup.find_all('a') if a.has_attr('href')]


def tag_to_text(tag):
    try:
        if isinstance(tag,Tag):
            return tag.get_text()
        elif isinstance(tag,str):
            return tag
        elif isinstance(tag,int):
            return str(tag)
        else:
            return None
    except TypeError as err:
        tag_error(err,tag)
    except ValueError as err:
        tag_error(err,tag)
    except AttributeError as err:
        tag_error(err,tag)
    return None


# make these more efficient
def clean_deposit_mongo(tag):
    return clean_tag(tag,'$','~$','.','?*')


def clean_extract_mongo(tag):
    return clean_tag(tag,'~$','$','?*','.')


def clean_tag(tag,a,b,c,d):
    try:
        text = tag.get_text().replace(a,b).replace(c,d)
    except TypeError:
        return None
    except ValueError:
        return None
    else:
        return text


