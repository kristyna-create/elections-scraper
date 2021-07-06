import csv
import sys
import os

import requests
from bs4 import BeautifulSoup as BS

def has_headers_but_no_class(tag):
    return tag.has_attr('headers') and not tag.has_attr('class')

def extract_res(url):

    dict_muni = {}

    try:
        r = requests.get(url)
        r.raise_for_status()
        soup = BS(r.text, "html.parser")
    except requests.exceptions.HTTPError:
        print('Could not retrieve the page')
    except:
        print(sys.exc_info()[:1])

    muni_number = []
    muni_url = []

    for id in soup.find_all('td', {'class': 'cislo'}):
        muni_number.append(id.string)
        for i in id.children:
            muni_url.append('https://volby.cz/pls/ps2017nss/' + i.get('href'))

    muni_list = []
    for munis in soup.find_all(has_headers_but_no_class):
        muni_list.append(munis.string)

    dict_muni['muni_number'] = muni_number
    dict_muni['muni_url'] = muni_url
    dict_muni['muni_list'] = muni_list

    return dict_muni

def extract_muni_results(muni_id, muni, key_url):
    try:
        r = requests.get(key_url)
        r.raise_for_status()
        soup_muni = BS(r.text, "html.parser")
    except requests.exceptions.HTTPError:
        print('Could not retrieve the page for municipality = {}'.format(muni))
    except:
        print(sys.exc_info()[:1])

    # registered = Number of registered voters
    # envelopes = Votes cast
    # valid = Valid votes

    summary_table = soup_muni.find_all('table')[0]  # always the first table on the page

    party_votes_res = {}

    party_votes_res['code'] = muni_id
    party_votes_res['location'] = muni

    party_votes_res['registered'] = summary_table.find_all('td', {'class': 'cislo'})[3].string
    party_votes_res['envelopes'] = summary_table.find_all('td', {'class': 'cislo'})[6].string
    party_votes_res['valid'] = summary_table.find_all('td', {'class': 'cislo'})[7].string


    for table in soup_muni.find_all('table')[1:]:
        for structure in table.find_all('tr')[2:]:
            row_info = [content.string for content in structure if content.string != '\n']
            party_votes_res[row_info[1]] = row_info[2]

    return party_votes_res

def write_results(party_votes_res, report_name):
    # header: code, location, registered, envelopes, valid, dict.keys

    target_header = list(party_votes_res.keys())

    report_existed = report_name + '.csv' in os.listdir()  # check if file exists already
    mode = 'a' if report_existed else 'w'

    with open(report_name + '.csv', mode, encoding="utf-8", newline='') as file:
        writer = csv.writer(file)
        if not report_existed:
            writer.writerow(target_header)  # if file does not exist, we will fill in the header first
        writer.writerow(list(party_votes_res.values()))


def muni_extract_and_write(dict_muni, report_name):
    for muni in range(len(dict_muni['muni_number'])):
        muni_id = dict_muni['muni_number'][muni]
        muni_name = dict_muni['muni_list'][muni]
        key_url = dict_muni['muni_url'][muni]

        party_votes_res = extract_muni_results(muni_id, muni_name, key_url)

        write_results(party_votes_res, report_name)



# Extract election results for all municipalities in a chosen district:
url_district = 'https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101' # insert link from https://volby.cz/pls/ps2017nss/ps3?xjazyk=CZ depending on the chosen district

report_name = 'Benesov' # insert report name without .csv


muni_extract_and_write(dict_muni=extract_res(url=url_district), report_name=report_name)














