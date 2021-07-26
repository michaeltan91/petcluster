
from .baseobject import BaseObject

class Node(BaseObject):

    def __init__(self):
        
        self.links_in = {}
        self.links_out = {}
        super().__init__()

    


class ProcessNode(Node):

    def __init__(self):
        
        
        self.process_type = ''
        self.process_name = ''
        self.energy_consumption = 0
        self.area_footprint = 0
        self.equipment_cost = 0
        self.harbor_access = False
        self.process_splittable = False
        self.opex = 0

        super().__init__()



class BackgroundNode(Node):

    def __init__(self):
        self.energy_consumption = 0
        self.environmental_impact = {}
        super().__init__()