import random

def generate_edges(num_nodes, weight_min=1, weight_max=10, num_classes=2, ensure_connected=True, seed=None):
    """
    Generates a list of edges in the format (node1, node2, weight) and a list of node classes.

    Parameters:
    - num_nodes: Total number of nodes in the graph.
    - weight_min: Minimum weight of the edges.
    - weight_max: Maximum weight of the edges.
    - num_classes: Number of classes to assign to nodes.
    - ensure_connected: Whether to ensure the graph is connected.
    - seed: (Optional) Seed for the random number generator for reproducibility.

    Returns:
    - edges: A list of tuples representing the edges with integer weights.
    - node_classes: A list where node_classes[i] is the class assigned to node i.
    """
    if seed is not None:
        random.seed(seed)

    # Assign classes to nodes
    node_classes = [random.randint(0, num_classes - 1) for _ in range(num_nodes)]

    edges = []
    for node1 in range(num_nodes):
        for node2 in range(node1 + 1, num_nodes):
            if ensure_connected:
                # Always create an edge between node1 and node2
                # Integer weight between weight_min and weight_max
                weight = random.randint(weight_min, weight_max)
                edges.append((node1, node2, weight))
            else:
                # Randomly decide whether to create an edge between node1 and node2
                if random.choice([True, False]):
                    # Integer weight between weight_min and weight_max
                    weight = random.randint(weight_min, weight_max)
                    edges.append((node1, node2, weight))

    return edges, node_classes
