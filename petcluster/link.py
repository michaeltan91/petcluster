
from .baseobject import BaseObject
import warnings
class Link(BaseObject):

    def __init__(self, uid, cluster):
        super().__init__(uid, cluster)



class  ResourceLink(Link):

    def __init__(self, uid, cluster):

        self.resource_type = ''
        self.mass_flow_rate = 0
        self.mole_flow_rate = 0
        self.volume_flow_rate = 0
        self.pressure = 0
        self.temperature = 0 
        self.carbon_fraction = 0

        self.mass_fraction = 0
        self.mole_fraction = 0

        self._node_from = []
        self._node_to = []

        super().__init__(uid, cluster)


    @property
    def massflow(self):
        return self.mass_flow_rate

    @property
    def moleflow(self):
        return self.mole_flow_rate

    @property
    def volflow(self):
        return self.volume_flow_rate

    @property
    def massfrac(self):
        return self.mass_fraction

    @property
    def molefrac(self):
        return self.mole_fraction

    @property
    def node_from(self):
        if len(self._node_from) == 0:
            warnings.warn('Link data has not yet been loaded')
        else:
            key = self._node_from
            value = self.cluster.nodes[self._node_from]
            return dict([(key,value)])

    @property
    def node_to(self):
        if len(self._node_to) == 0:
            warnings.warn('Link data has not yet been loaded')
        else:
            key = self._node_to
            value = self.cluster.nodes[self._node_to]
            return dict([(key,value)])
        

    def load_aspen_data(self, stream, massflow, node_from, node_to, node_model):
        self.mass_flow_rate = massflow
        self.mole_flow_rate = massflow / stream.massflow * stream.moleflow
        self.volume_flow_rate = massflow / stream.massflow * stream.volflow
        self.pressure = stream.pressure
        self.temperature = stream.temperature  

        self.mass_fraction = stream.massfrac
        self.mole_fraction = stream.molefrac
        self.carbon_fraction = stream.carbonfrac

        self._node_from = node_from
        self._node_to = node_to

        self.source = node_model



class ElectricityLink(Link):
    
    def __init__(self, uid, cluster):
        self.energy
        super().__init__(uid, cluster)