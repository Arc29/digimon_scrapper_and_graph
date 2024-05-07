import requests
import re
import itertools
import json
import sys, traceback
from bs4 import BeautifulSoup

url = "https://wikimon.net/List_of_Digimon"

page = requests.get(url)

soup = BeautifulSoup(page.content, 'html.parser')

results = soup.find_all('table', class_="wikitable")

digi_list = {}
for table in results:
    rows = table.find_all('tr')
    for row in rows:
        row_data = row.find_all('td')
        if len(row_data) > 0:
            digi_obj = {"name": row_data[0].text.strip(), "kanji": row_data[1].text.strip(), "debutYear": row_data[2].text.strip(), "debutMedia": row_data[3].text.strip()}
            digi_list[digi_obj['name']]=digi_obj
            

with open('wikimon_list.json', 'w') as outfile:
    json.dump(digi_list, outfile)