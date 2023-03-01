import json
import sys
import traceback
from collections import Counter
import os.path

import requests
from clint.textui import progress

def find_unknown_key_pairs(digi_obj:dict):
    items=digi_obj.items()
    print('Detected',len(items),'entries')
    unknown_set = set()
    for k,v in items:
        for pf in v['priorForms']:
            if pf['fusion']:
                for key in pf['fusees']:
                    if key not in digi_obj:
                        unknown_set.add((k,key))
            else:
                if pf['name'] not in digi_obj:
                    unknown_set.add((k,pf['name']))
        
        for pf in v['nextForms']:
            if pf['fusion']:
                for key in pf['fusees']:
                    if key not in digi_obj:
                        unknown_set.add((k,key))
            if pf['name'] not in digi_obj:
                unknown_set.add((k,pf['name']))

        for pf in v['slideForms']:
            if pf not in digi_obj and '(Multiple)' not in key:
                unknown_set.add((k,pf))
        
        for pf in v['digifuseForms']:
            if not pf['inX7F?']:
                if pf['base'] not in digi_obj and '(Multiple)' not in pf['base']: 
                    unknown_set.add((k,pf['base']))
                if pf['result'] not in digi_obj and '(Multiple)' not in pf['result']:
                    unknown_set.add((k,pf['result']))
                for key in pf['fusees']:
                    if key not in digi_obj and '(Multiple)' not in key:
                        unknown_set.add((k,key))
    print(len(unknown_set))
    for i in unknown_set:
        print(i)

def contains_masters_evo(s:str):
    test_list = ['(Champion)', '(Rookie)', '(Ultimate)', '(Mega)', '(Ultra)']
    freq = Counter(test_list)
    for i in s.split():
        if i in freq.keys():
            # print(s)
            return True
    return False

def delete_masters_evos(digi_obj:dict):
    items=digi_obj.items()
    
    print('Detected',len(items),'entries')
    unknown_set = set()
    for k,v in items:
        dpfl=[]
        dnfl=[]
        dsfl=[]
        ddfl=[]
        for pf in v['priorForms']:
            if pf['fusion']:
                for key in pf['fusees']:
                    if key not in digi_obj:
                        unknown_set.add(key)
                        if contains_masters_evo(key):
                            dpfl.append(pf)
            else:
                if pf['name'] not in digi_obj:
                    unknown_set.add(pf['name'])
                    if contains_masters_evo(pf['name']):
                        dpfl.append(pf)
        
        for pf in v['nextForms']:
            if pf['fusion']:
                for key in pf['fusees']:
                    if key not in digi_obj:
                        unknown_set.add(key)
                        if contains_masters_evo(key):
                            dnfl.append(pf)
            if pf['name'] not in digi_obj:
                unknown_set.add(pf['name'])
                if contains_masters_evo(pf['name']):
                    dnfl.append(pf)

        for pf in v['slideForms']:
            if pf not in digi_obj:
                unknown_set.add(pf)
                if contains_masters_evo(pf):
                    dsfl.append(pf)
        
        for pf in v['digifuseForms']:
            if not pf['inX7F?']:
                if pf['base'] not in digi_obj: 
                    unknown_set.add(pf['base'])
                    if contains_masters_evo(pf['base']):
                        ddfl.append(pf)
                if pf['result'] not in digi_obj:
                    unknown_set.add(pf['result'])
                    if contains_masters_evo(pf['result']):
                        ddfl.append(pf)
                for key in pf['fusees']:
                    if key not in digi_obj:
                        unknown_set.add(key)
                        if contains_masters_evo(key):
                            ddfl.append(pf)
        # if(dpfl):                    
        #     print(k,'P',dpfl)
        # if(dnfl):
        #     print(k,'N',dnfl)
        # if(dsfl):
        #     print(k,'S',dsfl)
        # if(ddfl):
        #     print(k,'D',ddfl)
        for i in dpfl:
            v['priorForms'].remove(i)
        for i in dnfl:
            v['nextForms'].remove(i)
        for i in dsfl:
            v['slideForms'].remove(i)
        for i in ddfl:
            v['digifuseForms'].remove(i)
    print(len(unknown_set))
    # for i in unknown_set:
    #     print(i)
    return digi_obj

