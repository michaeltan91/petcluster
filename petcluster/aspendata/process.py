import warnings
import pandas as pd
import numpy as np
from aspenauto import Model, ObjectCollection
from warnings import warn

from .stream import Stream
from .processdatasheet import ProcessDataSheet
from .utility import Manual_Utility, Natural_Gas_Manual, Steam_Gen_Manual, Steam_Stripping


class Process(object):

    def __init__(self, aspen_file):
        self.energy = {}
        self.material_feed = {}
        self.material_product = {}
        self.material_waste = {}
        self.material_all = {}

        # Load the Aspen model and run it
        self.aspen = Model(aspen_file)
        self.aspen.run(report_error=False)


    def add_manual_steam_gen(self, steam_type, block, heatstream, steam_stream_id):
        '''Add a manual steam generation utility'''
        # Retrieve the heatstream and material stream from the aspen simulation
        hs = self.aspen.heat_streams[heatstream]
        ms =self.aspen.streams[steam_stream_id]
        
        # Assign the steam generation utility to the requested block, 
        steam = Steam_Gen_Manual(block, hs, ms )
        try: 
            self.aspen.utilities[steam_type].blocks[block] = steam
            self.aspen.steam_gen[steam_type].blocks[block] = steam
        
        # When the requested utility is not yet defined, it is created
        except KeyError:
            utility = Manual_Utility()
            self.aspen.utilities[steam_type] = utility 
            self.aspen.steam_gen[steam_type] = utility
            self.aspen.utilities[steam_type].blocks[block] = steam
            self.aspen.steam_gen[steam_type].blocks[block] = steam
            warn("Created utility",steam_type,"if not intended check syntax")

    
    def add_manual_steam_stripping(self, steam_type, block, stream_id):
        
        steam_stream = self.aspen.streams[stream_id]
        steam_stripping = Steam_Stripping(block, steam_stream, steam_type)

        try:
            self.aspen.utilities[steam_type].blocks[block] = steam_stripping
            self.aspen.steam[steam_type].blocks[block] = steam_stripping

        # If the requested utility is not yet defined, it is created
        except KeyError:
            utility = Manual_Utility()
            self.aspen.utilities[steam_type] = utility
            self.aspen.steam[steam_type] = utility
            self.aspen.utilities[steam_type].blocks[block] = steam_stripping
            self.aspen.steam[steam_type].blocks[block] = steam_stripping
            warn("Created utility",steam_type,"if not intended check syntax")


    def add_manual_natural_gas(self, block, ng_stream_id):
        '''Add a manual natural gas utility'''

        # Retrieve the natural gas material stream from the aspen simulation
        ng_stream = self.aspen.streams[ng_stream_id]

        natural_gas = Natural_Gas_Manual(block, ng_stream)
        try:
            self.aspen.utilities['NG'].blocks[block] = natural_gas
            self.aspen.natural_gas['NG'].blocks[block] = natural_gas
        
        # If the requested utility is not yet defined, it is created
        except KeyError:
            utility = Manual_Utility()
            self.aspen.utilities['NG'] = utility
            self.aspen.natural_gas['NG'] = utility
            self.aspen.utilities['NG'].blocks[block] = natural_gas
            self.aspen.natural_gas['NG'].blocks[block] = natural_gas
            warn("Created utility NG if not intended check syntax")


    def load_process_data(self):
        '''
        Load the process data from the Aspen Model
        Add the manual utilities before loading the complete process data!!!!
        '''

        outlet_streams = []
        feed_streams = []
        product_streams = []
        waste_streams = []
        #self.utilities = self.aspen.utilities

        # Fill lists for material feed, product and waste streams
        for stream in self.aspen.material_streams:
            if stream.type is "Feed":
                feed_streams.append(stream.name)
            elif stream.type is "Product":
                product_streams.append(stream.name)
                outlet_streams.append(stream.name)
            elif stream.type is "Waste":
                waste_streams.append(stream.name)
                outlet_streams.append(stream.name)

        # Load material feed data from Aspen model
        for stream_id in feed_streams:
            stream = Stream(self.aspen.streams[stream_id])
            self.material_feed[stream_id] = stream
            self.material_all[stream_id] = stream
        # Load material product data from Aspen model
        for stream_id in product_streams:
            stream = Stream(self.aspen.streams[stream_id])
            self.material_product[stream_id] = stream
            self.material_all[stream_id] = stream
        # Load material waste data from Aspen model
        for stream_id in waste_streams:
            stream = Stream(self.aspen.streams[stream_id])
            self.material_waste[stream_id] = stream
            self.material_all[stream_id] = stream

        # Make a list of the standard steam definitions of the VICI project
        steam_types = [['LLPS','LLPS-GEN'], ['LPS','LPS-GEN'],['MPS','MPS-GEN'], ['HPS','HPS-GEN'], ['HHPS','HHPS-GEN']]

        # Load the total steam duty per type for the process
        for steam in steam_types:
            temp = 0
            # Load the total steam duty being utilized by the process
            try:
                for block in self.aspen.utilities[steam[0]].blocks:
                    temp += block.duty
            except KeyError:
                pass
            # Load the total steam duty being generated by the process
            try:
                for block in self.aspen.utilities[steam[1]].blocks:
                    temp -= block.duty
            except KeyError:
                pass
            # Set the units of energy to TJ per operating year
            self.energy[steam[0]] = temp * 8000 * 1E-6

        # Load the total electricity duty being utilized by the process
        temp = 0
        try:   
            for block in self.aspen.electricity['ELECTRIC'].blocks:
                temp += block.usage
            self.energy['Electricity'] = temp* 8000 * 1E-6 * 3.6
        except KeyError:
            pass

        # Load the total cooling water duty being utilized by the process
        temp = 0
        try:
            for block in self.aspen.coolwater['CW'].blocks:
                temp += block.duty
            self.energy['Cooling water'] = temp * 8000 * 1E-6
        except KeyError:
            pass
        
        # Load the total natural gas duty being utilized by the process
        temp = 0
        try:
            for block in self.aspen.natural_gas['NG'].blocks:
                temp += block.duty
            self.energy['NG'] = temp * 8000 * 1E-6
        except KeyError:
            pass

        # Load chilled water
        temp = 0
        try:
            for block in self.aspen.refrigerant['CHILLED'].blocks:
                temp += block.duty
            self.energy['Chilled Water'] = temp * 8000 * 1E-6
        except KeyError:
            pass
        
        # Load refrigerants
        refrigerant_types = ['R134a', 'R717', 'R-410a', 'R41', 'R1150', 'R740']
        for refrig in refrigerant_types:
            temp = 0 
            try:
                for block in self.aspen.refrigerant[refrig].blocks:
                    temp += block.duty
                self.energy[refrig] = temp * 8000 * 1E-6
            except KeyError:
                pass

        
        header = pd.MultiIndex.from_product([outlet_streams,['m_out','massflow','X']],names=['stream', 'type'])
        df = pd.DataFrame(np.zeros([0,len(header)]),  
                        columns=header)

        for name in outlet_streams:
            count = 0
            for comp, value in self.aspen.streams[name].massfrac.items():
                if value > 0.001:
                    df.loc[count,(name,'m_out')] = comp
                    df.loc[count,(name,'massflow')] = value * self.aspen.streams[name].massflow 
                    count += 1
        self.superstructure = df
        


    def report(self, excel_file):
        
        pds = ProcessDataSheet()
        pds.Print_Mass(self.aspen.streams, excel_file)
        pds.Print_Energy(self.aspen.natural_gas, self.aspen.coolwater, self.aspen.electricity,
        self.aspen.refrigerant, self.aspen.steam, self.aspen.steam_gen, excel_file)


    def close_aspen(self):
        """Closes the Aspen model and shuts down the Engine"""
        self.aspen.close()
        del(self.aspen)



    def e_factor(self):
        """Calculate the environmental factor a process, defined as the mass of waste (excluding water)
        divided by the total mass of product"""
        product_mass = 0
        waste_mass = 0

        # Determine the total product mass
        for name, stream in self.material_feed.items():
            product_mass += stream.massflow
        
        # Determine the total waste mass
        for name, stream in self.material_waste.items():
            waste_mass += stream.massflow
            # Exclude the contribution of water if part of the waste stream
            try:
                waste_mass -= stream.massfrac['H2O'] * stream.massflow
            except KeyError:
                pass

        return waste_mass / product_mass


    def GWP(self):
        
        return 1
    

    def calculate_carbon_fraction(self, component_list):
        """Calculate the carbon fraction of all the material feed, product and waste streams"""
        if isinstance(component_list, pd.DataFrame) is False:
            component_list = pd.read_excel(component_list, index_col=1)

        for name, stream in self.material_feed.items():
            stream.calc_carbon_frac(component_list)

        for name, stream in self.material_product.items():
            stream.calc_carbon_frac(component_list)

        for name, stream in self.material_waste.items():
            stream.calc_carbon_frac(component_list)

        


    def carbon_intensity(self, component_list):
        carbon_feed, carbon_waste, carbon_product = 0, 0, 0
        for name, stream in self.material_feed.items():
            temp = 0
             
            for component, value in stream.molefrac.items():
                temp += stream.moleflow * value * component_list['Carbon Atoms'][component] * 12.01 *8000*1E-6
            stream.carbonfrac = temp/stream.massflow
            carbon_feed += temp

        for name, stream in self.material_product.items():
            temp = 0 
            for component, value in stream.molefrac.items():
                temp += stream.moleflow * value * component_list['Carbon Atoms'][component] * 12.01 *8000*1E-6
            stream.carbonfrac = temp/stream.massflow
            carbon_product += temp

        for name, stream in self.material_waste.items():
            temp = 0 
            for component, value in stream.molefrac.items():
                temp += stream.moleflow * value * component_list['Carbon Atoms'][component] * 12.01 *8000*1E-6
            stream.carbonfrac = temp/stream.massflow
            carbon_waste += temp
        
        balance = carbon_feed - carbon_product - carbon_waste
        if balance/carbon_feed > 0.0001:
            warnings.warn("Carbon leak in process")
        else:
            return min(carbon_product/carbon_feed, 1)


    def process_water(self):

        water = 0
        # Determine the total amount of water used in the process
        for name, stream in self.material_feed.items():
            try:
                water += stream.massfrac['H2O'] * stream.massflow
            except KeyError:
                pass

        return water
