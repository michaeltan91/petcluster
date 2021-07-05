from aspenauto import ObjectCollection

class Manual_Utility(object):

    def __init__(self):
        self.blocks = ObjectCollection()


class Steam_Gen_Manual(object):

    def __init__(self, uid, heatstream, stream):
        
        self.uid = uid
        self.duty = heatstream.duty
        self.usage = stream.massflow


class Natural_Gas_Manual(object):

    def __init__(self, uid, ng_stream):

        LHV = 37809.49 # kJ/kg
        self.uid = uid
        self.usage = ng_stream.massflow
        self.duty = self.usage * 1E6 / 8000 * LHV * 1E-3
        