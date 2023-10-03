from petcluster import Multiplex
from py3plex.visualization.multilayer import hairball_plot, interactive_hairball_plot, draw_multilayer_default, draw_multiedges, plt

por = Multiplex()

import json
fileObject = open("material_links.json", "r")
jsonContent = fileObject.read()
por.link_list = json.loads(jsonContent)

fileObject = open("node_data.json", "r")
jsonContent = fileObject.read()

data = json.loads(jsonContent)
por.nodes = data['nodes']
por.performance.nodes = por.nodes
por.network.nodes = por.nodes


por.process_nodes = data['process_nodes']
por.performance.process_nodes = por.process_nodes
por.network.process_nodes=por.process_nodes

por.background_nodes = data['background_nodes']
por.performance.background_nodes = por.background_nodes


por.load_energy_table('mapping_energy.xlsx',sheet_name='Sheet2')
por.load_energy()
por.remove_duplicate_links_energy()


por.load_electricity_table('mapping_electricity.xlsx',sheet_name='Sheet1')
por.load_electricity()
por.remove_duplicate_links_electricity()


por.multiplex.add_edges(por.link_list)
por.multiplex.add_edges(por.energy_link_list)
por.multiplex.add_edges(por.electricity_link_list)

por.multiplex['MRKT','Material']['O1','Material'][2]['carbon_content'] = 0.838695330101104
por.multiplex['MRKT','Material']['O1','Material'][2]['carbon_flow_rate'] = 0.838695330101104 * por.multiplex['MRKT','Material']['O1','Material'][2]['mass_flow_rate']

por.multiplex['MRKT','Material']['CB1','Material'][0]['carbon_content'] = 0.850867018101365
por.multiplex['MRKT','Material']['CB1','Material'][0]['carbon_flow_rate'] = 124.56693145004 

por.multiplex._couple_all_edges()
por.multiplex.visualize_network()

from itertools import combinations
def check_duplicates(link1, link2, duplicate_list):
    '''Check if two links are duplicates by comparing the mass flow rate,
    temperature and pressure'''

    if link1[0] is not link2[0]:
        return duplicate_list
    if link1[1] is not link2[1]:
        return duplicate_list
    
    if link1[0][1] == 'Material':
        if abs(link1[3]['mass_flow_rate']-link2[3]['mass_flow_rate']) /  link1[3]['mass_flow_rate'] > 0.0001:
            return duplicate_list
        if abs(link1[3]['temperature']-link2[3]['temperature'])/link1[3]['temperature'] > 0.0001:
            return duplicate_list
        if abs(link1[3]['pressure']-link2[3]['pressure'])/link1[3]['pressure'] > 0.0001:
            return duplicate_list
        
        duplicate_list.append(link2)
        return duplicate_list
    
        
dup_list = []
test_list = [link for link in por.multiplex.get_edges(data=True)]

for link1, link2 in combinations(test_list,2):
    check_duplicates(link1,link2,dup_list)
    
por.multiplex.remove_edges((dup_list[0][0][0],dup_list[0][0][1], dup_list[0][1][0], dup_list[0][1][1], dup_list[0][2]))



node_list = []
ignore_list = ['MRKT','PROD','WWT','ENVI','SPROD','WATER','AIR','HCT','STCK','SWT','CLW']
remove_list = []

if node_list:
    temp = list(x for x in por.multiplex.get_nodes())
    for y in temp:
        if y[0] not in node_list:
            remove_list.append(y)
        
    temp2 = temp
    for y in remove_list:
        temp2.remove(y)
    
else:
    temp = list(x for x in por.multiplex.get_nodes())
    if ignore_list:
        for y in temp:
            if y[0] in ignore_list:
                remove_list.append(y) 

        temp2 = temp
        for y in remove_list:
            temp2.remove(y)


subnetwork = por.multiplex.subnetwork(input_list=temp2)

network_colors, graph = subnetwork.get_layers(style="hairball")
g, nsizes, final_color_mapping, pos = hairball_plot(graph,draw = False, scale_by_size=True, node_size=1)
interactive_hairball_plot(g,nsizes,final_color_mapping,pos,colorscale="Portland")

hairball_plot(graph, edge_width=0.05,alpha_channel=0.5)