def find_unknown_keys(digi_obj:dict):
    items=digi_obj.items()
    print('Detected',len(items),'entries')
    unknown_set = set()
    for k,v in items:
        for pf in v['priorForms']:
            if pf['fusion']:
                for key in pf['fusees']:
                    if key not in digi_obj:
                        unknown_set.add(key)
            else:
                if pf['name'] not in digi_obj:
                    unknown_set.add(pf['name'])
        
        for pf in v['nextForms']:
            if pf['fusion']:
                for key in pf['fusees']:
                    if key not in digi_obj:
                        unknown_set.add(key)
            if pf['name'] not in digi_obj:
                unknown_set.add(pf['name'])

        for pf in v['slideForms']:
            if pf not in digi_obj:
                unknown_set.add(pf)
        
        for pf in v['digifuseForms']:
            if not pf['inX7F?']:
                if pf['base'] not in digi_obj: 
                    unknown_set.add(pf['base'])
                if pf['result'] not in digi_obj:
                    unknown_set.add(pf['result'])
                for key in pf['fusees']:
                    if key not in digi_obj:
                        unknown_set.add(key)
    print(len(unknown_set))
    return unknown_set

def find_unknown_keys_appmon():
    unknown_set = set()
    try:
        with open('appmon_list.json') as file:
            digi_obj=json.load(file)
            items=digi_obj.items()
            print('Detected',len(items),'entries')
            
            for k,v in items:
                for pf in v['priorForms']:
                    if pf['fusion']:
                        for key in pf['fusees']:
                            if key not in digi_obj:
                                unknown_set.add(key)
                    else:
                        if pf['name'] not in digi_obj:
                            unknown_set.add(pf['name'])
                
                for pf in v['nextForms']:
                    if pf['fusion']:
                        for key in pf['fusees']:
                            if key not in digi_obj:
                                unknown_set.add(key)
                    if pf['name'] not in digi_obj:
                        unknown_set.add(pf['name'])
    except:
        pass

    print(len(unknown_set))
    return unknown_set

def update_unknown_keys():
    try:
        with open('digi_list_3.json','r') as file:
            dobj = json.load(file)
            new_keys=sorted(find_unknown_keys(dobj))
            for key in new_keys:
                digi_obj = {'name': '', 'url': '', 'image': '', 'level': '', 'type': [], 'attribute': [], 'family': [], 'size': [], 'debut': [], 'priorForms': [], 'nextForms': [], 'slideForms': [
                ], 'digifuseForms': [], 'partners': [], 'voiceActors': [], 'cards': [], 'otherNames': [], 'variations': [], 'groups': [], 'description': 'No description found', 'attacks': []}

                digi_obj['name'] = key
                if 'Digi-Egg' in key:
                    digi_obj['level'] = 'Digi-Egg'
                elif 'Spirit' in key:
                    digi_obj['level'] = 'Digi-Spirit'
                else:
                    digi_obj['level'] = 'Human/Object'

                dobj[key]=digi_obj
            with open('digi_list_4.json','w') as ofile:
                json.dump(dobj,ofile)
            
    except:
        print("Exception in user code:")
        print("-"*60)
        traceback.print_exc(file=sys.stdout)
        print("-"*60)




def find_digi_egg_evos(dobj:dict):
    mp = {}
    for k,v in dobj.items():
        for pf in v['priorForms']:
            if pf['fusion']:
                for key in pf['fusees']:
                    if "Digi-Egg" in key:
                        fusee = [x for x in pf['fusees'] if x != key][0]
                        # print(key,'+',fusee,'=',k)
                        if fusee not in mp:
                            mp[fusee]=[]
                        mp[fusee].append((k,key))
    # for k in mp.keys():
    #     print(k,mp[k])

    return mp

