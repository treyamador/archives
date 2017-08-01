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


def init_journal(title,site,pay,circ,solic,fee):

    def stringify(var):
        if var is None:
            return ' '
        return var

    return {
        'title':stringify(title),
        'website':stringify(site),
        'payment':stringify(pay),
        'circulation':stringify(circ),
        'unsolicited':stringify(solic),
        'fee':stringify(fee)
    }



def print_journal(journal):
    print('Title:',journal['title'])
    print('Website:',journal['website'])
    print('Circulation:',journal['circulation'])
    print('Payment:',journal['payment'])
    print('Unsolicited:',journal['unsolicited'])
    print('Fee:',journal['fee'])
    print('\n')



def get_entry_attr():
    return [
        'title',
        'website',
        'circulation',
        'payment',
        'unsolicited',
        'fee']



def write_html(soup,ext=''):
    with open('html'+str(ext)+'.txt','wb') as f_obj:
        try:
            html = u''+soup.get_text()+'\r\n'
            f_obj.write(html.encode('utf-8'))
        except (AttributeError, TypeError, ValueError):
            pass



def write_journals(journals,keys,filename):
    with open(filename,'wb') as f_obj:
        for journal in journals:
            for key in keys:
                try:
                    entry = u''+key+': '+journal[key]+'\r\n'
                    f_obj.write(entry.encode('utf-8'))
                except (AttributeError,TypeError,ValueError):
                    pass
            f_obj.write('\r\n'.encode('utf-8'))



def write_filtered_journals(journals,keys,filename):

    circu_categ = [
        'Less than 1,000',
        '1,000 to 2,500',
        '2,500 to 5,000',
        '5,000 to 10,000',
        'Greater than 10,000'
    ]

    print(journals)

    with open(filename,'wb') as f_obj:
        for category in circu_categ:
            if category in journals:
                entries = journals[category]
                category_title = u''+category+'\r\n\r\n'
                f_obj.write(category_title.encode('utf-8'))
                for journal in entries:
                    for key in keys:
                        try:
                            entry = u'    '+key+': '+journal[key]+'\r\n'
                            f_obj.write(entry.encode('utf-8'))
                        except (AttributeError,TypeError,ValueError):
                            pass
                    f_obj.write(u'\r\n'.encode('utf-8'))
                f_obj.write(u'\r\n'.encode('utf-8'))



def journal_info(url):
    soup,res = connect(url)
    title = get_text(soup.find('h1',{'class','title'}))
    site = get_link(soup.find('div',{'class','field-name-field-website'}))
    payment = get_field(soup,'field-name-field-pay')
    circ = get_field(soup,'field-name-field-circulation')
    solic = get_field(soup,'field-name-field-unsolicited-submissions')
    fee = get_field(soup,'field-name-field-reading-fee')
    return init_journal(title,site,payment,circ,solic,fee)



def filter_journals(journals):
    filtered = {}
    for journal in journals:
        print_journal(journal)
        if 'Cash' in journal['payment'] and 'Yes' in journal['unsolicited']:
            if journal['circulation'] != ' ':
                if 'circulation' not in filtered:
                    filtered[journal['circulation']] = []
                filtered[journal['circulation']].append(journal)
    return filtered



def sort_circulation_journals(journals):
    pass



def scrape(url):

    journals = []
    keys = get_entry_attr()
    soup,res = connect(url)
    links = gather_journal_links(soup,url)
    for link in links[103:105]:
        journals.append(journal_info(link))
    write_journals(journals,keys,'all_journals.txt')
    filtered = filter_journals(journals)
    #write_journals(filtered,keys,'filtered_journals.txt')
    write_filtered_journals(filtered,keys,'filtered_journals.txt')



def driver():
    lit_url = ''+\
        'https://www.pw.org/literary_magazines'+\
        '?field_genres_value=All'+\
        '&taxonomy_vocabulary_20_tid=All'+\
        '&simsubs=All&items_per_page=All'

    scrape(lit_url)


driver()


