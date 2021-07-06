from aspenauto import ObjectCollection

class Manual_Utility(object):
    '''Manual utility class for assigning utilities manually'''

    def __init__(self):
        self.blocks = ObjectCollection()


class Steam_Gen_Manual(object):
    '''Manual steam generation class'''

    def __init__(self, uid, heatstream, stream):
        
        self.uid = uid
        # The duty of steam generation is taken from the heatstream used for 
        # the generation of steam in the aspen simulation
        self.duty = heatstream.duty
        # The usage of the steam generation utility is taken from the mass flowrate of 
        # the produced steam stream
        self.usage = stream.massflow


class Natural_Gas_Manual(object):
    '''Manual natural gas utility class'''

    def __init__(self, uid, ng_stream):

        # The lower heating value of the natural gas mixture was calculated in Aspen Plus at 15C and P=1,02 bar  
        LHV = 37809.49 # kJ/kg
        self.uid = uid
        # The natural gas utility usage is taken from the mass flowrate of the natural gas stream 
        # in the aspen simulation
        self.usage = ng_stream.massflow
        # The duty of the natural gas combustion is calculated from the lower heating value (LHV)
        # of the natural gas mixture at 15C.
        self.duty = self.usage * 1E6 / 8000 * LHV * 1E-3
        