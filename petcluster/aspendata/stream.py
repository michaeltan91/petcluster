


class Stream(object):

    def __init__(self, stream):

        # Collect the mass fractions of the stream of all the components in the simulation
        self.massfrac = stream.massfrac

        pop_list = [comp for comp, value in stream.massfrac.items() if value < 0.0001 ]
        # Dispose components with a fraction smaller than 0.0001 
        for element in pop_list:
            self.massfrac.pop(element)
        mass_total = sum(self.massfrac.values())
        for comp, value in self.massfrac.items():
            self.massfrac[comp] = value/mass_total
        
        # Collect the mole fractions of the stream of the all the components in the simulation 
        self.molefrac = stream.molefrac

        pop_list = [comp for comp, value in stream.molefrac.items() if value < 0.0001 ]
        # Dispose components with a fraction smaller than 0.0001
        for element in pop_list:
            self.molefrac.pop(element)
        mole_total = sum(self.molefrac.values())
        for comp, value in self.molefrac.items():
            self.molefrac[comp] = value/mole_total

        # Collect the mass flowrate, mole flowrate, temperature and pressure of the stream from the aspen simulation
        self.massflow = stream.massflow
        self.moleflow = stream.moleflow
        self.volflow = stream.volflow
        self.pressure = stream.pressure
        self.temperature = stream.temperature
        self.carbonfrac = 0