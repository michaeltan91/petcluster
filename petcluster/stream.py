


class Stream(object):

    def __init__(self, stream):

        # Collect the mass fractions of the stream of all the components in the simulation
        self.massfrac = stream.massfrac
        #temp = [comp for comp, value in stream.massfrac.items() if value < 0.0001 ]
        # Dispose components with a fraction smaller than 0.0001 
        #for element in temp:
        #    self.massfrac.pop(element)
        
        # Collect the mole fractions of the stream of the all the components in the simulation 
        self.molefrac = stream.molefrac
        #temp = [comp for comp, value in stream.molefrac.items() if value < 0.0001 ]
        # Dispose components with a fraction smaller than 0.0001
        #for element in temp:
        #    self.molefrac.pop(element)


        self.massflow = stream.massflow
        self.moleflow = stream.moleflow
        self.pressure = stream.pressure
        self.temperature = stream.temperature