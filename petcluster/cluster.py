from aspenauto import Process
import os
import timeit
import pandas as pd
import numpy as np
import warnings

class Cluster(object):

    def __init__(self):
        self.adada = 1



    def create_static_table(self):
        
        files = [f for f in os.listdir('.') if os.path.isfile(f)]
        sep = ' '

        test = pd.DataFrame(np.zeros([0,11]))
        test.columns = ['Process ID', 'Process Name', 'IID', 'Stream in', 'Amount in', 'Type', 'OID', 'Stream out', 'Amount out', 'Treatment', 'Notes']
        row =  0  
        prod_row = 0

        for f in files:
            if f.endswith('.bkp'):
                uid = f.split(sep,1)[0]
                ttt = f.split(sep,1)[1]
                process_name = ttt.split('.bkp',1)[0]
                
                temp = Process(f)
                temp.run(report_error = False)
                
                for stream in temp.material_streams:
                    if stream.type is "Feed":
                        test.loc[row, 'Process ID'] = uid
                        test.loc[row, 'Process Name'] = process_name
                        test.loc[row, 'Stream in'] = stream.name
                        test.loc[row, 'Amount in'] = stream.massflow
                        row += 1
                    elif stream.type is "Product":
                        test.loc[prod_row, 'Process ID'] = uid
                        test.loc[prod_row, 'Process Name'] = process_name
                        test.loc[prod_row, 'Stream out'] = stream.name
                        test.loc[prod_row, 'Amount out'] = stream.massflow
                        prod_row += 1
                    elif stream.type is "Waste":
                        test.loc[prod_row, 'Process ID'] = uid
                        test.loc[prod_row, 'Process Name'] = process_name
                        test.loc[prod_row, 'Stream out'] = stream.name
                        test.loc[prod_row, 'Amount out'] = stream.massflow
                        prod_row += 1
                
                if prod_row > row:
                    row = prod_row
                else:
                    row += 1
                    prod_row = row
                print(uid)
                temp.close()
        
        self.table = test

    def load_static_table(self, excel_file):

        self.table = pd.read_excel(excel_file)