def update_digi_egg_evos():
    try:
        with open('digi_list.json') as infile:
            dobj = json.load(infile)
            # find_unknown_keys(digimon_list)
            mp=find_digi_egg_evos(dobj)
            for k in mp.keys():
                for combs in mp[k]:
                    dobj[k]['nextForms'].append({
                    "fusion": True,
                    "name": combs[0],
                    "fusees": [combs[1]]
                    })
                # print(k,dobj[k]['nextForms'])
            
            with open('digi_list_2.json','w') as outfile:
                json.dump(dobj,outfile)
    except Exception:
        print("Exception in user code:")
        print("-"*60)
        traceback.print_exc(file=sys.stdout)
        print("-"*60)

def get_images():
    img_path  = './digimon_images'
    skipped_digis=[]
    try:
        with open('digi_list_2.json', encoding='utf-8') as infile:
            digimon_list = json.load(infile)
            for k,v in digimon_list.items():
                print(k)
                if v['image'] == '':
                    skipped_digis.append(k)
                    continue
                
                path = img_path+v['url']
                if '.jpg' in v['image']:
                    path += '.jpg'
                elif '.png' in v['image']:
                    path += '.png'
                elif '.gif' in v['image']:
                    path += '.gif'
                else:
                    print("Unidentified image format for ",k,"Skipping...")
                    skipped_digis.append(k)
                    continue
                if os.path.isfile(path):
                    continue
                r = requests.get(v['image'], stream=True)
                with open(path, 'wb') as f:
                    total_length = int(r.headers.get('content-length'))
                    print(path)
                    for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1): 
                        if chunk:
                            f.write(chunk)
                            f.flush()
        print(skipped_digis)
                    
    except Exception:
        print("Exception in user code:")
        print("-"*60)
        traceback.print_exc(file=sys.stdout)
        print("-"*60)

def get_images_appmon():
    img_path  = './appmon_images'
    skipped_digis=[]
    try:
        with open('appmon_list.json', encoding='utf-8') as infile:
            digimon_list = json.load(infile)
            for k,v in digimon_list.items():
                print(k)
                if v['image'] == '':
                    skipped_digis.append(k)
                    continue
                
                path = img_path+v['url']
                if '.jpg' in v['image']:
                    path += '.jpg'
                elif '.png' in v['image']:
                    path += '.png'
                elif '.gif' in v['image']:
                    path += '.gif'
                else:
                    print("Unidentified image format for ",k,"Skipping...")
                    skipped_digis.append(k)
                    continue
                if os.path.isfile(path):
                    continue
                r = requests.get(v['image'], stream=True)
                with open(path, 'wb') as f:
                    total_length = int(r.headers.get('content-length'))
                    print(path)
                    for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1): 
                        if chunk:
                            f.write(chunk)
                            f.flush()
        print(skipped_digis)
                    
    except Exception:
        print("Exception in user code:")
        print("-"*60)
        traceback.print_exc(file=sys.stdout)
        print("-"*60)


def update_digi_urls():
    try:
        with open('digi_list_4.json',encoding='utf-8') as infile:
            dobj = json.load(infile)
            for k,v in dobj.items():
                if v['url'] == '':
                    v['url'] = '/wiki/'+(''.join(c if c.isalnum() 
                                       else "%{:02x}".format(ord(c)) for c in k))
            
            with open('digi_list_2.json','w') as outfile:
                json.dump(dobj,outfile)
    except Exception:
        print("Exception in user code:")
        print("-"*60)
        traceback.print_exc(file=sys.stdout)
        print("-"*60)


# update_digi_egg_evos()

# update_unknown_keys()

# get_images()

# update_digi_urls()

# print(find_unknown_keys_appmon())

get_images_appmon()

