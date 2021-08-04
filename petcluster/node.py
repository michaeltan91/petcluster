from warnings import warn

from .baseobject import BaseObject
from .aspendata import Process

class Node(BaseObject):

    def __init__(self, uid):
        
        self.links_in = {}
        self.links_out = {}
        super().__init__(uid)

    


class ProcessNode(Node):

    def __init__(self, uid):
        
        self.process_type = ''
        self.process_name = ''
        self.company = ''
        self.site = ''
        self.energy_consumption = 0
        self.area_footprint = 0
        self.equipment_cost = 0
        self.harbor_access = False
        self.process_splittable = False
        self.opex = 0
        self.aspen_data = None

        super().__init__(uid)


    def load_aspen_data(self, aspen_file, process_data):
        """
        Loads the data from the aspen plus model
        Assigns manual steam generation, manual natural gas or manual steam stripping utilities
        if assigned in process data
        """
        
        self.source = aspen_file
        # Start the Aspen Plus engine and open the model file
        # Runs the model without error reports
        self.aspen_data = Process(aspen_file)
        try:
            data = process_data[self.uid]
            self.process_name = data['process_name']
            self.company = data['company']
            self.site = data['site']

            # Add manual steam entry to the process for each occurence in the process data
            for steam in data['manual_steam']:
                steam_type = steam['steam_type']
                block = steam['block']
                heatstream = steam['heatstream']
                steam_steam = steam['steam_stream']
                self.aspen_data.add_manual_steam_gen(steam_type, block, heatstream, steam_steam)

            # Add manual steam stripping entry to process for each occurence in the process data
            for steam in data['manual_steam_stripping']:
                steam_type = steam['steam_type']
                block = steam['block']
                stream_id = steam['stream_id']
                self.aspen_data.add_manual_steam_stripping(steam_type, block, stream_id)

            # Add manual natural gas entry to the process for each occurencen in the process data
            for gas in data['manual_natural_gas']:
                block = gas['block']
                gas_stream_id = gas['ng_stream']
                self.aspen_data.add_manual_natural_gas(block, gas_stream_id)

        except KeyError:
            warn(self.uid, "is not defined in the process data input file")
            pass
        
        self.aspen_data.load_process_data()
        self.aspen_data.close_aspen()



class BackgroundNode(Node):

    def __init__(self, uid):
        self.energy_consumption = 0
        self.environmental_impact = {}
        super().__init__(uid)