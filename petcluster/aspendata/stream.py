'''Contains the data structure and retrieval for the stream data from the Aspen Plus simulation'''


class Stream(object):
    '''The main stream class for retrieving Aspen Plus stream data'''
    def __init__(self, stream):

        # Collect the mass fractions of the stream of all the components in the simulation
        self.massfrac = stream.massfrac

        """
        pop_list = [comp for comp, value in stream.massfrac.items() if value < 0.0001 ]
        # Dispose components with a fraction smaller than 0.0001
        for element in pop_list:
            self.massfrac.pop(element)
        mass_total = sum(self.massfrac.values())
        for comp, value in self.massfrac.items():
            self.massfrac[comp] = value/mass_total
        """
        # Collect the mole fractions of the stream of the all the components in the simulation
        self.molefrac = stream.molefrac
        """
        pop_list = [comp for comp, value in stream.molefrac.items() if value < 0.0001 ]
        # Dispose components with a fraction smaller than 0.0001
        for element in pop_list:
            self.molefrac.pop(element)
        mole_total = sum(self.molefrac.values())
        for comp, value in self.molefrac.items():
            self.molefrac[comp] = value/mole_total
        """
        # Collect the mass flowrate, mole flowrate, temperature and pressure of the stream
        # from the aspen simulation
        self.massflow = stream.massflow
        self.moleflow = stream.moleflow
        self.volflow = stream.volflow
        self.pressure = stream.pressure
        self.temperature = stream.temperature
        self.carbonfrac = 0


    def calc_carbon_frac(self, component_dict):
        '''Calculate the carbon fraction on the stream by mass'''
        temp = 0
        for component, value in self.molefrac.items():
            temp += self.moleflow * value * component_dict['Carbon Atoms'][component] * \
            12.01100000 *8000*1E-6
        self.carbonfrac = temp/self.massflow
