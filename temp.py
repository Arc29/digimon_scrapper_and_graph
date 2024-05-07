import json

digimon_list = {}

try:
    with open('digi_list_3.json') as infile:
        digimon_list = json.load(infile)
except Exception:
    print("Exception in user code:")
for digi in digimon_list:
    digimon_list[digi]['debut']=' '.join(digimon_list[digi]['debut'])
    if digimon_list[digi]['debut'].endswith(']'):
        i=digimon_list[digi]['debut'].rfind('[')
        digimon_list[digi]['debut']=digimon_list[digi]['debut'][0:i].strip()

with open('digi_list_3.json', 'w') as outfile:
    json.dump(digimon_list, outfile)