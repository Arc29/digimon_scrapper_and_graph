import requests
import re
import itertools
import json
import sys, traceback
from bs4 import BeautifulSoup


def delete_sups(content):
    for sup in content('sup'):
        sup.decompose()


digimon_fandom_url = "https://digimon.fandom.com"


page = requests.get(digimon_fandom_url+"/wiki/List_of_Appmon")

soup = BeautifulSoup(page.content, 'html.parser')

results = soup.find(id='mw-content-text')

# with open("demo.html", "w", encoding="utf-8") as f:
#     f.write(results.prettify())

# print(results.prettify())

appmon_tables = results.find_all('table', class_='sortable')

appmon_list = {}

try:
    with open('appmon_list.json') as infile:
        appmon_list = json.load(infile)
except Exception:
    print("Exception in user code:")
    print("-"*60)
    traceback.print_exc(file=sys.stdout)
    print("-"*60)

changed = False

appmon_row_list = []
try:
    for table in appmon_tables:
        appmon_row_list.extend(table.find_all('tr'))

    stop = len(appmon_row_list)  # Test limiter
    bad_strings = [", ","(",") ",")\n","\n","Ja:","En:"," and ","/","","and "," and",", and ",", ",",","\"",]
    counter=1
    for appmon_data in itertools.islice(appmon_row_list, 0, stop):
        tag = appmon_data.find('b')
        if tag != None:
            if tag.text in appmon_list:
                continue
            appmon_obj = {'name': '', 'url': '', 'image': '', 'grade': '', 'type': '', 'appli': '', 'power': '', 'debut': [], 'priorForms': [], 'nextForms': [],
             'buddies': [], 'voiceActors': [], 'cards': [], 'otherNames': [], 'variations': [], 'groups': [], 'description': 'No description found', 'attacks': []}
            appmon_obj["name"] = tag.text
            # appmon_list.append(tag.string)
            anchor = tag.find('a')
            print(appmon_obj["name"],counter)
            counter+=1
            if anchor and anchor.has_attr('href'):
                appmon_obj['url']=anchor['href']
                appmon_page = requests.get(digimon_fandom_url+anchor['href'])
                # Get the soup of corresponding page
                appmon_page_soup = BeautifulSoup(
                    appmon_page.content, 'html.parser')
                main_p = None
                main_ps = appmon_page_soup.find_all('p')
                for pp in main_ps:
                    if pp.aside != None:
                        main_p = pp
                        break
                if main_p == None:
                    appmon_list[appmon_obj['name']]=appmon_obj
                    changed = True
                    continue
                info_table=main_p.find('aside')
                if info_table != None:
                    if info_table.figure != None:
                        appmon_obj["image"]=info_table.figure.a['href']
                    # print(appmon_obj["image"])
                    rows = info_table.find_all('div',recursive=False)

                    for row in rows:
                        # print(row)
                        if row.h3 == None:
                            continue
                        key = ''.join(x for x in row.h3.get_text(strip=True).title() if not x.isspace())
                        key = key[0].lower()+key[1:]
                        # if key=='debut':
                        #     print(row)
                        appmon_obj[key] = []
                        eles = row.div
                        if key=='grade' or key == 'type' or key == 'appli' or key == 'power':
                            delete_sups(eles)
                            appmon_obj[key]=eles.get_text().strip()
                            continue
                        if key=='debut' or key=='voiceActors' or key=='buddies':
                            # print(eles)
                            appmon_obj[key].extend([BeautifulSoup(x,'html.parser').get_text(strip=True) for x in eles.prettify().split('<br/>')])
                            continue
                        for ele in eles.children:
                            txt=ele.text
                            if txt == None or txt.isspace() or txt in bad_strings or ele.name == 'sup' or ele.name == 'small':
                                continue
                            flag = False
                            if len(txt)>3 and txt.endswith(' + '):
                                appmon_obj[key].extend(txt[:-3].split(", "))
                                txt=' + '
                            if txt!='* (w/ ' and txt.endswith(' (w/ '):
                                appmon_obj[key].extend(txt[:-5].split(", "))
                                txt=' (w/ '
                            if txt.endswith(' * (w/ '):
                                appmon_obj[key].extend(txt[:-7].split(", "))
                                txt=' * (w/ '
                            if txt.startswith('* (w/ ') and txt.endswith(')'):
                                appmon_obj[key].extend(' * (w/ )')
                                appmon_obj[key].extend(txt[6:].split(", "))
                                flag=True
                            if txt.endswith('\n'):
                                txt = txt[:-1]
                            if txt.startswith(') '):
                                txt = txt[2:]
                            if not flag:
                                appmon_obj[key].extend(txt.split(", "))
                        if key == 'priorForms':
                            fusion_objs = []
                            fusees = []
                            i = 0
                            # print(appmon_obj[key])
                            while i < (len(appmon_obj[key])):
                                if i == len(appmon_obj[key])-1 or (appmon_obj[key][i+1] != ' + ' and 'w/' not in appmon_obj[key][i+1]):
                                    fusion_obj = {
                                        'fusion': False, 'name': appmon_obj[key][i], 'fusees': []}
                                    fusees = []
                                    fusion_objs.append(fusion_obj)
                                elif appmon_obj[key][i+1] == ' + ':
                                    while i < len(appmon_obj[key])-1 and appmon_obj[key][i+1] == ' + ':
                                        fusees.append(appmon_obj[key][i])
                                        i += 2
                                    fusees.append(appmon_obj[key][i])
                                    fusion_objs.append(
                                        {'fusion': True, 'name': '', 'fusees': fusees})
                                    fusees = []
                                elif 'w/' in appmon_obj[key][i+1]:
                                    fusees.append(appmon_obj[key][i])
                                    base = appmon_obj[key][i]
                                    i += 2
                                    while  ')' not in appmon_obj[key][i]:
                                        fusees.append(appmon_obj[key][i])
                                        i += 1
                                    fusion_objs.append(
                                        {'fusion': True, 'name': '', 'fusees': fusees})
                                    fusees = []
                                    if i == len(appmon_obj[key])-1 and 'w/' in appmon_obj[key][i+1]:
                                        appmon_obj[key].insert(i+1, base)
                                i += 1
                            appmon_obj[key] = fusion_objs
                        elif key == 'nextForms':
                            fusion_objs = []
                            fusees = []
                            i = 0
                            # print(appmon_obj[key])
                            while i < (len(appmon_obj[key])):
                                if i == len(appmon_obj[key])-1 or 'w/' not in appmon_obj[key][i+1]:
                                    fusion_obj = {
                                        'fusion': False, 'name': appmon_obj[key][i], 'fusees': []}
                                    fusees = []
                                    fusion_objs.append(fusion_obj)

                                elif 'w/' in appmon_obj[key][i+1]:
                                    base = appmon_obj[key][i]
                                    i += 2
                                    while ')' not in appmon_obj[key][i]:
                                        fusees.append(appmon_obj[key][i])
                                        i += 1
                                    fusion_objs.append(
                                        {'fusion': True, 'name': base, 'fusees': fusees})
                                    fusees = []
                                    if i != len(appmon_obj[key])-1 and 'w/' in appmon_obj[key][i+1]:
                                        appmon_obj[key].insert(i+1, base)
                                i += 1
                            appmon_obj[key] = fusion_objs
                    onerows = info_table.find_all('section')
                    for columns in onerows:
                        # print(columns)
                        # print(columns[0].prettify())
                        if columns.find('table') == None:
                            print('gg')
                            continue
                        vert_table = columns.find('table')
                        # print(vert_cols)
                        # print(vert_table)
                        if vert_table.caption == None:
                            continue
                        heading = vert_table.caption.get_text()
                        # print(heading)
                        # Convert key to camelCase
                        heading = ''.join(
                            x for x in heading.title() if not x.isspace())
                        heading = heading[0].lower()+heading[1:]
                        appmon_obj[heading] = []
                        vert_cols = vert_table.find_all('tr')
                        for i in range(0, len(vert_cols)):
                            delete_sups(vert_cols[i])
                            appmon_obj[heading].extend(
                                vert_cols[i].get_text()[3:-1].split('• '))
                        pattern = re.compile('\(.*?:\)')

                        appmon_obj[heading] = [{'language':pattern.match(x).group()[1:-2] ,'name':pattern.sub('',x).strip()}
                                             if pattern.match(x) else
                                             {'language':'NA' ,'name':x}
                                             for x in appmon_obj[heading] ]
                next_p=main_p.find_next_sibling('p')
                attack_list = None
                if next_p == None:
                    delete_sups(main_p)
                    desc=''
                    for sibling in info_table.next_siblings:
                       desc+=sibling.get_text()
                    appmon_obj['description'] = desc.strip()
                elif next_p.get_text(strip=True)=='Attacks':
                   delete_sups(main_p)
                   desc=''
                   for sibling in info_table.next_siblings:
                       desc+=sibling.get_text()
                   appmon_obj['description'] = desc.strip()
                   attack_list = next_p.find_next_sibling('ul')
                else:
                    delete_sups(next_p)
                    appmon_obj['description'] = next_p.get_text(strip=True)
                    if next_p.find_next_sibling('p') and next_p.find_next_sibling('p').get_text(strip=True)=='Attacks':
                        attack_list = next_p.find_next_sibling('ul')
                
                if(attack_list != None):
                    appmon_obj['attacks'] = []
                    attacks = attack_list.find_all('li')
                    for attack in attacks:
                        delete_sups(attack)
                        atk_txt = attack.get_text().strip()
                        to_list = atk_txt.rsplit(':', 1)
                        appmon_obj['attacks'].append(
                            {'name': to_list[0], 'description': to_list[1].strip() if len(to_list) > 1 else ''})

            
            appmon_list[appmon_obj['name']]=appmon_obj
            
            changed = True
except Exception:
    print("Exception in user code:")
    print("-"*60)
    traceback.print_exc(file=sys.stdout)
    print("-"*60)
finally:
    if changed:
        with open('appmon_list.json', 'w') as outfile:
            json.dump(appmon_list, outfile)




# print(appmon_list,len(appmon_list)) #1507 digimon including spoofs
