import plotly.graph_objects as go
import numpy as np

from collections import Counter

class Performance(object):


    def __init__(self, multiplex, nodes, process_nodes):

        self.multiplex = multiplex
        self.nodes = nodes
        self.process_nodes = process_nodes

    def carbon(self, process_list = "", cutoff = 0.1):

        label = []

        data = {}
        data['source'] = []
        data['target'] = []
        data['value'] = []
        data['color'] = []
        data['label'] = []
        counter = 0

        for link in self.multiplex.get_edges():
            if not process_list:

                stream = self.multiplex[link[0]][link[1]][link[2]]
                carbon_content = stream['carbon_content']*stream['mass_flow_rate']

                if carbon_content >= cutoff:
                    try:
                        name = self.nodes[link[0][0]]['name']
                    except KeyError:
                        name = link[0][0]

                    if name not in label:
                        label.append(name)
                        data['source'].append(counter)
                        counter += 1
                    else:
                        label.index(name)
                        data['source'].append(label.index(name))

                    try:
                        name = self.nodes[link[1][0]]['name']
                    except KeyError:
                        name = link[1][0]

                    if name not in label:
                        label.append(name)
                        data['target'].append(counter)
                        counter += 1
                    else:
                        data['target'].append(label.index(name))

                    data['value'].append(carbon_content)
                    color = list(np.random.choice(range(256), size=3))
                    temp = 'rgba(%d,%d,%d,0.8)' %(color[0],color[1],color[2])
                    data['color'].append(temp)
            else:
                if link[0][0] in process_list or link[1][0] in process_list:

                    stream = self.multiplex[link[0]][link[1]][link[2]]
                    carbon_content = stream['carbon_content']*stream['mass_flow_rate']
                    
                    if carbon_content >= cutoff:

                        try:
                            name = self.nodes[link[0][0]]['name']
                        except KeyError:
                            name = link[0][0]
                        
                        if name not in label:
                            label.append(name)
                            data['source'].append(counter)
                            counter += 1
                        else:
                            label.index(name)
                            data['source'].append(label.index(name))

                        try:
                            name = self.nodes[link[1][0]]['name']
                        except KeyError:
                            name = link[1][0]

                        if name not in label:
                            label.append(name)
                            data['target'].append(counter)
                            counter += 1
                        else:
                            data['target'].append(label.index(name))

                        data['value'].append(carbon_content)
                        color = list(np.random.choice(range(256), size=3))
                        temp = 'rgba(%d,%d,%d,0.8)' %(color[0],color[1],color[2])
                        data['color'].append(temp)
                
        fig = go.Figure(data=[go.Sankey(
            valueformat = ".2f",
            valuesuffix = "ktonne/oper-year",
            node = dict(
            pad = 25,
            thickness = 15,
            line = dict(color = "black", width = 0.5),
            label = label,
            color = "blue"
            ),
            link = data
        )])

        fig.update_layout(title_text="Carbon flows", font_size=20,
        autosize = False,
        width = 1200,
        height = 500)
        fig.show()


    def carbon2(self, process_list="", ignore_list="", cutoff=0.1, fig_width=1500, fig_height=750, fig_pad=150):
        label = []

        data = {}
        data['source'] = []
        data['target'] = []
        data['value'] = []
        data['color'] = []
        data['label'] = []
        counter = 0

        for link in self.multiplex.get_edges():
            if not process_list:

                stream = self.multiplex[link[0]][link[1]][link[2]]
                carbon_content = stream['carbon_content']*stream['mass_flow_rate']

                if carbon_content >= cutoff and link[0][0] not in ignore_list:
                    try: 
                        name_source = self.nodes[link[0][0]]['name']
                    except KeyError:
                        name_source = link[0][0]

                    try:
                        name_target = self.nodes[link[1][0]]['name']
                    except KeyError:
                        name_target = link[1][0]

                    if name_source in label and name_target in label:
                        indices1 = [i for i, x in enumerate(data['source']) if x == label.index(name_source)]
                        indices2 = [i for i, x in enumerate(data['target']) if x == label.index(name_target)]
                        a=set(indices1).intersection(indices2)
                        if len(a) > 0:
                            data['value'][a.pop()] += carbon_content
                        else:
                            if name_source not in label:
                                label.append(name_source)
                                data['source'].append(counter)
                                counter += 1
                            else:
                                label.index(name_source)
                                data['source'].append(label.index(name_source))


                            if name_target not in label:
                                label.append(name_target)
                                data['target'].append(counter)
                                counter += 1
                            else:
                                data['target'].append(label.index(name_target))

                            data['value'].append(carbon_content)

                    else:        
                        if name_source not in label:
                            label.append(name_source)
                            data['source'].append(counter)
                            counter += 1
                        else:
                            label.index(name_source)
                            data['source'].append(label.index(name_source))


                        if name_target not in label:
                            label.append(name_target)
                            data['target'].append(counter)
                            counter += 1
                        else:
                            data['target'].append(label.index(name_target))

                        data['value'].append(carbon_content)
                color = list(np.random.choice(range(256), size=3))
                temp = f"rgba({color[0]},{color[1]},{color[2]},0.8)"
                data['color'].append(temp)
                    
            else:
                if link[0][0] in process_list or link[1][0] in process_list:

                    stream = self.multiplex[link[0]][link[1]][link[2]]
                    carbon_content = stream['carbon_content']*stream['mass_flow_rate']

                    if carbon_content >= cutoff and link[0][0] not in ignore_list:
                        
                        try: 
                            name_source = self.nodes[link[0][0]]['name']
                        except KeyError:
                            name_source = link[0][0]

                        try:
                            name_target = self.nodes[link[1][0]]['name']
                        except KeyError:
                            name_target = link[1][0]

                        if name_source in label and name_target in label:
                            indices1 = [i for i, x in enumerate(data['source']) if x == label.index(name_source)]
                            indices2 = [i for i, x in enumerate(data['target']) if x == label.index(name_target)]
                            a=set(indices1).intersection(indices2)
                            if len(a) > 0:
                                data['value'][a.pop()] += carbon_content

                            else:
                                if name_source not in label:
                                    label.append(name_source)
                                    data['source'].append(counter)
                                    counter += 1
                                else:
                                    label.index(name_source)
                                    data['source'].append(label.index(name_source))

                                if name_target not in label:
                                    label.append(name_target)
                                    data['target'].append(counter)
                                    counter += 1
                                else:
                                    data['target'].append(label.index(name_target))

                                data['value'].append(carbon_content)

                        else:

                            if name_source not in label:
                                label.append(name_source)
                                data['source'].append(counter)
                                counter += 1
                            else:
                                label.index(name_source)
                                data['source'].append(label.index(name_source))


                            if name_target not in label:
                                label.append(name_target)
                                data['target'].append(counter)
                                counter += 1
                            else:
                                data['target'].append(label.index(name_target))

                            data['value'].append(carbon_content)
                    color = list(np.random.choice(range(256), size=3))
                    temp = f"rgba({color[0]},{color[1]},{color[2]},0.8)"
                    data['color'].append(temp)

        fig = go.Figure(data=[go.Sankey(
            valueformat = ".2f",
            valuesuffix = "ktonne/oper-year",
            node = dict(
            pad = fig_pad,
            thickness = 15,
            line = dict(color = "black", width = 0.5),
            label = label,
            color = "blue"
            ),
            link = data
        )])

        fig.update_layout(title_text="Carbon flows", font_size=30,
        autosize = False,
        width = fig_width,
        height = fig_height)
        
        config = {
        'toImageButtonOptions': { 'height': None, 'width': None}
        }
        fig.show(config=config)


    def water(self, process_list ="",ignore_list ="" ,cutoff = 0.1):

        label = []

        data = {}
        data['source'] = []
        data['target'] = []
        data['value'] = []
        data['color'] = []
        data['label'] = []
        counter = 0

        for link in self.multiplex.get_edges():
            if not process_list:

                stream = self.multiplex[link[0]][link[1]][link[2]]
                try:
                    water = stream['mass_fraction']['H2O']*stream['mass_flow_rate']
                except KeyError:
                    water = 0
                
                if water >= cutoff and link[0][0] not in ignore_list:
                    try: 
                        name = self.nodes[link[0][0]]['name']
                    except KeyError:
                        name = link[0][0]
                    
                    if name not in label:
                        label.append(name)
                        data['source'].append(counter)
                        counter += 1
                    else:
                        label.index(name)
                        data['source'].append(label.index(name))

                    try:
                        name = self.nodes[link[1][0]]['name']
                    except KeyError:
                        name = link[1][0]

                    if name not in label:
                        label.append(name)
                        data['target'].append(counter)
                        counter += 1
                    else:
                        data['target'].append(label.index(name))

                    data['value'].append(water)
                    color = list(np.random.choice(range(256), size=3))
                    temp = 'rgba(%d,%d,%d,0.8)' %(color[0],color[1],color[2])
                    data['color'].append(temp)

            else:
                if link[0][0] in process_list or link[1][0] in process_list:

                    stream = self.multiplex[link[0]][link[1]][link[2]]
                    try:
                        water = stream['mass_fraction']['H2O']*stream['mass_flow_rate']
                    except KeyError:
                        water = 0
                    
                    if water >= cutoff and link[0][0] not in ignore_list:

                        try:
                            name = self.nodes[link[0][0]]['name']
                        except KeyError:
                            name = link[0][0]
                        
                        if name not in label:
                            label.append(name)
                            data['source'].append(counter)
                            counter += 1
                        else:
                            label.index(name)
                            data['source'].append(label.index(name))

                        try:
                            name = self.nodes[link[1][0]]['name']
                        except KeyError:
                            name = link[1][0]

                        if name not in label:
                            label.append(name)
                            data['target'].append(counter)
                            counter += 1
                        else:
                            data['target'].append(label.index(name))

                        data['value'].append(water)
                        color = list(np.random.choice(range(256), size=3))
                        temp = 'rgba(%d,%d,%d,0.8)' %(color[0],color[1],color[2])
                        data['color'].append(temp)
                
        fig = go.Figure(data=[go.Sankey(
            valueformat = ".2f",
            valuesuffix = "ktonne/oper-year",
            node = dict(
            pad = 25,
            thickness = 15,
            line = dict(color = "black", width = 0.5),
            label = label,
            color = "blue"
            ),
            link = data
        )])

        fig.update_layout(title_text="Water flows", font_size=20,
        autosize = False,
        width = 1200,
        height = 500)
        fig.show()


    def water2(self, process_list ="",ignore_list ="" ,cutoff = 0.1, fig_width=1500, fig_height=750, fig_pad=150):

        label = []

        data = {}
        data['source'] = []
        data['target'] = []
        data['value'] = []
        data['color'] = []
        data['label'] = []
        counter = 0

        for link in self.multiplex.get_edges():
            if not process_list:

                stream = self.multiplex[link[0]][link[1]][link[2]]
                try:
                    water = stream['mass_fraction']['H2O']*stream['mass_flow_rate']
                except KeyError:
                    water = 0

                if water >= cutoff and link[0][0] not in ignore_list:
                    try: 
                        name_source = self.nodes[link[0][0]]['name']
                    except KeyError:
                        name_source = link[0][0]
                    
                    try:
                        name_target = self.nodes[link[1][0]]['name']
                    except KeyError:
                        name_target = link[1][0]
                        
                    
                    if name_source in label and name_target in label:
                        indices1 = [i for i, x in enumerate(data['source']) if x == label.index(name_source)]
                        indices2 = [i for i, x in enumerate(data['target']) if x == label.index(name_target)]
                        a=set(indices1).intersection(indices2)
                        if len(a) > 0:
                            data['value'][a.pop()] += water
                        else:
                            if name_source not in label:
                                label.append(name_source)
                                data['source'].append(counter)
                                counter += 1
                            else:
                                label.index(name_source)
                                data['source'].append(label.index(name_source))

                            if name_target not in label:
                                label.append(name_target)
                                data['target'].append(counter)
                                counter += 1
                            else:
                                data['target'].append(label.index(name_target))

                            data['value'].append(water)
                        
                    else:
                        
                        if name_source not in label:
                            label.append(name_source)
                            data['source'].append(counter)
                            counter += 1
                        else:
                            label.index(name_source)
                            data['source'].append(label.index(name_source))

                        if name_target not in label:
                            label.append(name_target)
                            data['target'].append(counter)
                            counter += 1
                        else:
                            data['target'].append(label.index(name_target))
                            
                        data['value'].append(water)
                        
                    color = list(np.random.choice(range(256), size=3))
                    temp = f"rgba({color[0]},{color[1]},{color[2]},0.8)"
                    data['color'].append(temp)

            else:
                if link[0][0] in process_list or link[1][0] in process_list:

                    stream = self.multiplex[link[0]][link[1]][link[2]]
                    try:
                        water = stream['mass_fraction']['H2O']*stream['mass_flow_rate']
                    except KeyError:
                        water = 0

                    if water >= cutoff and link[0][0] not in ignore_list:

                        try: 
                            name_source = self.nodes[link[0][0]]['name']
                        except KeyError:
                            name_source = link[0][0]

                        try:
                            name_target = self.nodes[link[1][0]]['name']
                        except KeyError:
                            name_target = link[1][0]
                        
                        if name_source in label and name_target in label:
                            indices1 = [i for i, x in enumerate(data['source']) if x == label.index(name_source)]
                            indices2 = [i for i, x in enumerate(data['target']) if x == label.index(name_target)]
                            a=set(indices1).intersection(indices2)
                            if len(a) > 0:
                                data['value'][a.pop()] += water
                            else:
                                if name_source not in label:
                                    label.append(name_source)
                                    data['source'].append(counter)
                                    counter += 1
                                else:
                                    label.index(name_source)
                                    data['source'].append(label.index(name_source))

                                if name_target not in label:
                                    label.append(name_target)
                                    data['target'].append(counter)
                                    counter += 1
                                else:
                                    data['target'].append(label.index(name_target))

                                    data['value'].append(water)
                        
                        else:
                            if name_source not in label:
                                label.append(name_source)
                                data['source'].append(counter)
                                counter += 1
                            else:
                                label.index(name_source)
                                data['source'].append(label.index(name_source))

                            if name_target not in label:
                                label.append(name_target)
                                data['target'].append(counter)
                                counter += 1
                            else:
                                data['target'].append(label.index(name_target))

                            data['value'].append(water)
                        color = list(np.random.choice(range(256), size=3))
                        
                        temp = f"rgba({color[0]},{color[1]},{color[2]},0.8)"
                        data['color'].append(temp)

        fig = go.Figure(data=[go.Sankey(
            valueformat = ".2f",
            valuesuffix = "ktonne/oper-year",
            node = dict(
            pad = fig_pad,
            thickness = 15,
            line = dict(color = "black", width = 0.5),
            label = label,
            color = "blue"
            ),
            link = data
        )])

        fig.update_layout(title_text="Water flows", font_size=25,
        autosize = False,
        width = fig_width,
        height = fig_height)
        fig.show()


    def process_energy(self, process, ignore_list=''):

        label_dict = {
        'LLPS': 'Very low pressure steam',
        'LPS' : 'Low pressure steam',
        'MPS' : 'Medium pressure steam',
        'HPS' : 'High pressure steam',
        'HHPS': 'Very high pressure steam',
        'Electricity': 'Electricity',
        'NG': 'Natural gas',
        'R134A': 'R134A',
        'R717': 'R717',
        'Cooling water': 'Cooling water'
        }

        color_dict = {
            'LLPS': 'bluegreen',
            'LPS':  'blue',
            'MPS':  'blueviolet',
            'HPS':  'red',
            'HHPS': 'darkred',
            'Electricity': 'orange',
            'NG':   'yellowgreen',
            'R134A': 'pink',
            'R717': 'black',
            'Cooling water': 'lightblue'
        }

        energy = self.nodes[process]['energy_consumption']
        values=[round(x,0) for name,x in energy.items() if name not in ignore_list and x != 0]
        utilities=[name for name,x in energy.items() if name not in ignore_list and  x != 0]

        labels = [label_dict[name] for name in utilities]
        colors = [color_dict[name] for name in utilities]
        process_name = self.nodes[process]['name']

        fig = go.Figure(data=[go.Pie(labels=labels,
                             values=values)])
        fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=30,
                        marker=dict(colors=colors, line=dict(color='#000000', width=2)))
        fig.update_layout(title_text = f'{process}. {process_name}<br>energy consumption in TJ/year',
                        autosize=False,
                        width=1000,
                        height=1000,
                        font=dict(size=30),
                        legend_font=dict(size=35))

        config = {
        'toImageButtonOptions': { 'height': None, 'width': None, }
        }
        fig.show(config=config)


    def cluster_energy(self, ignore_list=''):

        label_dict = {
        'LLPS': 'Very low pressure steam',
        'LPS' : 'Low pressure steam',
        'MPS' : 'Medium pressure steam',
        'HPS' : 'High pressure steam',
        'HHPS': 'Very high pressure steam',
        'Electricity': 'Electricity',
        'NG': 'Natural gas',
        'R134A': 'R134A',
        'R717': 'R717',
        'Cooling water': 'Cooling water'
        }

        color_dict = {
            'LLPS': 'bluegreen',
            'LPS':  'blue',
            'MPS':  'blueviolet',
            'HPS':  'red',
            'HHPS': 'darkred',
            'Electricity': 'orange',
            'NG':   'yellowgreen',
            'R134A': 'pink',
            'R717': 'black',
            'Cooling water': 'lightblue'
        }

        energy_total = Counter({})
        for node in self.process_nodes.values():
            energy_total += Counter(node['energy_consumption'])

        values=[round(x,0) for name,x in energy_total.items() if name not in ignore_list and x != 0]
        utilities=[name for name,x in energy_total.items() if name not in ignore_list and  x != 0]

        labels = [label_dict[name] for name in utilities]
        colors = [color_dict[name] for name in utilities]

        fig = go.Figure(data=[go.Pie(labels=labels,
                             values=values)])
        fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=30,
                        marker=dict(colors=colors, line=dict(color='#000000', width=2)))
        fig.update_layout(title_text = f'Cluster<br>energy consumption in TJ/year',
                        autosize=False,
                        width=1000,
                        height=1000,
                        font=dict(size=30),
                        legend_font=dict(size=35))

        config = {
        'toImageButtonOptions': { 'height': None, 'width': None, }
        }
        fig.show(config=config)