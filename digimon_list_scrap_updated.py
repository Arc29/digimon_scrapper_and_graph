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

def handleDigifuse(link,fuseList):
    fuse_page=requests.get(digimon_fandom_url+link)
    fuse_soup=BeautifulSoup(fuse_page.content,'html.parser')
    context=fuse_soup.find('div',class_='mw-parser-output')
    fuse_table_rows=context.find('table').find_all('tr')
    alt_results=[]
    for i in range(2,len(fuse_table_rows),2):
        delete_sups(fuse_table_rows[i])
        fuse_obj={'base':'','fusees':[],'result':'','inX7F?':False}
        cols=fuse_table_rows[i]('td')
        if len(cols)==1:
            alt_results.append(cols[0].get_text().strip())
        else:
            if alt_results:
                for alt in alt_results:
                    fuse_obj['base']=cols[0].get_text().strip()
                    fuse_obj['result']=alt
                    fuse_obj['fusees'].extend(cols[1].get_text().strip().split(', '))
                    fuseList.append(fuse_obj)
                    fuse_obj={'base':'','fusees':[],'result':'','inX7F?':False}
                alt_results=[]
            fuse_obj['base']=cols[0].get_text().strip()
            fuse_obj['result']=cols[2].get_text().strip()
            fuse_obj['fusees'].extend(cols[1].get_text().strip().split(', '))
        
            fuseList.append(fuse_obj)

page = requests.get(digimon_fandom_url+"/wiki/List_of_Digimon")

soup = BeautifulSoup(page.content, 'html.parser')

results = soup.find(id='mw-content-text')

# with open("demo.html", "w", encoding="utf-8") as f:
#     f.write(results.prettify())

# print(results.prettify())

digimon_tables = results.find_all('table', class_='sortable')

digimon_list = {}

try:
    with open('digi_list.json') as infile:
        digimon_list = json.load(infile)
except Exception:
    print("Exception in user code:")
    print("-"*60)
    traceback.print_exc(file=sys.stdout)
    print("-"*60)

changed = False

