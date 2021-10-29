import os, warnings, json 
import numpy as np
import pandas as pd 

from warnings import warn
from itertools import combinations
from aspenauto import Model
from py3plex.core import multinet

from petcluster.aspendata import process
from .aspendata import Process
from . import supporting
from petcluster import aspendata


class Multiplex(object):

    def __init__(self):

        self.multiplex = multinet.multi_layer_network(network_type='multiplex')
        self.nodes = {}
        self.process_nodes = {}
        self.background_nodes = {}


    def load_network_aspen(self):
        """Load the cluster using the aspen models, static table and 'process_data.json'"""

        # Check whether the static table has been loaded
        if self._table is None:
            warnings.warn('The static table of the cluster has not been loaded into the model')
            return

        # Load the mapping of all streams entering the process nodes
        list_in = self.table.drop(['Type','OID', 'Stream out', 'Amount out', 'Treatment', 'Notes'], axis = 'columns')
        list_in = list_in.dropna()
        mapping_in = [[x1,x2,x3,x4] for x1, x2, x3, x4 in zip(list_in['Process ID'], list_in['IID'], list_in['Stream in'], list_in['Amount in'])]

        self.mapping_in = {}
        for stream in mapping_in:
            node = stream[0]
            if node not in self.mapping_in.keys():
                self.mapping_in[node] = []
            self.mapping_in[node].append(stream)

        # Load the mapping of all streams leaving the process nodes
        list_out = self.table.drop(['IID', 'Stream in', 'Amount in', 'Type', 'Treatment', 'Notes'], axis = 'columns')
        list_out = list_out.dropna()
        mapping_out = [[x1,x2,x3,x4] for x1, x2, x3, x4 in zip(list_out['Process ID'], list_out['OID'], list_out['Stream out'], list_out['Amount out'])]

        self.mapping_out = {}
        for stream in mapping_out:
            node = stream[0]
            if node not in self.mapping_out.keys():
                self.mapping_out[node] = []
            self.mapping_out[node].append(stream)

        # Make a list of all the files in current directory
        files = [f for f in os.listdir('.') if os.path.isfile(f)]

        # Load the background data from 'background.json'
        with open("background.json") as jsonFile:
            background_data = json.load(jsonFile)
            jsonFile.close()

        # Load the process data from 'process_data.json'
        with open("process_data.json") as jsonFile:
            process_data = json.load(jsonFile)
            jsonFile.close()

        # Load compoment list from 'Components.xlsx'
        self.component_list = pd.read_excel('Components.xlsx', index_col=1)

        # Load the background nodes
        for uid, value in background_data.items():
            self.nodes[uid] = self.background_node(uid, value)
            self.background_nodes[uid] = self.nodes[uid]

        # Iterate over all the files
        link_list = []
        sep = ' '
        for f in files:
            # Only open the Aspen Plus backup files
            if f.endswith('.bkp'):
                # Retrieve the process uid and process name from the Aspen Plus file name
                uid = f.split(sep,1)[0]                 # Retrieve the process uid from the file name               
                uid = uid.replace('.', '')              # Remove the dot present in the uid
                try:
                    aspen_data = supporting.load_aspen_data(f, process_data[uid], self.component_list)
                except KeyError:
                    warn(self.uid, "is not defined in the process data input file")
                    pass
                
                self.nodes[uid] = self.process_node(uid, aspen_data, process_data[uid])
                self.process_nodes[uid] = self.nodes[uid]

                # Create an instance of each link using the static table. 
                # The link property data is retrieved directly from each respective aspen file. 
                # Starting with the incoming links.
                try:
                    for link_in in self.mapping_in[uid]:
                        stream_id = link_in[2]
                        stream = aspen_data.material_all[stream_id]
                        # Collect basic connection data in a list
                        link_data = [link_in[1],link_in[0],link_in[3],link_in[2]]
                        # 
                        link_list.append(self.resource_link(stream, link_data))
                except KeyError:
                    warnings.warn('process', uid, 'not defined in the static table. Check it is defined correctly')
                
                # Link property data is retrieved for the outgoing links. 
                try:
                    for link_out in self.mapping_out[uid]:        
                        stream_id = link_out[2]
                        stream = aspen_data.material_all[stream_id]
                        # Collect basic connection data in a list
                        link_data = [link_out[0], link_out[1], link_out[3], link_out[2]]
                        # 
                        link_list.append(self.resource_link(stream, link_data)) 
                except KeyError:
                    warnings.warn('process', uid, 'not defined in the static table. Check it is defined correctly')

        self.link_list = link_list


    def remove_duplicate_links(self, link_list):
        duplicate_list = []
        for link1, link2 in combinations(link_list,2):
            duplicate_list = self.check_duplicates(link1,link2,duplicate_list)
        if len(duplicate_list) >= 1:
            for duplicate in duplicate_list:
                    link_list.remove(duplicate)
    

    def check_duplicates(self, link1, link2, duplicate_list):
        if link1['source'] is link2['source'] and link1['source_type'] is link2['source_type'] and link1['target'] is link2['target'] and link1['target_type'] is link2['target_type']:
            if abs(link1['mass_flow_rate']-link2['mass_flow_rate']) / link1['mass_flow_rate'] < 0.0001:
                if abs(link1['temperature']-link2['temperature'])/link1['temperature'] < 0.0001 and abs(link1['pressure']-link2['pressure'])/link1['pressure'] < 0.0001:
                    duplicate_list.append(link2)
        return duplicate_list


    def assign_layers_aspen(self, link_list):
        for link in link_list:
            for component, frac in link['mass_fraction'].items():
                if frac >= 0.6:
                    link['source_type'] = self.component_list['Subcluster related'][component]
                    link['target_type'] = self.component_list['Subcluster related'][component]


    def resource_link(self, stream, link_data):

        link_dict = {
            "source": link_data[0],        # Source node
            "source_type": 1,   # Source node layer
            "target": link_data[1],        # Target node
            "target_type": 1,   # Target node layer
            "type": 1,          # ????
            
            "mass_flow_rate": link_data[2],
            "mole_flow_rate": link_data[2] / stream.massflow * stream.moleflow,
            "volume_flow_rate": link_data[2] / stream.massflow * stream.volflow,
            "mass_fraction": stream.massfrac,
            "mole_fraction": stream.molefrac,
            "pressure": stream.pressure,
            "temperature": stream.temperature,
            "carbon_content": 1
        }
        return link_dict


    def process_node(self, uid, aspendata, process_data):

        node_dict = {
            "source": uid,    # Process ID
            "process_type": 1,
            "process_name": process_data['process_name'],
            "energy_consumption": aspendata.energy,
            "area_footprint": process_data['footprint'],
            "equipment_cost": process_data['equipment_cost'],
            "harbor_access": 1,
            "process splittable": 1,
            "opex": 1
        }
        return node_dict

    
    def background_node(self, key, value):
        
        node_dict = {
            "source": key,    # Process ID

            "energy_consumption": 1,
            "environmental_impact": 1
        }
        return node_dict




    @property
    def table(self):
        if self._table is None:
            raise Exception('Static table has not been generated or loaded')
        return self._table


    def create_static_table(self):
        """"Create a static table from Aspen Models"""
        # Creates a static table from all the aspen plus backup files in the current directory
        # the static table is generated as a Pandas DataFrame
        # For each process, the process ID, process name, incoming stream name and flowrate, outgoing stream name and flowrate is stored. 

        files = [f for f in os.listdir('.') if os.path.isfile(f)]
        sep = ' '

        df = pd.DataFrame(np.zeros([0,11]))
        df.columns = ['Process ID', 'Process Name', 'IID', 'Stream in', 'Amount in', 'Type', 'OID', 'Stream out', 'Amount out', 'Treatment', 'Notes']
        row =  0  
        prod_row = 0

        for f in files:
            if f.endswith('.bkp'):
                # Retrieve the process ID and process name from the file name 
                uid = f.split(sep,1)[0]
                ttt = f.split(sep,1)[1]
                process_name = ttt.split('.bkp',1)[0]
                if uid.endswith('.'):
                    uid = uid[:-1]
                
                # Open the Aspen Plus simulation using "aspenauto"
                model = Model(f)
                # Run aspen simulation without error report
                model.run(report_error = False)
                
                for stream in model.material_streams:
                    # Load and store the feed streams in the static table
                    if stream.type is "Feed":
                        df.loc[row, 'Process ID'] = uid
                        df.loc[row, 'Process Name'] = process_name
                        df.loc[row, 'Stream in'] = stream.name
                        df.loc[row, 'Amount in'] = stream.massflow
                        row += 1
                    # Load and store the product streams in the static table
                    elif stream.type is "Product":
                        df.loc[prod_row, 'Process ID'] = uid
                        df.loc[prod_row, 'Process Name'] = process_name
                        df.loc[prod_row, 'Stream out'] = stream.name
                        df.loc[prod_row, 'Amount out'] = stream.massflow
                        prod_row += 1
                        # Load and store the waste streams in the static table
                    elif stream.type is "Waste":
                        df.loc[prod_row, 'Process ID'] = uid
                        df.loc[prod_row, 'Process Name'] = process_name
                        df.loc[prod_row, 'Stream out'] = stream.name
                        df.loc[prod_row, 'Amount out'] = stream.massflow
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
        self._table = df


    def save_static_table(self, excel_file):
        self._table.to_excel(excel_file, index = False)


    def load_static_table(self, excel_file):
        """"Load a static table from Excel"""
        self._table = pd.read_excel(excel_file)

    
    def add_process_static_table(self, aspen_file):
        '''Add a process to the static table'''
        # Add a process to the static table in the current memory
        # e.g. when current table is mapped and a new process has to be added and mapped

        df = self._table
        sep = ' '
        row = len(df.index)
        prod_row = row

        # Retrieve the process ID and process name from the file name 
        uid = aspen_file.split(sep,1)[0]
        ttt = aspen_file.split(sep,1)[1]
        process_name = ttt.split('.bkp',1)[0]

        # Check whether the process is already part of the static table by comparing the process ID
        if uid in self.table.values:
            raise ValueError('The requested process is already part of the static table')

        # Open the Aspen Plus simulation using "aspenauto"
        model = Model(aspen_file)
        # Run aspen simulation without error report
        model.run(report_error = False)
        
        for stream in model.material_streams:
            # Load and store the feed streams in the static table
            if stream.type is "Feed":
                df.loc[row, 'Process ID'] = uid
                df.loc[row, 'Process Name'] = process_name
                df.loc[row, 'Stream in'] = stream.name
                df.loc[row, 'Amount in'] = stream.massflow
                row += 1
            elif stream.type is "Product":
                # Load and store the product streams in the static table
                df.loc[prod_row, 'Process ID'] = uid
                df.loc[prod_row, 'Process Name'] = process_name
                df.loc[prod_row, 'Stream out'] = stream.name
                df.loc[prod_row, 'Amount out'] = stream.massflow
                prod_row += 1
            elif stream.type is "Waste":
                # Load and store the waste streams in the static table
                df.loc[prod_row, 'Process ID'] = uid
                df.loc[prod_row, 'Process Name'] = process_name
                df.loc[prod_row, 'Stream out'] = stream.name
                df.loc[prod_row, 'Amount out'] = stream.massflow
                prod_row += 1  

        # Close the aspen model
        model.close()
        self._table = df



    

