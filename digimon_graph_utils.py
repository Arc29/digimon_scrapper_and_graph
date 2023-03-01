import json
import os
import sys
import traceback
import webbrowser
from pyvis.network import Network

net = Network(directed=True,  font_color='white', bgcolor='#222222', filter_menu=True)
# dir_path = os.path.dirname(os.path.realpath(__file__))

def check_edge_exists(fro,to):
    edge_exists=False
    for e in net.get_edges():
            frm = e['from']
            dest = e['to']
            if (
                    (fro == frm and to == dest)
            ):
                # edge already exists
                edge_exists = True
    return edge_exists


def create_digimon_graph():

    net.set_template('./digimon.html.j2')
    
    img_path = 'file://'+dir_path+'/digimon_images'

    
    try:
        with open('digi_list_2.json', encoding='utf-8') as infile:
            digimon_list = json.load(infile)
            for k,v in digimon_list.items():
                # if v['image']:
                #     ext = ''
                #     if '.jpg' in v['image']:
                #         ext = '.jpg'
                #     elif '.png' in v['image']:
                #         ext = '.png'
                #     elif '.gif' in v['image']:
                #         ext = '.gif'
                #     net.add_node(k,title=v['description'],shape='circularImage',image=img_path+v['url']+ext)
                    # print(img_path+v['url']+ext)
                if v['image']:
                    net.add_node(k,title=v['description'],shape='circularImage',image=v['image'])
                else:
                    net.add_node(k,title=v['description'])
            #add edges from priorForms
            for k,v in digimon_list.items():
                if v['priorForms']:
                    for pf in v['priorForms']:
                        if pf['fusion']:
                            jogressNode = frozenset(pf['fusees']).__hash__()
                            net.add_node(jogressNode,title='Jogress Node',label='',color='blue')
                            for fusee in pf['fusees']:
                                if not check_edge_exists(fusee,jogressNode):
                                    net.add_edge(fusee,jogressNode)
                            if not check_edge_exists(jogressNode,k):
                                net.add_edge(jogressNode,k)
                        else:
                            if not check_edge_exists(pf['name'],k):
                                net.add_edge(pf['name'],k)
            #add edges from nextForms if not already present
            # edgeList=net.get_edges()
            nodeList=net.get_nodes()
            count=0
            c1=0
            kk=[]
            # print(edgeList)
            for k,v in digimon_list.items():
                fg=False
                if v['nextForms']:
                    for nf in v['nextForms']:
                        if nf['fusion']:
                            temp = nf['fusees']
                            temp.append(k)
                            jogressNode = frozenset(temp).__hash__()
                            if jogressNode not in net.get_nodes():
                                count+=1
                                kk.append(temp)
                                net.add_node(jogressNode,title='Jogress Node',label='',color='blue')
                            for fusee in nf['fusees']:
                                if not check_edge_exists(fusee,jogressNode):
                                    print(fusee,jogressNode,'A')
                                    fg=True
                                    net.add_edge(fusee,jogressNode)
                                    # pass
                            if not check_edge_exists(k,jogressNode):
                                print(k,jogressNode,'B')
                                fg=True
                                net.add_edge(k,jogressNode)
                                # pass
                            if not check_edge_exists(jogressNode,nf['name']):
                                fg=True
                                print(jogressNode,nf['name'],'C')
                                net.add_edge(jogressNode,nf['name'])
                                # pass
                        else:
                            if not check_edge_exists(k,nf['name']):
                                fg=True
                                print(k,nf['name'],'D')
                                net.add_edge(k,nf['name'])
                                # pass
                if fg:
                    c1+=1
            #add edges from slide forms if not already present
            for k,v in digimon_list.items():
                if v['slideForms']:
                    for sf in v['slideForms']:
                        if not check_edge_exists(k,sf):
                            print(k,sf,'E')
                            net.add_edge(k,sf,color='red')

            #add edges for digi-fuse forms if not already present
            net.add_node('X7FFusionNode',title='Digimon World + Fusion Fighters United Army',color='red')
            net.add_edge('Shoutmon','X7FFusionNode',color='green')
            net.add_edge('X7FFusionNode','Shoutmon X7F Superior Mode',color='green')
            for k,v in digimon_list.items():
                if k == "Shoutmon X7F Superior Mode":
                    continue
                if v['digifuseForms']:
                    for df in v['digifuseForms']:
                        if df['inX7F?'] and not check_edge_exists(k,'X7FFusionNode'):
                            net.add_edge(k,'X7FFusionNode',color='yellow')
                            print(k,'X7FFusionNode','F')
                        elif not df['inX7F?']:
                            temp=df['fusees']
                            temp.append(df['base'])
                            digifuseNode = frozenset(temp).__hash__()

                            if digifuseNode not in net.get_nodes():
                                net.add_node(digifuseNode,label='',title='DigiFuse Node',color='#ff1111')
                            if not check_edge_exists(df['base'],digifuseNode):
                                net.add_edge(df['base'],digifuseNode,color='green')
                                print(df['base'],digifuseNode,'G')
                            for fusee in df['fusees']:
                                if not check_edge_exists(fusee,digifuseNode):
                                    net.add_edge(fusee,digifuseNode,color='yellow')
                                    print(fusee,digifuseNode,'H')
                            if not check_edge_exists(digifuseNode,df['result']):
                                net.add_edge(digifuseNode,df['result'],color='green')
                                print(digifuseNode,df['result'],'I')

            #add x-antibody evolutions
            count=0
            for k,v in digimon_list.items():
                if k.endswith(' X') and k[0:-2] in digimon_list:
                    # print(k)
                    count+=1
                    net.add_edge(k,k[0:-2],color='purple',title='Remove X-antibody')
                    net.add_edge(k[0:-2],k,color='black',title='Add X-antibody')
                elif k.endswith(' X') and k[0:-2] not in digimon_list:
                    if k=='Belphemon X':
                        net.add_edge(k,'Belphemon Sleep Mode',color='purple',title='Remove X-antibody')
                        net.add_edge(k,'Belphemon Rage Mode',color='purple',title='Remove X-antibody')
                        net.add_edge('Belphemon Sleep Mode',k,color='black',title='Add X-antibody')
                        net.add_edge('Belphemon Rage Mode',k,color='black',title='Add X-antibody')
                    elif k=='Justimon X':
                        for vars in v['variations']:
                            net.add_edge(vars['name'],k,color='black',title='Add X-antibody')
                    elif k=='MetalGreymon X':
                        net.add_edge(k,'MetalGreymon (Vaccine)',color='purple',title='Remove X-antibody')
                        net.add_edge('MetalGreymon (Vaccine)',k,color='black',title='Add X-antibody')

                    # print(k)
            # print(count)

            # for i in edgeList:
            #     if i['from']=='Starmon (2010 anime)+Pickmon (Red)':
            #         print(i)
            # for n in net.get_edges():
            #     print(n)
            net.write_html('digimon_graph_web.html')
            webbrowser.open_new_tab('digimon_graph_web.html')
            # print(c1)
    except Exception:
        print("Exception in user code:")
        print("-"*60)
        traceback.print_exc(file=sys.stdout)
        print("-"*60)

