'''Contains the supporting methods for retrieving aspen data'''
from .aspendata import Process

def load_aspen_data(aspen_file, process_data, component_dict):
    """
    Loads the data from the aspen plus model
    Assigns manual steam generation, manual natural gas or manual steam stripping utilities
    if assigned in process data
    """

    # Start the Aspen Plus engine and open the model file
    # Runs the model without error reports
    aspen_data = Process(aspen_file)

    process_name = process_data['process_name']
    company = process_data['company']
    site = process_data['site']

    # Add manual steam entry to the process for each occurence in the process data
    for steam in process_data['manual_steam']:
        steam_type = steam['steam_type']
        block = steam['block']
        heatstream = steam['heatstream']
        steam_stream = steam['steam_stream']
        aspen_data.add_manual_steam_gen(steam_type, block, heatstream, steam_stream)

    # Add manual steam stripping entry to process for each occurence in the process data
    for steam in process_data['manual_steam_stripping']:
        steam_type = steam['steam_type']
        block = steam['block']
        stream_id = steam['stream_id']
        aspen_data.add_manual_steam_stripping(steam_type, block, stream_id)

    # Add manual natural gas entry to the process for each occurence in the process data
    for gas in process_data['manual_natural_gas']:
        block = gas['block']
        gas_stream_id = gas['ng_stream']
        aspen_data.add_manual_natural_gas(block, gas_stream_id)

    # Add manual electricity entry to the process for each occurence in the process data
    for electricity in process_data['manual_electricity']:
        block = electricity['block']
        electric_stream_id = electricity['elec_stream']
        aspen_data.add_manual_electricity(block, electric_stream_id)

    # Add high temperature heat stream for each occurence in the process data
    for heat in process_data['high_temperature_heat']:
        block = heat['block']
        heatstream_id = heat['heat_stream']
        aspen_data.add_high_temperature_heat(block, heatstream_id)
    

    aspen_data.load_process_data()
    aspen_data.calculate_carbon_fraction(component_dict)
    aspen_data.close_aspen()

    return aspen_data
