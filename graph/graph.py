import networkx as nx
import matplotlib.pyplot as plt

class Graph:
    def __init__(self):
        self.G = nx.Graph()
        self.node_classes = []
        self.n = 0
        self.pos = None

    def create_graph(self, edges, node_classes):
        self.G.add_weighted_edges_from(edges)
        self.n = self.G.number_of_nodes()
        self.node_classes = node_classes
        print(f"Number of nodes: {self.n}")
        print(f"Number of edges: {self.G.number_of_edges()}")
        print(f'Node classes: {self.node_classes}')
        print("Edges and weights:")
        for edge in self.G.edges(data=True):
            print(edge)

    def draw_graph(self, title="Graph"):
        # Generate a sorted list of unique class labels
        unique_classes = sorted(set(self.node_classes))

        # Define colors (ensure there are enough colors for the number of classes)
        colors = ['orange', 'lightgreen', 'blue', 'pink', 'yellow', 'red']

        # Map each class label to a color
        class_to_color = {cls: colors[i % len(colors)] for i, cls in enumerate(unique_classes)}

        # Assign colors to nodes based on their classes
        node_colors = [class_to_color[self.node_classes[node]] for node in self.G.nodes()]

        self.pos = nx.spring_layout(self.G, seed=42)
        nx.draw(self.G, self.pos, with_labels=True, node_color=node_colors,
                node_size=500, font_size=10, font_weight='bold')
        labels = nx.get_edge_attributes(self.G, 'weight')
        nx.draw_networkx_edge_labels(self.G, self.pos, edge_labels=labels)
        plt.title(title)
        plt.show()
