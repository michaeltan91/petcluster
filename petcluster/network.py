"""Contains the complex network calculations"""
import networkx as nx
import plotly.graph_objects as go

class Network(object):
    """Base network visualization and properties class"""

    def __init__(self, multiplex, nodes, process_nodes):

        self.multiplex=multiplex
        self.nodes = nodes
        self.process_nodes = process_nodes


    def adjacency_matrix(self, weight, layer=None):
        """Returns a numpy array of the adjacency matrix"""
        if layer is None:
            node_list = sorted([x for x in self.multiplex.core_network.nodes if \
                x[0] in self.process_nodes.keys()])

            return (nx.to_numpy_array(self.multiplex.core_network,nodelist=node_list),
                [str(x) for x in node_list])

        else:
            labels, networks, _node_dict = self.multiplex.get_layers()
            try:
                labels.index(layer)
                node_list = sorted([x for x in networks[labels.index(layer)].nodes if \
                    x[0] in self.process_nodes.keys()])

                return (nx.to_numpy_array(networks[labels.index(layer)], nodelist= node_list,\
                        weight=weight), [x[0] for x in node_list])

            except KeyError:
                print(f'Layer {layer} is defined in the model')


    def visualize_adjacency_matrix(self, weighted = False, layer=None, **kwargs):
        """Visualizes the adjacency matrix"""
        weight_options = {
            "Material":"carbon_flow_rate",
            "Steam": "energy",
            "Electricity": "energy"
        }
        if weighted is True:
            if layer is None:
                raise KeyError
            else:
                weight = weight_options[layer]
        else:
            weight = 1


        numeric_network, node_list = self.adjacency_matrix(weight, layer)
        fig = go.Figure(data=go.Heatmap(
            z=numeric_network,
            x=node_list,
            y=node_list,
            xgap =1,
            ygap=1,
            colorscale = 'balance'
        ))
        fig.update_xaxes(side="top", tickangle=-90)
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(**kwargs)
        fig.show()
