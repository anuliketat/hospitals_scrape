import os
import requests
import pandas as pd
import numpy as np
import re
import time

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from bs4 import BeautifulSoup


DRIVER_PATH = 'C:\\Users\\Anudeep\\Downloads\\chromedriver.exe' # chromedriver.exe path
option = webdriver.ChromeOptions()
option.add_argument('headless')

def get_page_source(url, city):
    '''
    returns source code text file for all the web pages in url
    '''
    print('CITY:', city)
    driver = webdriver.Chrome(DRIVER_PATH, options=option)
    print('Loading page...')
    driver.get(url+city.lower())

    print('saving website source data...')
    results_class = 'u-d-inlineblock u-smallest-font implicit subsection'.replace(' ', '.')
    num_hospitals = int(driver.find_element_by_class_name(results_class).text.strip(' matches found'))
    print('Hospitals found:', num_hospitals)
    scroll = num_hospitals//10 + 1
    for i in range(1, scroll+1):
        driver.execute_script("window.scrollTo(1, 1e+07)")
        pause = 1.5 if i < 10 else 2
        time.sleep(pause)
    # save page source html
    file_name = f'hospitals_{city}.html'
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(driver.page_source)

    print(f'Sourced web page elements data for {scroll} pages')
    print(f'source file saved in {os.path.abspath(file_name)}')
    driver.close()
    return file_name

def scrape_list(html_path, city):
    '''
    html_path: saved html file
    ---------------------------------------
    returns Pandas DataFrame with added attributes
    '''
    with open(html_path, 'r') as data:
        soup = BeautifulSoup(data, 'html.parser')

    card_class = 'u-cushion.u-white-fill.u-normal-text.o-card.o-card--separated.c-list-card'
    names, links, loc = [], [], []
    hosp_list = soup.find_all('div', {'class':card_class.replace('.', ' ')})
    print(f'Scraping list of hospitals ({len(hosp_list)})...')
    for card in hosp_list:
        names.append(card.find('h2').text)
        web_join = 'https://www.practo.com'
        links.append(web_join+card.find('a').get('href'))
        loc.append(card.find('h3').text)

    print(f'hospitals in {city}:', len(links))
    hosp = pd.DataFrame({'name':names, 'url':links, 'loc':loc})
    hosp['city'] = city

    return hosp

def scrape_info(dataframe):
    '''
    dataframe: Pandas dataframe
    --------------------------------------------
    returns Pandas Dataframe with additional scraped attributes
    '''
    links = dataframe['url'].tolist()
    print('Scraping hospital specific information...')
    ratings, full_loc, num_docs, typ = [], [], [], []
    hosp_info, fac_specs = {}, {}
    for link in links:
        page = requests.get(link).content
        soup = BeautifulSoup(page, 'html.parser')
        #rating
        rat = np.NaN
        try:
            rat = soup.find('span', class_='common__star-rating__value').text
        except AttributeError as e:
            print(link, 'NO Rating')
        finally:
            ratings.append(rat)

        try:
            # hospital type
            h2s = soup.find_all('h2', class_='u-spacer--right-thin u-d-inlineblock')
            hosp_type = h2s[0].text
            # doctors
            docs = h2s[1].text.strip(' Doctors')
        except IndexError as e:
            print(link, 'no DOC Info' if docs is None else link, 'no Hospital Type' if hosp_type is None else None)
        finally:
            num_docs.append(docs) if docs else num_docs.append(np.NaN)
            typ.append(hosp_type) if hosp_type else typ.append(np.NaN)
        # full address
        loc_div = None
        try:
            loc_div = soup.find('div', class_='pure-u-1-3 u-cushion--right')
            address = loc_div.find('p', class_='c-profile--details').text.strip('Get Directions')
            if loc_div is not None:
                address = re.sub(r"(\w)([A-Z])", r"\1, \2", address)
            else:
                address = soup.find('p', class_='c-profile--clinic__address').text
        except AttributeError as e:
            print(link, 'No Address found' if address is None else None)
        finally:
            full_loc.append(address) if address else full_loc.append(np.NaN)
        # beds, ambulance
        h3_tags = soup.find_all('h3', {'class':'profile_details u-spacer--top'})
        h3_list = []
        for tag in h3_tags:
            h3_list.append(tag.find('span', class_='u-bold').text)
        hosp_info[link] = h3_list
        # facilities and specialized depts
        h2_tags = soup.find_all('h2')
        dic = {}
        for h2 in h2_tags:
            if ('specialties' in h2.text.lower()) | ('facilities' in h2.text.lower()):
                info_list = []
                try:
                    sibling = h2.find_next_sibling()
                    for i in sibling.find_all('li'):
                        info_list.append(i.get_text())
                        key = h2.text.strip(':').lower()
                        pattern = r'\b(?!facilities\b)\w+' if 'facilities' in key else r'\b(?!specialties\b)\w+'
                        key = re.sub(pattern, '', key).strip()
                        dic[key] = info_list
                        fac_specs[link] = dic
                except AttributeError:
                    print(link, 'No facilities/specialties')
    temp_dic = {}
    for i in links:
        if i not in fac_specs.keys():
            temp_dic[i] = np.NaN
    fac_specs.update(temp_dic)

    dataframe['rating'] = ratings
    dataframe['address'] = full_loc
    dataframe['doctors'] = num_docs
    dataframe['type'] = typ
    dataframe['beds/amb'] = dataframe['url'].map(hosp_info)
    dataframe['fac/specs'] = dataframe['url'].map(fac_specs)
    return dataframe

def scrape_services(dataframe):
    services_dic = {}
    links = dataframe['url'].tolist()
    print('\nScraping services...')
    for link in links:
        url = link+'/services'
        driver = webdriver.Chrome(DRIVER_PATH, options=option)
        driver.get(url) # get services page
        #time.sleep(0.5)
        try:
            # Expand view all
            view_class = '//*[@id="entity"]/span'
            view = driver.find_element_by_xpath(view_class)
            view.click()
        except NoSuchElementException:
            print(link, 'No Services')
        except ElementNotInteractableException:
            continue
        finally:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            list_class = 'pure-u-1-3 u-cushion--right-less'
            serv_list = soup.find_all('div', class_=list_class)
            services_dic[link] = [li.text for li in serv_list] if list_class else np.NaN

    dataframe['services'] = dataframe['url'].map(services_dic)
    return dataframe