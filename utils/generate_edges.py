import random


def generate_edges(num_nodes, weight_min=1, weight_max=10, seed=None):
    """
    Generates a list of edges in the format (node1, node2, weight).

    Parameters:
    - num_nodes: Total number of nodes in the graph.
    - weight_min: Minimum weight of the edges.
    - weight_max: Maximum weight of the edges.
    - seed: (Optional) Seed for the random number generator for reproducibility.

    Returns:
    - A list of tuples representing the edges with integer weights.
    """
    if seed is not None:
        random.seed(seed)

    edges = []
    for node1 in range(num_nodes):
        for node2 in range(node1 + 1, num_nodes):
            # Randomly decide whether to create an edge between node1 and node2
            if random.choice([True, False]):
                weight = random.randint(weight_min, weight_max)  # Integer weight between weight_min and weight_max
                edges.append((node1, node2, weight))

    return edges
