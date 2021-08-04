
from .baseobject import BaseObject

class Link(BaseObject):

    def __init__(self, uid):
        self.node_from = []
        self.node_to = []
        super().__init__(uid)



class  ResourceLink(Link):

    def __init__(self, uid):

        self.resource_type = ''
        self.mass_flow_rate = 0
        self.mole_flow_rate = 0
        self.volume_flow_rate = 0
        self.pressure = 0
        self.temperature = 0 
        self.carbon_fraction = 0

        self.mass_fraction = 0
        self.mole_fraction = 0

        
        super().__init__(uid)


    def calculate_carbon_content(self, stream, component_list):
        
        total_carbon = 0
        for component, value in stream.molefrac.items():
            total_carbon += stream.moleflow * value * component_list['Carbon Atoms'][component] * 12.01 *8000*1E-6
            carbonfrac = total_carbon/stream.massflow
        return carbonfrac 


class ElectricityLink(Link):
    
    def __init__(self, uid):
        self.energy
        super().__init__(uid)