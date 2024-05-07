import unicodedata
import json
import sys, traceback

digi_list_1 = {}
digi_list_2 = {}
try:
    with open('digi_list_3.json') as infile:
        digi_list_1 = json.load(infile)
except Exception:
    print("Exception in user code:")
    print("-"*60)
    traceback.print_exc(file=sys.stdout)
    print("-"*60)

try:
    with open('wikimon_list.json') as infile:
        digi_list_2 = json.load(infile)
except Exception:
    print("Exception in user code:")
    print("-"*60)
    traceback.print_exc(file=sys.stdout)
    print("-"*60)
# tmp = []
# for key in digi_list_1:
#     if 'name_ja_romanized' in digi_list_1[key] and len(digi_list_1[key]['name_ja_romanized'])>0:
#         tmp.append(digi_list_1[key]['name_ja_romanized'])

# for i in tmp:
#     digi_list_1[i]={}

s1 = {}
s2 = {}

for i in digi_list_1:
    if 'name_ja' in digi_list_1[i]:
        s1[unicodedata.normalize('NFKC',digi_list_1[i]['name_ja'])] = i
for i in digi_list_2:
    s2[unicodedata.normalize('NFKC',digi_list_2[i]['kanji'])] = i

diff = ""
for digi in s2:
    if digi not in s1:
        diff+=s2[digi]+"( "+digi+" )\n"
diff+=('========================\n')
for digi in s1:
    if digi not in s2:
        diff+=s1[digi]+"( "+digi+" )\n"

with open('diff.txt', 'w') as outfile:
    outfile.writelines(diff)