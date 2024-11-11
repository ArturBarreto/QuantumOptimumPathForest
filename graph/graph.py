import networkx as nx
import matplotlib.pyplot as plt

class Graph:
    def __init__(self):
        self.G = nx.Graph()
        self.n = 0
        self.pos = None

    def create_graph(self, edges):
        self.G.add_weighted_edges_from(edges)
        self.n = self.G.number_of_nodes()
        print(f"Number of nodes: {self.n}")
        print(f"Number of edges: {self.G.number_of_edges()}")
        print("Edges and weights:")
        for edge in self.G.edges(data=True):
            print(edge)

    def draw_graph(self, title="Graph"):
        self.pos = nx.spring_layout(self.G, seed=42)
        nx.draw(self.G, self.pos, with_labels=True, node_color='lightblue',
                node_size=500, font_size=10, font_weight='bold')
        labels = nx.get_edge_attributes(self.G, 'weight')
        nx.draw_networkx_edge_labels(self.G, self.pos, edge_labels=labels)
        plt.title(title)
        plt.show()
