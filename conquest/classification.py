import networkx as nx

# Function to find prototypes (root nodes) from the MST
def find_prototypes(mst_edges, graph):
    mst_subgraph = nx.Graph()
    mst_subgraph.add_edges_from(mst_edges)
    connected_components = list(nx.connected_components(mst_subgraph))
    prototypes = []
    for component in connected_components:
        prototype = min(component, key=lambda node: graph.degree[node])
        prototypes.append(prototype)
    return prototypes

# Function to classify nodes using BFS from each prototype
def classify_nodes(mst_edges, prototypes, graph):
    node_classes = {}
    for prototype in prototypes:
        for node in nx.bfs_tree(graph, source=prototype).nodes:
            node_classes[node] = prototype
    return node_classes
