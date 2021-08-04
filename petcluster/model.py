import os
import warnings
import pandas as pd
import numpy as np

from aspenauto import Model
from .link import ResourceLink, ElectricityLink
from .node import ProcessNode, BackgroundNode

import json

class ClusterModel(object):

    def __init__(self):

        self.backgroundnodes = {}
        self.cluster = {}
        self._table = None

        self.nodes = {}
        self.links = {}
    

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



    def load_cluster_aspen(self):
        """Load the cluster using the aspen models, static table and 'process_data.json'"""

        # Check whether the static table has been loaded
        if self._table is None:
            warnings.warn('The static table of the cluster has not been loaded into the model')
            return


        # Load the mapping of all streams entering the process nodes
        #mapping_in = self.table.drop(['Type','OID', 'Stream out', 'Amount out', 'Treatment', 'Notes'], axis = 'columns')
        #mapping_in = mapping_in.dropna()
        list_in = self.table.drop(['Type','OID', 'Stream out', 'Amount out', 'Treatment', 'Notes'], axis = 'columns')
        list_in = list_in.dropna()
        mapping_in = [[x1,x2,x3,x4] for x1, x2, x3, x4 in zip(list_in['Process ID'], list_in['IID'], list_in['Stream in'], list_in['Amount in'])]

        self.mapping_in = {}
        for stream in mapping_in:
            node = stream[0]
            if node not in self.mapping_in.keys():
                self.mapping_in[node] = []
            self.mapping_in[node].append(stream)
        #self.mapping_in =  {x2+'-'+x1:[x2,x1,x3,x4] for x1, x2, x3, x4 in zip(y['Process ID'], y['IID'], y['Stream in'], y['Amount in'])}

        # Load the mapping of all streams leaving the process nodes
        #mapping_out = self.table.drop(['IID', 'Stream in', 'Amount in', 'Type', 'Treatment', 'Notes'], axis = 'columns')
        #mapping_out = mapping_out.dropna()
        list_out = self.table.drop(['IID', 'Stream in', 'Amount in', 'Type', 'Treatment', 'Notes'], axis = 'columns')
        list_out = list_out.dropna()
        mapping_out = [[x1,x2,x3,x4] for x1, x2, x3, x4 in zip(list_out['Process ID'], list_out['OID'], list_out['Stream out'], list_out['Amount out'])]

        self.mapping_out = {}
        for stream in mapping_out:
            node = stream[0]
            if node not in self.mapping_out.keys():
                self.mapping_out[node] = []
            self.mapping_out[node].append(stream)
        #self.mapping_out = {x1+'-'+x2:[x1,x2,x3,x4] for x1, x2, x3, x4 in zip(y['Process ID'], y['OID'], y['Stream out'], y['Amount out'])}


        # Make a list of all the files in current directory
        files = [f for f in os.listdir('.') if os.path.isfile(f)]

        # Load the process data from 'process_data.json'
        with open("process_data.json") as jsonFile:
            process_data = json.load(jsonFile)
            jsonFile.close()
        
        # Iterate over all the files
        sep = ' '
        for f in files:
            # Only open the Aspen Plus backup files
            if f.endswith('.bkp'):
                uid = f.split(sep,1)[0]
                ttt = f.split(sep,1)[1]
                
                uid = uid.replace('.', '')
                process_name = ttt.split('.bkp',1)[0]

                node = ProcessNode(uid)
                node.load_aspen_data(f, process_data)
                self.nodes[uid] = node
        
                
