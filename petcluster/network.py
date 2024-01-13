"""Contains the complex network calculations"""
import networkx as nx
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from py3plex.visualization.multilayer import hairball_plot, plt
import numpy as np

class Network(object):
    """Base network visualization and properties class"""

    def __init__(self, multiplex, nodes, process_nodes):

        self.multiplex=multiplex
        self.nodes = nodes
        self.process_nodes = process_nodes
        self.numeric_network = []


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
            colorscale = 'OrRd'
        ))
        fig.update_traces(colorbar_tickmode="auto",colorbar_ticklabelstep=2,selector=dict(type='heatmap'))
        fig.update_xaxes(side="top", tickangle=-90)
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(**kwargs)
        fig.show()


    def visualize_adjacency_matrix_combined(self, weighted =False, **kwargs):
        layer_list = ["Material", "Steam", "Electricity"]
        weight_options = {
            "Material":"carbon_flow_rate",
            "Steam": "energy",
            "Electricity": "energy"
        }
        i = 1
        fig = make_subplots(rows=1,cols=3, subplot_titles=("Material","Steam","Electricity"))
        for layer in layer_list:
            if weighted is True:
                weight = weight_options[layer]
                numeric_network, node_list = self.adjacency_matrix(weight, layer)
                max_element = np.amax(numeric_network)
                numeric_network = numeric_network/max_element
            else:
                weight = 1
                numeric_network, node_list = self.adjacency_matrix(weight, layer)

            fig.add_trace(go.Heatmap(
            z=numeric_network,
            x=node_list,
            y=node_list,
            xgap =1,
            ygap=1,
            coloraxis = "coloraxis"
            ),1,i)
            i+=1

        fig.update_xaxes(side="top", tickangle=-90)
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(**kwargs, coloraxis={"colorscale":"OrRd"})
        #fig.update_traces(colorbar_tickmode="auto",colorbar_ticklabelstep=4,selector=dict(type='heatmap'))
        if weighted is True:
            fig.update_traces(colorbar_tickmode="auto",colorbar_tick0=0,colorbar_dtick=1 ,selector=dict(type='heatmap'))
        else:
            fig.update_traces(colorbar_tickmode="auto",colorbar_tick0=0,colorbar_dtick="L1.0" ,selector=dict(type='heatmap'))
        fig.show()
        self.numeric_network = numeric_network


    def visualize_hairball(self, node_list="", ignore_list="", draw=True):

        remove_list = []
        if node_list:
            temp = list(x for x in self.multiplex.get_nodes())
            for node in temp:
                if node[0] not in node_list:
                    remove_list.append(node)

            temp2 = temp
            for node in remove_list:
                temp2.remove(node)

        else:
            temp = list(x for x in self.multiplex.get_nodes())
            if ignore_list:
                for node in temp:
                    if node[0] in ignore_list:
                        remove_list.append(node) 

                temp2 = temp
                for node in remove_list:
                    temp2.remove(node)

        subnetwork = self.multiplex.subnetwork(input_list=temp2)
        labels = temp2
        network_colors, graph = subnetwork.get_layers(style="hairball")

        test_colors = []
        for node in graph.nodes():
            if node[1] == "Material":
                test_colors.append("C3")
            elif node[1] == "Steam":
                test_colors.append("C0")
            elif node[1] == "Electricity":
                test_colors.append("C1")

        test_colors = [("C3" if node[1]=="Material" else ("C0" if node[1] =="Steam" else ("C1" if node[1] == "Electricity" else "black"))) for node in graph.nodes]
        test_colors[0] = "C1"
        test_colors[1] = "C0"

        if draw is True:
            hairball_plot(graph, edge_width=0.5,alpha_channel=1,node_size=5 ,draw=draw, color_list= test_colors,scale_by_size=False, legend=True)
            plt.savefig("network.pdf",dpi=600)
            plt.show()
        else:
            return hairball_plot(graph, edge_width=0.5,alpha_channel=1,node_size=5 ,draw=draw, color_list= test_colors,scale_by_size=False, legend=True)