def create_appmon_graph():

    net.set_template('./digimon.html.j2')
    # img_path = 'file://'+dir_path+'/appmon_images'

    try:
        with open('appmon_list.json', encoding='utf-8') as infile:
            digimon_list = json.load(infile)
            for k,v in digimon_list.items():
                # if v['image']:
                #     ext = ''
                #     if '.jpg' in v['image']:
                #         ext = '.jpg'
                #     elif '.png' in v['image']:
                #         ext = '.png'
                #     elif '.gif' in v['image']:
                #         ext = '.gif'
                #     net.add_node(k,title=v['description'],shape='circularImage',image=img_path+v['url']+ext)
                #     print(img_path+v['url']+ext)
                if v['image']:
                    net.add_node(k,title=v['description'],shape='circularImage',image=v['image'],color='white')
                else:
                    net.add_node(k,title=v['description'],color='white')
            #add edges from priorForms
            for k,v in digimon_list.items():
                if v['priorForms']:
                    for pf in v['priorForms']:
                        if pf['fusion']:
                            jogressNode = frozenset(pf['fusees']).__hash__()
                            net.add_node(jogressNode,title='Applink Node\n'+' + '.join(pf['fusees'])+'\n= '+k,label='',color='blue')
                            for fusee in pf['fusees']:
                                if not check_edge_exists(fusee,jogressNode):
                                    net.add_edge(fusee,jogressNode)
                            if not check_edge_exists(jogressNode,k):
                                net.add_edge(jogressNode,k)
                        else:
                            if not check_edge_exists(pf['name'],k):
                                net.add_edge(pf['name'],k)
            #add edges from nextForms if not already present
            # edgeList=net.get_edges()
            nodeList=net.get_nodes()
            count=0
            c1=0
            kk=[]
            # print(edgeList)
            for k,v in digimon_list.items():
                fg=False
                if v['nextForms']:
                    for nf in v['nextForms']:
                        if nf['fusion']:
                            temp = nf['fusees']
                            temp.append(k)
                            jogressNode = frozenset(temp).__hash__()
                            if jogressNode not in net.get_nodes():
                                count+=1
                                kk.append(temp)
                                net.add_node(jogressNode,title='Applink Node\n'+' + '.join(temp)+'\n= '+nf['name'],label='',color='blue')
                            for fusee in nf['fusees']:
                                if not check_edge_exists(fusee,jogressNode):
                                    print(fusee,jogressNode,'A')
                                    fg=True
                                    net.add_edge(fusee,jogressNode)
                                    # pass
                            if not check_edge_exists(k,jogressNode):
                                print(k,jogressNode,'B')
                                fg=True
                                net.add_edge(k,jogressNode)
                                # pass
                            if not check_edge_exists(jogressNode,nf['name']):
                                fg=True
                                print(jogressNode,nf['name'],'C')
                                net.add_edge(jogressNode,nf['name'])
                                # pass
                        else:
                            if not check_edge_exists(k,nf['name']):
                                fg=True
                                print(k,nf['name'],'D')
                                net.add_edge(k,nf['name'])
                                # pass
                if fg:
                    c1+=1
            net.write_html('appmon_graph.html')
            webbrowser.open_new_tab('appmon_graph.html')
            # print(c1)
    except Exception:
        print("Exception in user code:")
        print("-"*60)
        traceback.print_exc(file=sys.stdout)
        print("-"*60)

# g = Network(filter_menu=True,directed=True)
# g.set_template('C:/Users/ArcRo/Documents/b.html.j2')
# g.add_node(0,shape='circularImage', image='file://C:/Users/ArcRo/Documents/digimon_images/wiki/Agumon_(Burst_Mode).png')
# g.add_node(1,shape='circularImage', image='file://C:/Users/ArcRo/Documents/digimon_images/wiki/L_Spirit_of_Darkness.png')
# g.add_node(2,shape='circularImage', image='file://C:/Users/ArcRo/Documents/digimon_images/wiki/L_Spirit_of_Darkness.png')
# g.add_edge(0, 1)
# g.add_edge(1, 2)
# g.write_html('sp.html')
# webbrowser.open_new_tab('sp.html')

create_appmon_graph()
# create_digimon_graph()



