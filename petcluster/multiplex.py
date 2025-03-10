'''Contains the main structure and methods'''
import os
import warnings
import json
from itertools import combinations
import numpy as np
import pandas as pd

from aspenauto import Model
from py3plex.core import multinet

from . import supporting
from .performance import Performance
from .network import Network

class Multiplex(object):
    '''Main petcluster class'''
    def __init__(self):

        self.multiplex = multinet.multi_layer_network(network_type='multiplex',directed='True')
        self.nodes = {}
        self.process_nodes = {}
        self.background_nodes = {}
        self.mapping_in = {}
        self.mapping_out = {}
        self.component_dict = {}
        self._table = {}
        self._energy_table = {}
        self._electricity_table = {}

        self.link_list = []
        self.energy_link_list = []
        self.electricity_link_list = []
        self.performance = Performance(self.multiplex, self.nodes, \
                                    self.process_nodes, self.component_dict)
        self.network = Network(self.multiplex, self.nodes, self.process_nodes)

    def load_network_aspen(self):
        """Load the cluster using the aspen models, static table and 'process_data.json'"""

        # Check whether the static table has been loaded
        if self._table is None:
            warnings.warn('The static table of the cluster has not been loaded into the model')
            return

        # Load the mapping of all streams entering the process nodes
        list_in = self.table.drop(['Type','OID', 'Stream out',
        'Amount out', 'Treatment', 'Notes'], axis = 'columns')
        list_in = list_in.dropna()
        mapping_in = [[x1,x2,x3,x4] for x1, x2, x3, x4 in zip(list_in['Process ID'],
        list_in['IID'], list_in['Stream in'], list_in['Amount in'])]

        self.mapping_in = {}
        for stream in mapping_in:
            node = stream[0]
            if node not in self.mapping_in:
                self.mapping_in[node] = []
            self.mapping_in[node].append(stream)

        # Load the mapping of all streams leaving the process nodes
        list_out = self.table.drop(['IID', 'Stream in',
        'Amount in', 'Type', 'Treatment', 'Notes'], axis = 'columns')
        list_out = list_out.dropna()
        mapping_out = [[x1,x2,x3,x4] for x1, x2, x3, x4 in zip(list_out['Process ID'],
        list_out['OID'], list_out['Stream out'], list_out['Amount out'])]

        self.mapping_out = {}
        for stream in mapping_out:
            node = stream[0]
            if node not in self.mapping_out:
                self.mapping_out[node] = []
            self.mapping_out[node].append(stream)

        # Make a list of all the files in current directory
        files = [file_name for file_name in os.listdir('.') if os.path.isfile(file_name)]

        # Load the background data from 'background.json'
        with open("background.json", encoding='utf-8') as json_file:
            background_data = json.load(json_file)
            json_file.close()

        # Load the process data from 'process_data.json'
        with open("process_data.json", encoding='utf-8') as json_file:
            process_data = json.load(json_file)
            json_file.close()

        # Load compoment list from 'Components.xlsx'
        self.component_dict = pd.read_excel('Components.xlsx', index_col=1)

        # Load the background nodes
        for uid, value in background_data.items():
            self.nodes[uid] = self.background_node(uid, value)
            self.background_nodes[uid] = self.nodes[uid]

        # Iterate over all the files
        link_list = []
        sep = ' '

        for file_name in files:
            # Only open the Aspen Plus backup files
            if file_name.endswith('.bkp'):
                # Retrieve the process uid and process name from the Aspen Plus file name
                uid = file_name.split(sep,1)[0]       # Retrieve the process uid from the file name
                uid = uid.replace('.', '')            # Remove the dot present in the uid
                try:
                    aspen_data = supporting.load_aspen_data(file_name, process_data[uid],
                    self.component_dict)
                except KeyError:
                    warnings.warn(f"Process {uid} is not defined in the process data input file")

                print(uid)
                self.nodes[uid] = self.process_node(uid, aspen_data, process_data[uid])
                self.process_nodes[uid] = self.nodes[uid]

                # Create an instance of each link using the static table.
                # The link property data is retrieved directly from each respective aspen file.
                # Starting with the incoming links.
                try:
                    for link_in in self.mapping_in[uid]:
                        try:
                            stream_id = link_in[2]
                            stream = aspen_data.material_all[stream_id]
                            # Collect basic connection data in a list
                            link_data = [link_in[1],link_in[0],link_in[3],None, link_in[2]]
                            #
                            link_list.append(self.resource_link(stream, link_data))
                        except KeyError:
                            warnings.warn(f"Stream {stream_id} in process {uid} \
                            not defined in the static table. Check it is defined correctly")

                    # Link property data is retrieved for the outgoing links.

                    for link_out in self.mapping_out[uid]:
                        try:
                            stream_id = link_out[2]
                            stream = aspen_data.material_all[stream_id]
                            # Collect basic connection data in a list
                            link_data = [link_out[0],link_out[1],link_out[3],link_out[2],None]
                            #
                            link_list.append(self.resource_link(stream, link_data))
                        except KeyError:
                            warnings.warn(f"Stream {stream_id} in process {uid} \
                            not defined in the static table. Check it is defined correctly")
                except KeyError:
                    warnings.warn(f"Process {uid} is not present in the mapping table")
        self.link_list = link_list


    def collect_steam(self):
        """Method collecting the steam demand of processses from the Aspen Plus models"""
        # Make a list of all the files in current directory
        files = [file_name for file_name in os.listdir('.') if os.path.isfile(file_name)]

        # Load the process data from 'process_data.json'
        with open("process_data.json", encoding='utf-8') as json_file:
            process_data = json.load(json_file)
            json_file.close()

        # Load compoment list from 'Components.xlsx'
        self.component_dict = pd.read_excel('Components.xlsx', index_col=1)

        sep = ' '
        for file_name in files:
            # Only open the Aspen Plus backup files
            if file_name.endswith('.bkp'):
                # Retrieve the process uid and process name from the Aspen Plus file name
                uid = file_name.split(sep,1)[0]       # Retrieve the process uid from the file name
                uid = uid.replace('.', '')            # Remove the dot present in the uid
                try:
                    aspen_data = supporting.load_aspen_data(file_name, process_data[uid],
                    self.component_dict)
                except KeyError:
                    warnings.warn(f"Process {uid} is not defined in the process data input file")

                print(uid)
                self.nodes[uid] = self.process_node(uid, aspen_data, process_data[uid])
                self.process_nodes[uid] = self.nodes[uid]


    def load_data_json(self, material_file, steam_file, electricity_file, node_file):
        """Loads the material, steam and electricity link and node data from the json input files"""
        # Load link data
        file_object = open(material_file, "r", encoding="utf-8")
        json_content = file_object.read()
        self.link_list = json.loads(json_content)
        self.remove_excess_material_links()
        # Load steam links
        file_object = open(steam_file, "r", encoding="utf-8")
        json_content = file_object.read()
        self.energy_link_list = json.loads(json_content)
        # Load electricity links
        file_object = open(electricity_file, "r", encoding="utf-8")
        json_content = file_object.read()
        self.electricity_link_list = json.loads(json_content)

        # Load node data
        file_object = open(node_file, "r", encoding="utf-8")
        json_content = file_object.read()
        data = json.loads(json_content)
        self.nodes = data['nodes']
        self.performance.nodes = self.nodes
        self.network.nodes = self.nodes
        self.process_nodes = data['process_nodes']
        self.performance.process_nodes = self.process_nodes
        self.network.process_nodes=self.process_nodes
        self.background_nodes = data['background_nodes']
        self.performance.background_nodes = self.background_nodes

        # Load link data into the model
        self.multiplex.add_edges(self.link_list)
        self.multiplex.add_edges(self.energy_link_list)
        self.multiplex.add_edges(self.electricity_link_list)
        #self.multiplex._couple_all_edges()
        self.couple_nodes()


    def couple_nodes(self):
        """Couples identical nodes across the layers"""
        nodes = {node[0] for node in self.multiplex.core_network.nodes()}
        layers = {node[1] for node in self.multiplex.core_network.nodes()}

        for node in nodes:
            for layer_1 in layers:
                for layer_2 in layers:
                    if layer_1 != layer_2:
                        node_couple=(node,layer_1),(node,layer_2)
                        self.multiplex.core_network.add_edge(node_couple[0],node_couple[1],\
                                                             type="coupling",weight=1)


    def load_energy(self, agg_steam = True):
        """Load steam mapping from the energy table"""
        energy_link_list = []

        list_in = self._energy_table.drop(['Company ID','Company','Site ID','Site name', \
        'Process Name','Notes IN','Steam type OUT','OID','OUT','Notes OUT','Unnamed: 14'],\
                                        axis='columns')
        list_in = list_in.dropna()
        mapping_in = [[x1,x2,x3,x4] for x1, x2, x3, x4 in zip(list_in['Process ID'],
        list_in['IID'], list_in['Steam type IN'], list_in['IN'])]

        list_out = self._energy_table.drop(['Company ID','Company', 'Site ID', 'Site name', \
        'Process Name', 'Notes IN', 'Steam type IN', 'IID', 'IN', 'Notes OUT', 'Unnamed: 14'],\
                                        axis='columns')
        list_out = list_out.dropna()
        mapping_out = [[x1,x2,x3,-x4] for x1, x2, x3, x4 in zip(list_out['Process ID'], \
        list_out['OID'], list_out['Steam type OUT'], list_out['OUT'])]

        for link_in in mapping_in:
            link_data = [link_in[1],link_in[0],link_in[3],link_in[2]]
            energy_link_list.append(self.energy_link(link_data, agg_steam))

        for link_out in mapping_out:
            link_data = [link_out[0],link_out[1],link_out[3],link_out[2]]
            energy_link_list.append(self.energy_link(link_data, agg_steam))
        self.energy_link_list = energy_link_list


    def load_electricity(self):
        """Load electricity mapping from the electricity table"""
        electricity_link_list = []
        agg_steam=False

        list_in = self._electricity_table.drop(['Company ID','Company','Site ID','Site name', \
        'Process Name','Notes IN','Electricity OUT','OID','OUT','Notes OUT'], axis='columns')
        list_in = list_in.dropna()
        mapping_in = [[x1,x2,x3,x4] for x1, x2, x3, x4 in zip(list_in['Process ID'],
        list_in['IID'], list_in['Electricity IN'], list_in['IN'])]

        list_out = self._electricity_table.drop(['Company ID','Company', 'Site ID', 'Site name', \
        'Process Name', 'Notes IN', 'Electricity IN', 'IID', 'IN', 'Notes OUT'],axis='columns')
        list_out = list_out.dropna()
        mapping_out = [[x1,x2,x3,-x4] for x1, x2, x3, x4 in zip(list_out['Process ID'], \
        list_out['OID'], list_out['Electricity OUT'], list_out['OUT'])]

        for link_in in mapping_in:
            link_data = [link_in[1],link_in[0],link_in[3],link_in[2]]
            electricity_link_list.append(self.energy_link(link_data, agg_steam))

        for link_out in mapping_out:
            link_data = [link_out[0],link_out[1],link_out[3],link_out[2]]
            electricity_link_list.append(self.energy_link(link_data, agg_steam))
        self.electricity_link_list = electricity_link_list


    def combine_olefins(self, uid1, uid2):
        """Combine the data from two Aspen Plus Olefin models into a single data enitity"""
        process1 = self.process_nodes[uid1]
        process2 = self.process_nodes[uid2]

        data_type = 'energy_consumption'
        for key in process1[data_type]:
            try:
                process1[data_type][key] += process2[data_type][key]
            except KeyError:
                continue

        data_type = 'steam_usage'
        for key in process1[data_type]:
            try:
                process1[data_type][key] += process2[data_type][key]
            except KeyError:
                continue

        data_type = 'energy_use'
        for key in process1[data_type]:
            try:
                process1[data_type][key] += process2[data_type][key]
            except KeyError:
                continue

        data_type = 'energy_production'
        for key in process1[data_type]:
            try:
                process1[data_type][key] += process2[data_type][key]
            except KeyError:
                continue

        data_type = 'auxiliary_materials'
        for key1, _value1 in process1[data_type].items():
            try:
                for key2, value2 in process2[data_type][key1].items():
                    process1[key1][key2] = value2
            except KeyError:
                pass

        for link in self.link_list:
            if link['source'] == uid2:
                link['source'] = uid1

            if link['target'] == uid2:
                link['target'] = uid1


    def remove_excess_material_links(self):
        """Remove duplicate material flows"""
        del_list = []
        for link1, link2 in combinations(self.link_list,2):
            del_list = self.check_material_flows(link1,link2,del_list)
        if len(del_list) >= 1:
            for duplicate in del_list:
                try:
                    self.link_list.remove(duplicate)
                except ValueError:
                    pass
                    #warnings.warn(f"{duplicate} is not part of the list of links")


    def remove_duplicate_links(self):
        '''Removes duplicate links from the link_list'''
        duplicate_list = []
        for link1, link2 in combinations(self.link_list,2):
            duplicate_list = self.check_duplicates(link1,link2,duplicate_list)
        if len(duplicate_list) >= 1:
            for duplicate in duplicate_list:
                try:
                    self.link_list.remove(duplicate)
                except ValueError:
                    warnings.warn(f'{duplicate} is not part of the list of links')


    def remove_duplicate_links_energy(self):
        '''Removes duplicate links from the link_list'''
        duplicate_list = []
        for link1, link2 in combinations(self.energy_link_list,2):
            duplicate_list = self.check_duplicates(link1,link2,duplicate_list)
        if len(duplicate_list) >= 1:
            for duplicate in duplicate_list:
                try:
                    self.energy_link_list.remove(duplicate)
                except ValueError:
                    warnings.warn(f'{duplicate} is not part of the list of links')


    def remove_duplicate_links_electricity(self):
        '''Removes duplicate links from the link_list'''
        duplicate_list = []
        for link1, link2 in combinations(self.electricity_link_list,2):
            duplicate_list = self.check_duplicates_electricity(link1,link2,duplicate_list)
        if len(duplicate_list) >= 1:
            for duplicate in duplicate_list:
                try:
                    self.electricity_link_list.remove(duplicate)
                except ValueError:
                    warnings.warn(f'{duplicate} is not part of the list of links')


    def check_material_flows(self, link1, link2, del_list):
        """Check if two links are transporting the same chemical and should be combined into one"""
        if link1['source'] != link2['source']:
            #print(5)
            return del_list
        if link1['target'] != link2['target']:
            #print(4)
            return del_list
        if link1['source_type'] != link2['source_type']:
            #print(3)
            return del_list
        if link1['target_type'] != link2['target_type']:
            #print(0)
            return del_list
        if link1["mass_fraction"] != link2["mass_fraction"]:
            #print(1)
            return del_list
        #print(2)
        link1["mass_flow_rate"] += link2["mass_flow_rate"]
        link1["mole_flow_rate"] += link2["mole_flow_rate"]
        link1["volume_flow_rate"] += link2["volume_flow_rate"]
        link1["carbon_flow_rate"] += link2["carbon_flow_rate"]
        del_list.append(link2)
        return del_list


    def check_duplicates(self, link1, link2, duplicate_list):
        '''Check if two links are duplicates by comparing the mass flow rate,
        temperature and pressure'''

        if link1['source'] is not link2['source']:
            return duplicate_list
        if link1['target'] is not link2['target']:
            return duplicate_list
        if link1['source_type'] is not link2['source_type']:
            return duplicate_list
        if link1['target_type'] is not link2['target_type']:
            return duplicate_list
        if abs(link1['mass_flow_rate']-link2['mass_flow_rate']) /  link1['mass_flow_rate'] > 0.0001:
            return duplicate_list
        if abs(link1['temperature']-link2['temperature'])/link1['temperature'] > 0.0001:
            return duplicate_list
        if abs(link1['pressure']-link2['pressure'])/link1['pressure'] > 0.0001:
            return duplicate_list
        duplicate_list.append(link2)
        return duplicate_list


    def check_duplicates_electricity(self, link1, link2, duplicate_list):
        '''Check if two links are duplicates by comparing the mass flow rate,
        temperature and pressure'''
        if link1['source'] is not link2['source']:
            return duplicate_list
        if link1['target'] is not link2['target']:
            return duplicate_list
        if link1['source_type'] is not link2['source_type']:
            return duplicate_list
        if link1['target_type'] is not link2['target_type']:
            return duplicate_list
        if abs(link1['energy']-link2['energy']) /  link1['energy'] > 0.0001:
            return duplicate_list

        duplicate_list.append(link2)
        return duplicate_list


    def process_auxiliary(self, aspendata):
        '''Retrieves the auxiliary stream data from the aspen model and
        returns them in a dictionary'''
        aux_dict = {}
        for aux_type, aux_values in aspendata.material_auxiliary.items():
            aux_dict[aux_type] = {}
            for stream_name, stream in aux_values.items():
                try:
                    aux_dict[aux_type][stream_name] = {
                    "mass_flow_rate": stream.massflow,
                    "mole_flow_rate": stream.moleflow,
                    "volume_flow_rate": stream.volflow,
                    "mass_fraction": stream.massfrac,
                    "mole_fraction": stream.molefrac,
                    "pressure": stream.pressure,
                    "temperature": stream.temperature,
                    "carbon_content": stream.carbonfrac,
                    "liquid_fraction": stream.liquid_frac,
                    "solid_fraction": stream.solid_frac,
                    "vapor_fraction": stream.vapor_frac
                    }
                except KeyError:
                    pass
        return aux_dict


    def assign_layers_aspen(self):
        '''Assign predefined layers to each link in the link_list'''

        for link in self.link_list:
            if link['source'] not in self.process_nodes.keys():
                link['source_type'] = 'IN'
                link['target_type'] = 'IN'

            if link['target'] not in self.process_nodes.keys():
                link['source_type'] = 'OUT'
                link['target_type'] = 'OUT'


    def cluster_material_boundary(self):
        """Assign tag to material links crossing the cluster boundary"""
        for link in self.link_list:
            if link['source'] not in self.process_nodes.keys():
                link['cluster_boundary'] = 'To'

            if link['target'] not in self.process_nodes.keys():
                link['cluster_boundary'] = 'From'


    def cluster_energy_boundary(self):
        """Assign tag to steam links crossing the cluster boundary"""
        for link in self.energy_link_list:
            if link['source'] not in self.process_nodes.keys():
                link['cluster_boundary'] = 'To'

            if link['target'] not in self.process_nodes.keys():
                link['cluster_boundary'] = 'From'


    def cluster_electricity_boundary(self):
        """Assign tag to electricity links crossing the cluster boundary"""
        for link in self.electricity_link_list:
            if link['source'] not in self.process_nodes.keys():
                link['cluster_boundary'] = 'To'

            if link['target'] not in self.process_nodes.keys():
                link['cluster_boundary'] = 'From'


    def resource_link(self, stream, link_data):
        '''Returns a dictionary containing the link data in the format required for py3plex'''

        try:
            moleflow = link_data[2] / stream.massflow * stream.moleflow
            volflow = link_data[2] / stream.massflow * stream.volflow
        except ZeroDivisionError:
            moleflow  = 0
            volflow = 0

        carbon_flow_rate = link_data[2]*stream.carbonfrac

        link_dict = {
            "source": link_data[0],        # Source node
            "source_type": 'Material',   # Source node layer
            "target": link_data[1],        # Target node
            "target_type": 'Material',   # Target node layer
            "type": 1,          # ????

            "source_stream": link_data[3],
            "target_stream": link_data[4],

            "mass_flow_rate": link_data[2],
            "mole_flow_rate": moleflow,
            "volume_flow_rate": volflow,
            "mass_fraction": stream.massfrac,
            "mole_fraction": stream.molefrac,
            "pressure": stream.pressure,
            "temperature": stream.temperature,
            "carbon_content": stream.carbonfrac,
            "carbon_flow_rate": carbon_flow_rate,
            "liquid_fraction": stream.liquid_frac,
            "solid_fraction": stream.solid_frac,
            "vapor_fraction": stream.vapor_frac,

            "cluster_boundary": None
        }
        return link_dict


    def energy_link(self, link_data, aggregated_steam):
        """Returns a dictionary containing the energy link data in the format required by Py3plex"""
        heating_dict = {
            'HHPS': 1.96671347,
            'HPS': 1.63234735,
            'MPS': 1.87787119,
            'LPS': 2.09553499,
            'LLPS': 2.13536712
        }

        if link_data[3] == 'HHPS' or link_data[3] =='HPS' or link_data[3] =='MPS' or \
            link_data[3] =='LPS' or link_data[3] =='LLPS':
            energy_type = link_data[3]
            if aggregated_steam is True:
                layer = 'Steam'
            else:
                layer = link_data[3]


            energy = heating_dict[energy_type] * link_data[2]

            link_dict = {
            "source": link_data[0],
            'source_type': layer,
            "target":link_data[1],
            "target_type": layer,
            "type": 1,

            "energy_type": energy_type,
            "mass_flow_rate": link_data[2],
            "energy": energy,

            "pressure": 1,
            "temperature": 1,

            "cluster_boundary": None
            }
            return link_dict

        elif link_data[3] =='ELECTRIC':
            energy_type = 'Electricity'
            layer = 'Electricity'

            link_dict = {
                "source": link_data[0],
                'source_type': layer,
                "target":link_data[1],
                "target_type": layer,
                "type": 1,

                "energy_type": energy_type,

                "mass_flow_rate": link_data[2],
                "energy": link_data[2],

                "pressure": "N.A.",
                "temperature": "N.A.",

                "cluster_boundary": None
            }
            return link_dict


    def process_node(self, uid, aspendata, process_data):
        '''Returns a dictionary containing the process node data in the
        format required for py3plex'''
        aux_data = self.process_auxiliary(aspendata)
        node_dict = {
            "source": uid,    # Process ID
            "type": 1,
            "name": process_data['process_name'],
            "name_abbrev": process_data['process_name_abbreviation'],
            "energy_consumption": aspendata.energy,
            "steam_usage": aspendata.steam_usage,
            "energy_use": aspendata.energy_use,
            "energy_production": aspendata.energy_production,
            "auxiliary_materials": aux_data,
            "area_footprint": process_data['footprint'],
            "equipment_cost": process_data['equipment_cost'],
            "company": process_data['company'],
            "site": process_data['site'],
            "CAPEX": process_data["CAPEX"],
            "harbor_access": 1,
            "process splittable": 1,
            "opex": 1,
            "stream_table": aspendata.superstructure
        }
        return node_dict


    def background_node(self, key, value):
        '''Returns a dictionary containing the background node data in the
        format required by py3plex'''
        node_dict = {
            "source": key,    # Process ID
            "name": value['name'],
            "energy_consumption": 1,
            "environmental_impact": 1
        }
        return node_dict




    @property
    def table(self):
        '''Returns the static table'''
        if self._table is None:
            raise Exception('Static table has not been generated or loaded')
        return self._table


    def create_static_table(self):
        """"Create a static table from Aspen Models"""
        # Creates a static table from all the aspen plus backup files in the current directory
        # the static table is generated as a Pandas DataFrame
        # For each process, the process ID, process name, incoming stream name and
        # flowrate, outgoing stream name and flowrate is stored.

        files = [file_name for file_name in os.listdir('.') if os.path.isfile(file_name)]
        sep = ' '

        data_frame = pd.DataFrame(np.zeros([0,11]))
        data_frame.columns = ['Process ID', 'Process Name', 'IID', 'Stream in', 'Amount in', 'Type',
        'OID', 'Stream out', 'Amount out', 'Treatment', 'Notes']
        row =  0
        prod_row = 0

        for file_name in files:
            if file_name.endswith('.bkp'):
                # Retrieve the process ID and process name from the file name
                uid = file_name.split(sep,1)[0]
                ttt = file_name.split(sep,1)[1]
                process_name = ttt.split('.bkp',1)[0]
                if uid.endswith('.'):
                    uid = uid[:-1]

                # Open the Aspen Plus simulation using "aspenauto"
                model = Model(file_name)
                # Run aspen simulation without error report
                model.run(report_error = False)

                for stream in model.material_streams:
                    # Load and store the feed streams in the static table
                    if stream.type == "Feed":
                        data_frame.loc[row, 'Process ID'] = uid
                        data_frame.loc[row, 'Process Name'] = process_name
                        data_frame.loc[row, 'Stream in'] = stream.name
                        data_frame.loc[row, 'Amount in'] = stream.massflow
                        row += 1
                    # Load and store the product streams in the static table
                    elif stream.type == "Product":
                        data_frame.loc[prod_row, 'Process ID'] = uid
                        data_frame.loc[prod_row, 'Process Name'] = process_name
                        data_frame.loc[prod_row, 'Stream out'] = stream.name
                        data_frame.loc[prod_row, 'Amount out'] = stream.massflow
                        prod_row += 1
                        # Load and store the waste streams in the static table
                    elif stream.type == "Waste":
                        data_frame.loc[prod_row, 'Process ID'] = uid
                        data_frame.loc[prod_row, 'Process Name'] = process_name
                        data_frame.loc[prod_row, 'Stream out'] = stream.name
                        data_frame.loc[prod_row, 'Amount out'] = stream.massflow
                        prod_row += 1

                if prod_row > row:
                    row = prod_row
                else:
                    row += 1
                    prod_row = row
                print(uid)

                # Closes the Aspen model
                model.close()
        #
        self._table = data_frame


    def save_static_table(self, excel_file):
        '''Saves the static table to an excel file'''
        self._table.to_excel(excel_file, index = False)


    def load_static_table(self, excel_file):
        """"Load a static table from Excel"""
        self._table = pd.read_excel(excel_file)


    def load_energy_table(self, excel_file, sheet_name=0):
        """Load the energy table from Excel"""
        self._energy_table = pd.read_excel(excel_file, sheet_name=sheet_name)


    def load_electricity_table(self, excel_file, sheet_name=0):
        """Load the energy table from Excel"""
        self._electricity_table = pd.read_excel(excel_file, sheet_name=sheet_name)


    def add_process_static_table(self, aspen_file):
        '''Add a process to the static table'''
        # Add a process to the static table in the current memory
        # e.g. when current table is mapped and a new process has to be added and mapped

        data_frame = self._table
        sep = ' '
        row = len(data_frame.index)
        prod_row = row

        # Retrieve the process ID and process name from the file name
        uid = aspen_file.split(sep,1)[0]
        uid = uid.strip('.')
        ttt = aspen_file.split(sep,1)[1]
        process_name = ttt.split('.bkp',1)[0]

        # Check whether the process is already part of the static table by comparing the process ID
        if uid in self.table['Process ID'].values:
            raise ValueError('The requested process is already part of the static table')

        # Open the Aspen Plus simulation using "aspenauto"
        model = Model(aspen_file)
        # Run aspen simulation without error report
        model.run(report_error = False)

        for stream in model.material_streams:
            # Load and store the feed streams in the static table
            if stream.type == "Feed":
                data_frame.loc[row, 'Process ID'] = uid
                data_frame.loc[row, 'Process Name'] = process_name
                data_frame.loc[row, 'Stream in'] = stream.name
                data_frame.loc[row, 'Amount in'] = stream.massflow
                row += 1
            elif stream.type == "Product":
                # Load and store the product streams in the static table
                data_frame.loc[prod_row, 'Process ID'] = uid
                data_frame.loc[prod_row, 'Process Name'] = process_name
                data_frame.loc[prod_row, 'Stream out'] = stream.name
                data_frame.loc[prod_row, 'Amount out'] = stream.massflow
                prod_row += 1
            elif stream.type == "Waste":
                # Load and store the waste streams in the static table
                data_frame.loc[prod_row, 'Process ID'] = uid
                data_frame.loc[prod_row, 'Process Name'] = process_name
                data_frame.loc[prod_row, 'Stream out'] = stream.name
                data_frame.loc[prod_row, 'Amount out'] = stream.massflow
                prod_row += 1

        # Close the aspen model
        model.close()
        self._table = data_frame


    def save_data_json(self, json_file, ):
        """Save background node, process node and material link list to a json file"""
        data = {
            "background_nodes" : self.background_nodes,
            "process_nodes" : self.process_nodes,
            "link_list" : self.link_list
        }

        with open(json_file, "w", encoding='utf-8') as outfile:
            json.dump(data, outfile)


    def read_data_json(self, json_file_material, json_file_nodes):
        """
        file_object = open(json_file, "r", encoding='utf-8')
        json_content = file_object.read()
        data = json.loads(json_content)

        self.process_nodes = data['process_nodes']
        self.background_nodes = data['background_nodes']

        self.nodes = self.process_nodes
        self.nodes.update(self.background_nodes)

        self.link_list = data['link_list']
        """
        file_object = open(json_file_material, "r", encoding="utf-8")
        json_content = file_object.read()
        self.link_list = json.loads(json_content)

        file_object = open(json_file_nodes, "r", encoding="utf-8")
        json_content = file_object.read()
        data = json.loads(json_content)

        self.nodes = data['nodes']
        self.performance.nodes = self.nodes
        self.network.nodes = self.nodes

        self.process_nodes = data['process_nodes']
        self.performance.process_nodes = self.process_nodes
        self.network.process_nodes=self.process_nodes

        self.background_nodes = data['background_nodes']
        self.performance.background_nodes = self.background_nodes
