from collections import deque

# Function to find prototypes (root nodes) from the MST
def find_prototypes(mst_edges, graph):
    """
    Finds prototypes (root nodes) for each class.

    Parameters:
    - mst_edges: List of edges (i, j) in the MST.
    - graph: Graph object containing the node_classes.

    Returns:
    - prototypes: Dictionary mapping class labels to prototype nodes.
    """
    prototypes = {}
    nodes_in_mst = set()
    for edge in mst_edges:
        nodes_in_mst.update(edge)

    for node in nodes_in_mst:
        cls = graph.node_classes[node]
        if cls not in prototypes:
            prototypes[cls] = node  # Assign the first encountered node of each class as prototype
    return prototypes

# Function to classify nodes using BFS from each prototype
def classify_nodes(mst_edges, prototypes, graph):
    """
    Classify nodes using BFS from each prototype in the MST.

    Parameters:
    - mst_edges: List of edges (i, j) in the MST.
    - prototypes: Dictionary mapping class labels to prototype nodes.
    - graph: Graph object.

    Returns:
    - node_classes: List where node_classes[i] is the class assigned to node i.
    """
    # Build adjacency list from mst_edges
    adjacency = {}
    for i, j in mst_edges:
        adjacency.setdefault(i, []).append(j)
        adjacency.setdefault(j, []).append(i)

    # Initialize node classes with None
    node_classes = [None] * graph.n
    # Initialize queue for BFS
    queue = deque()
    # Initialize visited set
    visited = set()

    # Start BFS from each prototype
    for cls, node in prototypes.items():
        node_classes[node] = cls
        visited.add(node)
        queue.append((node, cls))

    while queue:
        current_node, current_class = queue.popleft()
        for neighbor in adjacency.get(current_node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                node_classes[neighbor] = current_class
                queue.append((neighbor, current_class))

    return node_classes