'''Contains the performance calculation and visualization'''
from collections import Counter
import plotly.graph_objects as go
import numpy as np

class Performance(object):
    """Main performance object for calculating cluster performance and sankey diagrams"""

    def __init__(self, multiplex, nodes, process_nodes, component_dict):

        self.multiplex = multiplex
        self.nodes = nodes
        self.process_nodes = process_nodes
        self.component_dict = component_dict


    def carbon_sankey(self, process_list="", ignore_list="", cutoff=0.1, fig_width=1500,\
                    fig_height=750, fig_pad=150, fig_thickness = 10, text_font = 30, \
                    title=True, process_abrev = False):
        '''Depicts all the carbon flows in the cluster in a sankey diagram'''
        label = []

        data = {}
        data['source'] = []
        data['target'] = []
        data['value'] = []
        data['color'] = []
        data['label'] = []
        counter = 0

        if process_abrev is True:
            process_name = 'name_abbrev'
        else:
            process_name = 'name'


        for link in self.multiplex.get_edges():
            if not process_list:
                if link[0][1] == 'Material' and link[1][1] == 'Material':
                    stream = self.multiplex[link[0]][link[1]][link[2]]
                    carbon_content = stream['carbon_content']*stream['mass_flow_rate']

                    if carbon_content >= cutoff and link[0][0] not in ignore_list:
                        try:
                            name_source = self.nodes[link[0][0]][process_name]
                        except KeyError:
                            try:
                                name_source = self.nodes[link[0][0]]['name']
                            except KeyError:
                                name_source = link[0][0]

                        try:
                            name_target = self.nodes[link[1][0]][process_name]
                        except KeyError:
                            try:
                                name_target = self.nodes[link[1][0]]['name']
                            except KeyError:
                                name_target = link[1][0]

                        if name_target == 'Stack':
                            name_target = 'Environment'

                        if name_source in label and name_target in label:
                            indices1 = [i for i, x in enumerate(data['source']) \
                                        if x == label.index(name_source)]
                            indices2 = [i for i, x in enumerate(data['target']) \
                                        if x == label.index(name_target)]
                            intersect=set(indices1).intersection(indices2)
                            if len(intersect) > 0:
                                data['value'][intersect.pop()] += carbon_content
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
                    temp = f"rgba({color[0]},{color[1]},{color[2]},0.5)"
                    data['color'].append(temp)

            else:
                if link[0][1] == 'Material' and link[1][1] == 'Material':
                    if link[0][0] in process_list or link[1][0] in process_list:

                        stream = self.multiplex[link[0]][link[1]][link[2]]
                        carbon_content = stream['carbon_content']*stream['mass_flow_rate']

                        if carbon_content >= cutoff and link[0][0] not in ignore_list:

                            try:
                                name_source = self.nodes[link[0][0]][process_name]
                            except KeyError:
                                try:
                                    name_source = self.nodes[link[0][0]]['name']
                                except KeyError:
                                    name_source = link[0][0]

                            try:
                                name_target = self.nodes[link[1][0]][process_name]
                            except KeyError:
                                try:
                                    name_target = self.nodes[link[1][0]]['name']
                                except KeyError:
                                    name_target = link[1][0]

                            if name_target == 'Stack':
                                name_target = 'Environment'

                            if name_source in label and name_target in label:
                                indices1 = [i for i, x in enumerate(data['source']) \
                                            if x == label.index(name_source)]
                                indices2 = [i for i, x in enumerate(data['target']) \
                                            if x == label.index(name_target)]
                                intersect=set(indices1).intersection(indices2)
                                if len(intersect) > 0:
                                    data['value'][intersect.pop()] += carbon_content

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
                        temp = f"rgba({color[0]},{color[1]},{color[2]},0.5)"
                        data['color'].append(temp)

        fig = go.Figure(data=[go.Sankey(
            valueformat = ".2f",
            valuesuffix = "ktonne/oper-year",
            node = dict(
            pad = fig_pad,
            thickness = fig_thickness,
            line = dict(color = "black", width = 1.5),
            label = label,
            color = "blue"
            ),
            link = data
        )])

        if title is True:
            fig.update_layout(title_text="Carbon flows", font_size=text_font,
            autosize = False,
            width = fig_width,
            height = fig_height)
        else:
            fig.update_layout(font_size=text_font,
            autosize = False,
            width = fig_width,
            height = fig_height)

        config = {
        'toImageButtonOptions': { 'height': None, 'width': None}
        }
        fig.show(config=config)


    def material_sankey(self, process_list="", ignore_list="", cutoff=0.1, fig_width=1500,\
                        fig_height=750, fig_pad=150, fig_thickness = 10, text_font = 30):
        '''Depicts all the carbon flows in the cluster in a sankey diagram'''
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
                if link[0][1] == 'Material' and link[1][1] == 'Material':
                    stream = self.multiplex[link[0]][link[1]][link[2]]
                    material_flow = stream['mass_flow_rate']

                    if material_flow >= cutoff and link[0][0] not in ignore_list:
                        try:
                            name_source = self.nodes[link[0][0]]['name']
                        except KeyError:
                            name_source = link[0][0]

                        try:
                            name_target = self.nodes[link[1][0]]['name']
                        except KeyError:
                            name_target = link[1][0]

                        if name_target == 'Stack':
                            name_target = 'Environment'

                        if name_source in label and name_target in label:
                            indices1 = [i for i, x in enumerate(data['source']) \
                                        if x == label.index(name_source)]
                            indices2 = [i for i, x in enumerate(data['target']) \
                                        if x == label.index(name_target)]
                            intersect=set(indices1).intersection(indices2)
                            if len(intersect) > 0:
                                data['value'][intersect.pop()] += material_flow
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

                                data['value'].append(material_flow)

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

                            data['value'].append(material_flow)
                    color = list(np.random.choice(range(256), size=3))
                    temp = f"rgba({color[0]},{color[1]},{color[2]},0.8)"
                    data['color'].append(temp)

            else:
                if link[0][1] == 'Material' and link[1][1] == 'Material':
                    if link[0][0] in process_list or link[1][0] in process_list:

                        stream = self.multiplex[link[0]][link[1]][link[2]]
                        material_flow = stream['mass_flow_rate']

                        if material_flow >= cutoff and link[0][0] not in ignore_list:

                            try:
                                name_source = self.nodes[link[0][0]]['name']
                            except KeyError:
                                name_source = link[0][0]

                            try:
                                name_target = self.nodes[link[1][0]]['name']
                            except KeyError:
                                name_target = link[1][0]

                            if name_target == 'Stack':
                                name_target = 'Environment'

                            if name_source in label and name_target in label:
                                indices1 = [i for i, x in enumerate(data['source']) \
                                            if x == label.index(name_source)]
                                indices2 = [i for i, x in enumerate(data['target']) \
                                            if x == label.index(name_target)]
                                intersect=set(indices1).intersection(indices2)
                                if len(intersect) > 0:
                                    data['value'][intersect.pop()] += material_flow

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

                                    data['value'].append(material_flow)

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

                                data['value'].append(material_flow)
                        color = list(np.random.choice(range(256), size=3))
                        temp = f"rgba({color[0]},{color[1]},{color[2]},0.8)"
                        data['color'].append(temp)

        fig = go.Figure(data=[go.Sankey(
            valueformat = ".2f",
            valuesuffix = "ktonne/oper-year",
            node = dict(
            pad = fig_pad,
            thickness = fig_thickness,
            line = dict(color = "black", width = 0.5),
            label = label,
            color = "blue"
            ),
            link = data
        )])

        fig.update_layout(title_text="Material flows", font_size=text_font,
        autosize = False,
        width = fig_width,
        height = fig_height)

        config = {
        'toImageButtonOptions': { 'height': None, 'width': None}
        }
        fig.show(config=config)



    def water_sankey(self, process_list ="",ignore_list ="" ,cutoff = 0.1, fig_width=1500, \
                    fig_height=750, fig_pad=150, fig_thickness = 15, text_font=30):
        '''Depicts all the water flows in the cluster in a sankey diagram'''
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
                if link[0][1] == 'Material' and link[1][1] == 'Material':

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

                        if name_target == 'Stack':
                            name_target = 'Environment'

                        if name_source in label and name_target in label:
                            indices1 = [i for i, x in enumerate(data['source']) \
                                        if x == label.index(name_source)]
                            indices2 = [i for i, x in enumerate(data['target']) \
                                        if x == label.index(name_target)]
                            intersect=set(indices1).intersection(indices2)
                            if len(intersect) > 0:
                                data['value'][intersect.pop()] += water
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
                if link[0][1] == 'Material' and link[1][1] == 'Material':
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

                            if name_target == 'Stack':
                                name_target = 'Environment'

                            if name_source in label and name_target in label:
                                indices1 = [i for i, x in enumerate(data['source']) \
                                            if x == label.index(name_source)]
                                indices2 = [i for i, x in enumerate(data['target']) \
                                            if x == label.index(name_target)]
                                intersect=set(indices1).intersection(indices2)
                                if len(intersect) > 0:
                                    data['value'][intersect.pop()] += water
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
            thickness = fig_thickness,
            line = dict(color = "black", width = 0.5),
            label = label,
            color = "blue"
            ),
            link = data
        )])

        fig.update_layout(title_text="Water flows", font_size=text_font,
        autosize = False,
        width = fig_width,
        height = fig_height)
        fig.show()


    def steam_sankey(self, process_list="", ignore_list="", cutoff=0.1, fig_width=1500, \
                    fig_height=750, fig_pad=150, fig_thickness = 10, text_font = 30):
        '''Depicts all the carbon flows in the cluster in a sankey diagram'''
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
                if link[0][1] == 'Steam' and link[1][1] == 'Steam':
                    stream = self.multiplex[link[0]][link[1]][link[2]]
                    steam_amount = stream['energy']

                    if steam_amount >= cutoff and link[0][0] not in ignore_list:
                        try:
                            name_source = self.nodes[link[0][0]]['name']
                        except KeyError:
                            name_source = link[0][0]

                        try:
                            name_target = self.nodes[link[1][0]]['name']
                        except KeyError:
                            name_target = link[1][0]

                        if name_target == 'Stack':
                            name_target = 'Environment'

                        if name_source in label and name_target in label:
                            indices1 = [i for i, x in enumerate(data['source']) \
                                        if x == label.index(name_source)]
                            indices2 = [i for i, x in enumerate(data['target']) \
                                        if x == label.index(name_target)]
                            intersect=set(indices1).intersection(indices2)
                            if len(intersect) > 0:
                                data['value'][intersect.pop()] += steam_amount
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

                                data['value'].append(steam_amount)

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

                            data['value'].append(steam_amount)
                    color = list(np.random.choice(range(256), size=3))
                    temp = f"rgba({color[0]},{color[1]},{color[2]},0.8)"
                    data['color'].append(temp)

            else:
                if link[0][1] == 'Steam' and link[1][1] == 'Steam':
                    if link[0][0] in process_list or link[1][0] in process_list:

                        stream = self.multiplex[link[0]][link[1]][link[2]]
                        steam_amount = stream['energy']

                        if steam_amount >= cutoff and link[0][0] not in ignore_list:

                            try:
                                name_source = self.nodes[link[0][0]]['name']
                            except KeyError:
                                name_source = link[0][0]

                            try:
                                name_target = self.nodes[link[1][0]]['name']
                            except KeyError:
                                name_target = link[1][0]

                            if name_target == 'Stack':
                                name_target = 'Environment'

                            if name_source in label and name_target in label:
                                indices1 = [i for i, x in enumerate(data['source']) \
                                            if x == label.index(name_source)]
                                indices2 = [i for i, x in enumerate(data['target']) \
                                            if x == label.index(name_target)]
                                intersect=set(indices1).intersection(indices2)
                                if len(intersect) > 0:
                                    data['value'][intersect.pop()] += steam_amount

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

                                    data['value'].append(steam_amount)

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

                                data['value'].append(steam_amount)
                        color = list(np.random.choice(range(256), size=3))
                        temp = f"rgba({color[0]},{color[1]},{color[2]},0.8)"
                        data['color'].append(temp)

        fig = go.Figure(data=[go.Sankey(
            valueformat = ".2f",
            valuesuffix = "TJ/oper-year",
            node = dict(
            pad = fig_pad,
            thickness = fig_thickness,
            line = dict(color = "black", width = 0.5),
            label = label,
            color = "blue"
            ),
            link = data
        )])

        fig.update_layout(title_text="Steam energy flows", font_size=text_font,
        autosize = False,
        width = fig_width,
        height = fig_height)

        config = {
        'toImageButtonOptions': { 'height': None, 'width': None}
        }
        fig.show(config=config)


    def carbon_process(self, process):
        '''
        Calculate the total amount of carbon entering the process,
        the total amount of carbon in the waste streams and
        the total amount of carbon in the product stream.
        [ktonne / operating-year]
        '''
        carbon_in = 0
        carbon_waste = 0
        carbon_prod = 0

        for link in self.multiplex.get_edges():
            if link[0][0] == process:
                if link[1][0] == 'PROD' or link[1][0] in self.process_nodes.keys():
                    try:
                        stream = self.multiplex[link[0]][link[1]][link[2]]
                        carbon = stream['mass_flow_rate'] * stream['carbon_content']
                        carbon_prod += carbon
                    except KeyError:
                        pass
                else:
                    try:
                        stream = self.multiplex[link[0]][link[1]][link[2]]
                        carbon = stream['mass_flow_rate'] * stream['carbon_content']
                        carbon_waste += carbon
                    except KeyError:
                        pass
            if link[1][0] == process:
                try:
                    stream = self.multiplex[link[0]][link[1]][link[2]]
                    carbon = stream['mass_flow_rate'] * stream['carbon_content']
                    carbon_in += carbon
                except KeyError:
                    pass

        return carbon_in, carbon_waste, carbon_prod


    def carbon_cluster(self):
        '''
        Calculate the total amount of carbon entering the cluster,
        the total amount of carbon in the cluster waste streams and
        the total amount of carbon in the cluster product streams
        [ktonne / operating-year]
        '''
        carbon_in = 0
        carbon_waste = 0
        carbon_prod = 0

        tags,layers,_link_dict=  self.multiplex.get_layers()
        layer_in = tags.index('IN')
        layer_out = tags.index('OUT')

        for link in layers[layer_in].edges:
            data = self.multiplex[link[0]][link[1]][link[2]]
            carbon_in += data['carbon_content'] * data['mass_flow_rate']

        for link in layers[layer_out].edges:
            if link[1][0] == 'PROD':
                data = self.multiplex[link[0]][link[1]][link[2]]
                carbon_prod += data['carbon_content'] * data['mass_flow_rate']
            else:
                data = self.multiplex[link[0]][link[1]][link[2]]
                carbon_waste += data['carbon_content'] * data['mass_flow_rate']

        return carbon_in, carbon_waste, carbon_prod, carbon_prod/carbon_in


    def water_process(self, process):
        '''
        Returns the total amount of water entering the process,
        total water to the chlorinated waste treatment,
        total water to waste water treatment,
        total water in the product streams,
        total water in the air,
        total water in the source.
        [ktonne / operating-year]
        '''

        water_in = 0
        water_lq_chlor = 0
        water_wwt = 0
        water_prod = 0
        water_air = 0
        water_source = 0

        for link in self.multiplex.get_edges():
            if link[0][0] == process:
                stream = self.multiplex[link[0]][link[1]][link[2]]
                if link[1][0] == 'PROD' or link[1][0] in self.process_nodes.keys():
                    try:
                        water = stream['mass_flow_rate'] * stream['mass_fraction']['H2O']
                        water_prod += water
                    except KeyError:
                        pass
                elif link[1][0] == 'LQCL':
                    try:
                        water = stream['mass_fraction']['H2O'] * stream['mass_flow_rate']
                        water_lq_chlor += water
                    except KeyError:
                        pass
                elif link[1][0] == 'WWT':
                    try:
                        water = stream['mass_fraction']['H2O'] * stream['mass_flow_rate']
                        water_wwt += water
                    except KeyError:
                        pass
                else:
                    if stream['vapor_fraction'] == 1:
                        try:
                            water = stream['mass_fraction']['H2O'] * stream['mass_flow_rate']
                            water_air += water
                        except KeyError:
                            pass
                    else:
                        try:
                            water = stream['mass_fraction']['H2O'] * stream['mass_flow_rate']
                            water_source += water
                        except KeyError:
                            pass
            if link[1][0] == process:
                try:
                    stream = self.multiplex[link[0]][link[1]][link[2]]
                    water = stream['mass_flow_rate'] * stream['mass_fraction']['H2O']
                    water_in += water
                except KeyError:
                    pass

        return water_in, water_lq_chlor, water_wwt, water_prod, water_air, water_source


    def water_cluster(self):
        '''
        Returns the total amount of water entering the cluster,
        total water to the chlorinated waste treatment,
        total water to waste water treatment,
        total water in the product streams,
        total water in the air,
        total water in the source
        [ktonne / operating-year]
        '''
        water_in = 0
        water_lq_chlor = 0
        water_wwt = 0
        water_prod = 0
        water_air = 0
        water_source = 0

        tags,layers,_link_dict=  self.multiplex.get_layers()
        layer_in = tags.index('IN')
        layer_out = tags.index('OUT')

        for link in layers[layer_in].edges:
            stream = self.multiplex[link[0]][link[1]][link[2]]
            try:
                water = stream['mass_fraction']['H2O'] * stream['mass_flow_rate']
                water_in += water
            except KeyError:
                pass

        for link in layers[layer_out].edges:
            stream = self.multiplex[link[0]][link[1]][link[2]]
            if link[1][0] == 'PROD':
                try:
                    water = stream['mass_fraction']['H2O'] * stream['mass_flow_rate']
                    water_prod += water
                except KeyError:
                    pass
            elif link[1][0] == 'LQCL':
                try:
                    water = stream['mass_fraction']['H2O'] * stream['mass_flow_rate']
                    water_lq_chlor += water
                except KeyError:
                    pass
            elif link[1][0] == 'WWT':
                try:
                    water = stream['mass_fraction']['H2O'] * stream['mass_flow_rate']
                    water_wwt += water
                except KeyError:
                    pass
            else:
                if stream['vapor_fraction'] == 1:
                    try:
                        water = stream['mass_fraction']['H2O'] * stream['mass_flow_rate']
                        water_air += water
                    except KeyError:
                        pass
                else:
                    try:
                        water = stream['mass_fraction']['H2O'] * stream['mass_flow_rate']
                        water_source += water
                    except KeyError:
                        pass

        return water_in, water_lq_chlor, water_wwt, water_prod, water_air, water_source


    def co2_process(self, process):
        '''
        Calculates the amount of direct CO2 emissions of a process
        [ktonne / operating-year]
        '''

        co2_out = 0

        for link in self.multiplex.get_edges():
            if link[0][0] == process and link[1][0] == 'ENVI':
                try:
                    stream = self.multiplex[link[0]][link[1]][link[2]]
                    co2 = stream['mass_flow_rate'] * stream['mass_fraction']['CO2']
                    co2_out += co2
                except KeyError:
                    pass

            elif link[0][0] == process and link[1][0] == 'STCK':
                stream = self.multiplex[link[0]][link[1]][link[2]]
                co2 = stream['carbon_content']*stream['mass_flow_rate']/12.011*44.0095
                co2_out += co2

        return co2_out


    def co2_cluster(self):
        '''
        Calculates the amount of direct CO2 emissions of the cluster
        [ktonne / operating-year]
        '''
        co2_out = 0

        tags,layers,_link_dict=  self.multiplex.get_layers()
        layer_out = tags.index('OUT')

        for link in layers[layer_out].edges:
            data = self.multiplex[link[0]][link[1]][link[2]]

            if link[1][0] == 'ENVI:':
                try:
                    co2 = data['mass_fraction']['CO2'] * data['mass_flow_rate']
                    co2_out += co2
                except KeyError:
                    co2_out += 0
            elif link[1][0] == 'STCK':
                co2 = data['carbon_content']*data['mass_flow_rate']/12.011*44.0095
                co2_out += co2

        return co2_out


    def energy_process(self, process, ignore_list=''):
        '''Retrieves the energy consumption of a process and returns the values as a piechart'''

        label_dict = {
        'LLPS': 'Very low pressure steam<br>(T=142,7°C)',
        'LPS' : 'Low pressure steam<br>(T=155,5°C)',
        'MPS' : 'Medium pressure steam<br>(T=214,9°C)',
        'HPS' : 'High pressure steam<br>(T=265,2°C)',
        'HHPS': 'Very high pressure steam>br> (T=311°C)',
        'Electricity': 'Electricity',
        'NG': 'Natural gas',
        'R134A': 'Refrigerant<br>R134A',
        'R717': 'Refrigerant<br>R717',
        'R410A': 'Refrigerant<br>R410A',
        'R41': 'Refrigerant<br>R41',
        'R1150': "Refrigerant<br>R1150",
        'Cooling water': 'Cooling water',
        'Chilled water': 'Chilled water'
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
            'R410A': 'brown',
            'R41': 'turquoise',
            'R1150': "red",
            'Cooling water': 'lightblue',
            'Chilled water': 'darkblue'
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
        fig.update_layout(title_text = f'{process}. {process_name}<br>net energy consumption \
                        in TJ/year',
                        autosize=False,
                        width=1000,
                        height=1000,
                        font=dict(size=30),
                        legend_font=dict(size=25))

        config = {
        'toImageButtonOptions': { 'height': None, 'width': None, }
        }
        fig.show(config=config)


    def energy_cluster(self, ignore_list='' ,normalized=False, title=True):
        '''Retrieves the overall energy consumption of the cluster and
        presents the values in a piechart'''

        label_dict = {
        'LLPS': 'Very low pressure steam<br>(T=142,7°C)',
        'LPS' : 'Low pressure steam<br>(T=155,5°C)',
        'MPS' : 'Medium pressure steam<br>(T=214,9°C)',
        'HPS' : 'High pressure steam<br>(T=265,2°C)',
        'HHPS': 'Very high pressure steam<br>(T=311°C)',
        'Electricity': 'Electricity',
        'NG': 'Natural gas',
        'R134A': 'Refrigerant<br>R134A',
        'R717': 'Refrigerant<br>R717',
        'R410A': 'Refrigerant<br>R410A',
        'R41': 'Refrigerant<br>R41',
        'R1150': "Refrigerant<br>R1150",
        'Cooling water': 'Cooling water',
        'Chilled water': 'Chilled water'
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
            'R410A': 'brown',
            'R41': 'turquoise',
            'R1150': "red",
            'Cooling water': 'lightblue',
            'Chilled water': 'darkblue'
        }
        if normalized is True:
            carbon_prod = 0
            tags,layers,_link_dict=  self.multiplex.get_layers()
            layer_out = tags.index('OUT')

            for link in layers[layer_out].edges:
                if link[1][0] == 'PROD':
                    data = self.multiplex[link[0]][link[1]][link[2]]
                    carbon_prod += data['carbon_content'] * data['mass_flow_rate']

            energy_total = Counter({})
            for node in self.process_nodes.values():
                energy_total += Counter(node['energy_consumption'])

            values=[round(x/carbon_prod,1) for name,x in energy_total.items() \
                    if name not in ignore_list and x != 0]
            utilities=[name for name,x in energy_total.items() \
                    if name not in ignore_list and x != 0]
            figure_title = "Cluster net energy intensity<br>in TJ/ktonne of carbon product"

        else:
            energy_total = Counter({})
            for node in self.process_nodes.values():
                energy_total += Counter(node['energy_consumption'])

            values=[round(x,0) for name,x in energy_total.items() \
                    if name not in ignore_list and x != 0]
            utilities=[name for name,x in energy_total.items() \
                    if name not in ignore_list and  x != 0]
            figure_title = "Cluster<br>net energy consumption in TJ/year"

        labels = [label_dict[name] for name in utilities]
        colors = [color_dict[name] for name in utilities]

        fig = go.Figure(data=[go.Pie(labels=labels,
                             values=values)])
        fig.update_traces(hoverinfo='label+percent', textinfo='value+percent', textfont_size=25,
                        marker=dict(colors=colors, line=dict(color='#000000', width=2)))
        if title is True:
            fig.update_layout(title_text = figure_title,
            autosize = False,
            width=1000,
            height=1000,
            font=dict(size=25),
            legend_font=dict(size=25))
        else:
            fig.update_layout(autosize = False,
            width=1000,
            height=1000,
            font=dict(size=25),
            legend_font=dict(size=25))

        config = {
        'toImageButtonOptions': { 'height': None, 'width': None, }
        }
        fig.show(config=config)
        """fig.write_image("figures/energy_process.svg")"""


    def emissions_cluster(self, ignore_list='',normalized = False):

        if normalized is True:

            figure_title = 'Cluster total emission'

        else:

            figure_title = 'Cluster emission intensity per ktonne of carbon product'

        fig = go.Figure(data=[go.Pie(labels=labels,
                             values=values)])
        fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=30,
                        marker=dict(colors=colors, line=dict(color='#000000', width=2)))
        fig.update_layout(title_text = figure_title,
                        autosize=False,
                        width=1000,
                        height=1000,
                        font=dict(size=30),
                        legend_font=dict(size=28))

        config = {
        'toImageButtonOptions': { 'height': None, 'width': None, }
        }
        fig.show(config=config)
