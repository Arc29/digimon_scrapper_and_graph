import requests
import re
import itertools
import json
import sys, traceback
from bs4 import BeautifulSoup

digimon_fandom_url = "https://digimon.fandom.com"

page = requests.get(digimon_fandom_url+"/wiki/List_of_Digimon")

soup = BeautifulSoup(page.content, 'html.parser')

results = soup.find(id='mw-content-text')

# with open("demo.html", "w", encoding="utf-8") as f:
#     f.write(results.prettify())

# print(results.prettify())

digimon_tables = results.find_all('table', class_='sortable')

# digimon_list = {}

# try:
#     with open('digi_list_2.json') as infile:
#         digimon_list = json.load(infile)
# except Exception:
#     print("Exception in user code:")
#     print("-"*60)
#     traceback.print_exc(file=sys.stdout)
#     print("-"*60)

digimon_row_list = []
no_jap_name_list = []
try:
    for table in digimon_tables:
        digimon_row_list.extend(table.find_all('tr'))

    stop = len(digimon_row_list)  # Test limiter
    bad_strings = [", ","(",") ",")\n","\n","Ja:","En:"," and ","/","","and "," and",", and ",", ",",","\"",]
    counter=1
    for digimon_data in itertools.islice(digimon_row_list, 0, stop):
        tag = digimon_data.find('b')
        if tag != None:
            
            digi_obj = {'name': '', 'jap_name': '', 'url': '', 'image': '', 'level': '', 'type': [], 'attribute': [], 'family': [], 'size': [], 'debut': [], 'priorForms': [], 'nextForms': [], 'slideForms': [
            ], 'digifuseForms': [], 'partners': [], 'voiceActors': [], 'cards': [], 'otherNames': [], 'variations': [], 'groups': [], 'description': 'No description found', 'attacks': []}
            digi_obj["name"] = tag.text
            # digimon_list.append(tag.string)
            anchor = tag.find('a')
            print(digi_obj["name"],counter)
            counter+=1
            if anchor and anchor.has_attr('href'):
                digi_obj['url']=anchor['href']
                digimon_page = requests.get(digimon_fandom_url+anchor['href'])
                # Get the soup of corresponding page
                digimon_page_soup = BeautifulSoup(
                    digimon_page.content, 'html.parser')
                main_p = None
                main_ps = digimon_page_soup.find_all('p')
                for pp in main_ps:
                    if pp.aside != None:
                        main_p = pp
                        break
                if main_p == None:
                    # digimon_list[digi_obj['name']]=digi_obj
                    # changed = True
                    continue
                info_table=main_p.find('aside')
                if info_table != None:
                    if info_table.h2 != None:
                        print(info_table.h2.text)
                        jap_name = info_table.h2.find('span', lang='ja-Latn-hepburn', recursive=True)
                        if jap_name == None:
                            no_jap_name_list.append(digi_obj['name'])
                        else:
                            digi_obj["jap_name"]=jap_name.text
                            digimon_row_list.append(digi_obj)
                            print(digi_obj['jap_name'])
                    # if info_table.figure != None:
                    #     digi_obj["image"]=info_table.figure.a['href']
                    # print(digi_obj["image"])
                    # rows = info_table.find_all('div',recursive=False)
    print('No japanese names found:', no_jap_name_list)
except Exception:
    print("Exception in user code:")
    print("-"*60)
    traceback.print_exc(file=sys.stdout)
    print("-"*60)
finally:
    with open('no_jap.json', 'w') as outfile:
        json.dump(no_jap_name_list, outfile)
    with open('digi_jap.json', 'w') as outfile:
        json.dump(digimon_row_list, outfile)