digimon_row_list = []
try:
    for table in digimon_tables:
        digimon_row_list.extend(table.find_all('tr'))

    stop = len(digimon_row_list)  # Test limiter
    bad_strings = [", ","(",") ",")\n","\n","Ja:","En:"," and ","/","","and "," and",", and ",", ",",","\"",]
    counter=1
    for digimon_data in itertools.islice(digimon_row_list, 0, stop):
        tag = digimon_data.find('b')
        if tag != None:
            if tag.string in digimon_list:
                continue
            digi_obj = {'name': '', 'url': '', 'image': '', 'level': '', 'type': [], 'attribute': [], 'family': [], 'size': [], 'debut': [], 'priorForms': [], 'nextForms': [], 'slideForms': [
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
                    digimon_list[digi_obj['name']]=digi_obj
                    changed = True
                    continue
                info_table=main_p.find('aside')
                if info_table != None:
                    if info_table.figure != None:
                        digi_obj["image"]=info_table.figure.a['href']
                    # print(digi_obj["image"])
                    rows = info_table.find_all('div',recursive=False)

                    for row in rows:
                        # print(row)
                        if row.h3 == None:
                            continue
                        key = ''.join(x for x in row.h3.get_text(strip=True).title() if not x.isspace())
                        key = key[0].lower()+key[1:]
                        # if key=='debut':
                        #     print(row)
                        digi_obj[key] = []
                        eles = row.div
                        if key=='level':
                            delete_sups(eles)
                            digi_obj[key]=eles.get_text().strip()
                            continue
                        if key=='debut' or key=='voiceActors' or key=='partners':
                            # print(eles)
                            digi_obj[key].extend([BeautifulSoup(x,'html.parser').get_text(strip=True) for x in eles.prettify().split('<br/>')])
                            continue
                        for ele in eles.children:
                            txt=ele.text
                            
                            if key=='digifuseForms' and ele.name=='a':
                                if txt!="Shoutmon X7F Superior Mode":
                                    handleDigifuse(ele['href'],digi_obj[key])
                                else:
                                    digi_obj[key].append({'base':'','fusees':[],'result':'Shoutmon X7F Superior Mode','inX7F?':True})
                                continue
                            if key=='priorForms' and digi_obj['name']=='Shoutmon X7F Superior Mode':
                                key='digifuseForms'
                                handleDigifuse(ele['href'],digi_obj[key])
                                continue
                            if txt == None or txt.isspace() or txt in bad_strings or ele.name == 'sup' or ele.name == 'small':
                                continue
                            
                            if len(txt)>3 and txt.endswith(' + '):
                                digi_obj[key].extend(txt[:-3].split(", "))
                                txt=' + '
                            if txt!='* (w/ ' and txt.endswith(' (w/ '):
                                digi_obj[key].extend(txt[:-5].split(", "))
                                txt=' (w/ '
                            if txt.endswith(' * (w/ '):
                                digi_obj[key].extend(txt[:-7].split(", "))
                                txt=' * (w/ '
                            if txt.endswith('\n'):
                                txt = txt[:-1]
                            if txt.startswith(') '):
                                txt = txt[2:]

                            digi_obj[key].extend(txt.split(", "))
                        if key == 'priorForms':
                            fusion_objs = []
                            fusees = []
                            i = 0
                            # print(digi_obj[key])
                            while i < (len(digi_obj[key])):
                                if i == len(digi_obj[key])-1 or (digi_obj[key][i+1] != ' + ' and 'w/' not in digi_obj[key][i+1]):
                                    fusion_obj = {
                                        'fusion': False, 'name': digi_obj[key][i], 'fusees': []}
                                    fusees = []
                                    fusion_objs.append(fusion_obj)
                                elif digi_obj[key][i+1] == ' + ':
                                    while i < len(digi_obj[key])-1 and digi_obj[key][i+1] == ' + ':
                                        fusees.append(digi_obj[key][i])
                                        i += 2
                                    fusees.append(digi_obj[key][i])
                                    fusion_objs.append(
                                        {'fusion': True, 'name': '', 'fusees': fusees})
                                    fusees = []
                                elif 'w/' in digi_obj[key][i+1]:
                                    fusees.append(digi_obj[key][i])
                                    base = digi_obj[key][i]
                                    i += 2
                                    while ')' not in digi_obj[key][i]:
                                        fusees.append(digi_obj[key][i])
                                        i += 1
                                    fusion_objs.append(
                                        {'fusion': True, 'name': '', 'fusees': fusees})
                                    fusees = []
                                    if i != len(digi_obj[key])-1 and 'w/' in digi_obj[key][i+1]:
                                        digi_obj[key].insert(i+1, base)
                                i += 1
                            digi_obj[key] = fusion_objs
                        elif key == 'nextForms':
                            fusion_objs = []
                            fusees = []
                            i = 0
                            while i < (len(digi_obj[key])):
                                if i == len(digi_obj[key])-1 or 'w/' not in digi_obj[key][i+1]:
                                    fusion_obj = {
                                        'fusion': False, 'name': digi_obj[key][i], 'fusees': []}
                                    fusees = []
                                    fusion_objs.append(fusion_obj)

                                elif 'w/' in digi_obj[key][i+1]:
                                    base = digi_obj[key][i]
                                    i += 2
                                    while ')' not in digi_obj[key][i]:
                                        fusees.append(digi_obj[key][i])
                                        i += 1
                                    fusion_objs.append(
                                        {'fusion': True, 'name': base, 'fusees': fusees})
                                    fusees = []
                                    if i != len(digi_obj[key])-1 and 'w/' in digi_obj[key][i+1]:
                                        digi_obj[key].insert(i+1, base)
                                i += 1
                            digi_obj[key] = fusion_objs
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
                        digi_obj[heading] = []
                        vert_cols = vert_table.find_all('tr')
                        for i in range(0, len(vert_cols)):
                            delete_sups(vert_cols[i])
                            digi_obj[heading].extend(
                                vert_cols[i].get_text()[3:-1].split('• '))
                        pattern = re.compile('\(.*?:\)')

                        digi_obj[heading] = [{'language':pattern.match(x).group()[1:-2] ,'name':pattern.sub('',x).strip()}
                                             if pattern.match(x) else
                                             {'language':'NA' ,'name':x}
                                             for x in digi_obj[heading] ]
                next_p=main_p.find_next_sibling('p')
                attack_list = None
                if next_p == None:
                    delete_sups(main_p)
                    desc=''
                    for sibling in info_table.next_siblings:
                       desc+=sibling.get_text()
                    digi_obj['description'] = desc.strip()
                elif next_p.get_text(strip=True)=='Attacks':
                   delete_sups(main_p)
                   desc=''
                   for sibling in info_table.next_siblings:
                       desc+=sibling.get_text()
                   digi_obj['description'] = desc.strip()
                   attack_list = next_p.find_next_sibling('ul')
                else:
                    delete_sups(next_p)
                    digi_obj['description'] = next_p.get_text(strip=True)
                    if next_p.find_next_sibling('p') and next_p.find_next_sibling('p').get_text(strip=True)=='Attacks':
                        attack_list = next_p.find_next_sibling('ul')
                
                if(attack_list != None):
                    digi_obj['attacks'] = []
                    attacks = attack_list.find_all('li')
                    for attack in attacks:
                        delete_sups(attack)
                        atk_txt = attack.get_text().strip()
                        to_list = atk_txt.rsplit(':', 1)
                        digi_obj['attacks'].append(
                            {'name': to_list[0], 'description': to_list[1].strip() if len(to_list) > 1 else ''})

            
            digimon_list[digi_obj['name']]=digi_obj
            
            changed = True
except Exception:
    print("Exception in user code:")
    print("-"*60)
    traceback.print_exc(file=sys.stdout)
    print("-"*60)
finally:
    if changed:
        with open('digi_list.json', 'w') as outfile:
            json.dump(digimon_list, outfile)




# print(digimon_list,len(digimon_list)) #1507 digimon including spoofs
