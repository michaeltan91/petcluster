'''Contains the data structure and retrieval for the stream data from the Aspen Plus simulation'''
import warnings
import copy

class Stream(object):
    '''The main stream class for retrieving Aspen Plus stream data'''
    def __init__(self, stream):

        # Collect the mass fractions of the stream of all the components in the simulation
        self.massfrac = stream.massfrac
        self.massflow_comp = {}
        for comp, massfrac in stream.massfrac.items(): 
            self.massflow_comp[comp] = stream.massflow * massfrac

        pop_list = [comp for comp, value in stream.massfrac.items() if value == 0]
        for element in pop_list:
            self.massfrac = copy.deepcopy(self.massfrac)
            self.massfrac.pop(element)

        # Collect the mole fractions of the stream of the all the components in the simulation
        self.molefrac = stream.molefrac
        pop_list =  [comp for comp, value in stream.molefrac.items() if value == 0]
        for element in pop_list:
            self.molefrac.pop(element)

        # Collect the mass flowrate, mole flowrate, temperature and pressure of the stream
        # from the aspen simulation
        self.massflow = stream.massflow
        self.moleflow = stream.moleflow
        self.volflow = stream.volflow
        self.pressure = stream.pressure
        self.temperature = stream.temperature
        self.carbonfrac = 0
        self.liquid_frac = stream.lfrac
        self.solid_frac = stream.sfrac
        self.vapor_frac = stream.vfrac


    def calc_carbon_frac(self, component_dict):
        '''Calculate the carbon fraction on the stream by mass'''
        temp = 0
        for component, value in self.molefrac.items():
            try:
                temp += self.moleflow * value * component_dict['Carbon Atoms'][component] * \
                12.01100000 *8000*1E-6
            except KeyError:
                warnings.warn(f"Component {component} is not defined in the list of components")
        try:
            self.carbonfrac = temp/self.massflow
        except ZeroDivisionError:
            self.carbonfrac = 0
