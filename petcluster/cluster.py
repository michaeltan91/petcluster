from aspenauto import Model, ObjectCollection
import os
import pandas as pd
import numpy as np
import warnings
import pickle

from .aspendata.process import Process

class Cluster(object):

    def __init__(self):
        self.processes = {}


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
        self.table = df


    def load_static_table(self, excel_file):
        """"Load a static table from Excel"""
        self.table = pd.read_excel(excel_file)

    
    def add_process_static_table(self, aspen_file):
        '''Add a process to the static table'''
        # Add a process to the static table in the current memory
        # e.g. when current table is mapped and a new process has to be added and mapped

        df = self.table
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
        self.table = df


    def load_cluster(self):
        '''Load the mass and energy balances of every Aspen Plus backup file in the current directory'''
        files = [f for f in os.listdir('.') if os.path.isfile(f)]
        sep = ' '
        for f in files:
            if f.endswith('.bkp'):
                uid = f.split(sep,1)[0]
                ttt = f.split(sep,1)[1]
                process_name = ttt.split('.bkp',1)[0]

                model = Process(f)
                self.processes[uid] = model
                model.process_data()
                model.close_aspen()


    def load_components(self, component_file):
        '''Load the component list from excel'''
        self.component_list = pd.read_excel(component_file, index_col=1)



class Cluster2(object):

    def __init__(self):
        self.process_nodes = {}
        self.resource_links = {}
        self.electricitly_links = {}


    
    




