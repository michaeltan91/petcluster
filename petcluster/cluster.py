from aspenauto import Model
import os
import pandas as pd
import numpy as np
import warnings

from .process import Process

class Cluster(object):

    def __init__(self):
        self.processes = {}


    def create_static_table(self):
        """"Create a static table from Aspen Models"""
        files = [f for f in os.listdir('.') if os.path.isfile(f)]
        sep = ' '

        df = pd.DataFrame(np.zeros([0,11]))
        df.columns = ['Process ID', 'Process Name', 'IID', 'Stream in', 'Amount in', 'Type', 'OID', 'Stream out', 'Amount out', 'Treatment', 'Notes']
        row =  0  
        prod_row = 0

        for f in files:
            if f.endswith('.bkp'):
                uid = f.split(sep,1)[0]
                ttt = f.split(sep,1)[1]
                process_name = ttt.split('.bkp',1)[0]
                
                model = Model(f)
                model.run(report_error = False)
                
                for stream in model.material_streams:
                    if stream.type is "Feed":
                        df.loc[row, 'Process ID'] = uid
                        df.loc[row, 'Process Name'] = process_name
                        df.loc[row, 'Stream in'] = stream.name
                        df.loc[row, 'Amount in'] = stream.massflow
                        row += 1
                    elif stream.type is "Product":
                        df.loc[prod_row, 'Process ID'] = uid
                        df.loc[prod_row, 'Process Name'] = process_name
                        df.loc[prod_row, 'Stream out'] = stream.name
                        df.loc[prod_row, 'Amount out'] = stream.massflow
                        prod_row += 1
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
                model.close()
        
        self.table = df


    def load_static_table(self, excel_file):
        """"Load a static table from Excel"""
        self.table = pd.read_excel(excel_file)

    
    def add_process_static_table(self, aspen_file):
        
        df = self.table
        sep = ' '
        row = len(df.index)
        prod_row = row

        uid = aspen_file.split(sep,1)[0]
        ttt = aspen_file.split(sep,1)[1]
        process_name = ttt.split('.bkp',1)[0]

        if uid in self.table.values:
            raise ValueError('The requested process is already part of the static table')

        model = Model(aspen_file)
        model.run(report_error = False)

        for stream in model.material_streams:
            if stream.type is "Feed":
                df.loc[row, 'Process ID'] = uid
                df.loc[row, 'Process Name'] = process_name
                df.loc[row, 'Stream in'] = stream.name
                df.loc[row, 'Amount in'] = stream.massflow
                row += 1
            elif stream.type is "Product":
                df.loc[prod_row, 'Process ID'] = uid
                df.loc[prod_row, 'Process Name'] = process_name
                df.loc[prod_row, 'Stream out'] = stream.name
                df.loc[prod_row, 'Amount out'] = stream.massflow
                prod_row += 1
            elif stream.type is "Waste":
                df.loc[prod_row, 'Process ID'] = uid
                df.loc[prod_row, 'Process Name'] = process_name
                df.loc[prod_row, 'Stream out'] = stream.name
                df.loc[prod_row, 'Amount out'] = stream.massflow
                prod_row += 1  

        model.close()
        self.table = df


    def load_cluster(self):

        files = [f for f in os.listdir('.') if os.path.isfile(f)]
        sep = ' '
        for f in files:
            if f.endswith('.bkp'):
                uid = f.split(sep,1)[0]
                ttt = f.split(sep,1)[1]
                process_name = ttt.split('.bkp',1)[0]

                model = Process()
                self.processes[uid] = model
                model.process_data(f)
                model.close_aspen()

