# This algorithm seeks to solve an optimization problem over a graph using quantum optimization techniques,
# specifically the QAOA (Quantum Approximate Optimization Algorithm), to find an optimal configuration of the
# graph's edges that minimizes the total cost. It does so by considering a series of constraints that shape the
# problem into a minimum spanning tree with additional rules regarding depth and connectivity.

from graph.graph import Graph
from optimization.qubo_problem import QUBOProblem
from visualization.plotting import draw_solution
from utils.config import Config
from utils.generate_edges import generate_edges

def main():
    # Initial configurations
    config = Config()

    # Edge definitions with weights
    # edges = [
    #     (0, 1, 2)
    #    ,(0, 2, 3)
    #    ,(1, 2, 1)
    #    ,(1, 3, 4)
    #    ,(2, 3, 5)
    #    ,(2, 4, 2)
    #    ,(3, 4, 1)
    #    ,(0, 3, 6)
    #    ,(1, 4, 3)
    # ]

    # ToDo: Implement as cartesian coordinates
    # edges = [
    #     # Component 1
    #      (0, 1, 3)  # Edge between node 0 and node 1 with weight 3
    #     ,(0, 2, 5)  # Edge between node 0 and node 2 with weight 5
    #     ,(1, 2, 1)  # Edge between node 1 and node 2 with weight 1
    #
    #     # Component 2
    #     ,(3, 4, 2)  # Edge between node 3 and node 4 with weight 2
    #     ,(3, 5, 4)  # Edge between node 3 and node 5 with weight 4
    #     ,(4, 5, 1)  # Edge between node 4 and node 5 with weight 1
    #
    #     # Component 3
    #     ,(6, 7, 1)  # Edge between node 6 and node 7 with weight 1
    #     ,(5, 6, 8)  # Edge between node 5 and node 6 with weight 8
    #
    #     # Connecting components 1 and 3
    #     ,(1, 7, 2)  # Edge between node 1 and node 7 with weight 2
    #     ,(1, 6, 4)  # Edge between node 1 and node 6 with weight 4
    #
    #     # Connecting components 2 and 3
    #     ,(4, 6, 7)  # Edge between node 4 and node 6 with weight 7
    # ]

    # Example usage:
    edges, node_classes = generate_edges(7, num_classes=2, seed=42, ensure_connected=False)

    # Instantiate and create the graph
    graph = Graph()
    graph.create_graph(edges, node_classes)
    graph.draw_graph(title="Graph with Nodes and Weighted Edges")

    # Configure and solve the QUBO problem
    qubo_problem = QUBOProblem(graph.G, config)
    qubo_problem.configure_variables()
    qubo_problem.define_objective_function()
    qubo_problem.add_constraints()
    solution = qubo_problem.solve_problem()

    # Visualize the solution
    draw_solution(graph.G, solution)

    from conquest.classification import find_prototypes, classify_nodes
    import networkx as nx
    import matplotlib.pyplot as plt

    mst_edges = []
    for (i, j) in graph.G.edges:
        var_name = f'y_{min(i, j)}_{max(i, j)}'
        if solution.get(var_name, 0) == 1:
            mst_edges.append((i, j))

    # Step 1: Extract prototypes from the MST
    prototypes = find_prototypes(mst_edges, graph)

    # Step 2: Classify nodes using BFS from prototypes
    classified_node_classes = classify_nodes(mst_edges, prototypes, graph)

    # Step 3: Print results
    print("Prototypes:")
    for cls, node in prototypes.items():
        print(f"Node {node} (Class {cls})")

    print("\nClassified Nodes:")
    for node, cls in enumerate(classified_node_classes):
        print(f"Node {node} (Class {cls}) is classified under Prototype {prototypes.get(cls)} ")

    # Optional visualization

    # Create a set of MST edges
    mst_edge_set = set()
    for edge in mst_edges:
        # Ensure edges are stored with sorted node tuples
        mst_edge_set.add((min(edge[0], edge[1]), max(edge[0], edge[1])))

    # Generate a sorted list of unique class labels
    unique_classes = sorted(set(classified_node_classes))

    # Define colors (ensure there are enough colors for the number of classes)
    colors = ['orange', 'lightgreen', 'blue', 'pink', 'yellow', 'red']

    # Map each class label to a color
    class_to_color = {cls: colors[i % len(colors)] for i, cls in enumerate(unique_classes)}

    # Assign colors to nodes based on their classes
    node_colors = [class_to_color[classified_node_classes[node]] for node in graph.G.nodes()]

    # Use the same positions for consistency
    pos = nx.spring_layout(graph.G, seed=42)

    # Create a figure
    plt.figure(figsize=(10, 8))

    # Draw all nodes
    nx.draw_networkx_nodes(graph.G, pos, nodelist=graph.G.nodes(),
                           node_color=node_colors, node_size=500)

    # Draw labels for all nodes
    nx.draw_networkx_labels(graph.G, pos, labels={node: node for node in graph.G.nodes()},
                            font_size=10, font_weight='bold')

    # Assign colors to edges based on whether they are in the MST and connect nodes of the same class
    edge_colors = []
    for edge in graph.G.edges():
        edge_key = (min(edge[0], edge[1]), max(edge[0], edge[1]))
        # Check if edge is in MST
        if edge_key in mst_edge_set:
            # Check if nodes are in the same class
            if classified_node_classes[edge[0]] == classified_node_classes[edge[1]]:
                edge_colors.append('red')  # MST edge connecting same class nodes
            else:
                edge_colors.append('lightgray')  # MST edge connecting different class nodes
        else:
            edge_colors.append('lightgray')  # Non-MST edge

    # Draw all edges with assigned colors
    nx.draw_networkx_edges(graph.G, pos, edgelist=graph.G.edges(), edge_color=edge_colors, width=2)

    # Optionally, draw edge labels for the entire graph
    labels = nx.get_edge_attributes(graph.G, 'weight')
    nx.draw_networkx_edge_labels(graph.G, pos, edge_labels=labels)

    # Finalize and display the plot
    plt.axis('off')
    plt.title("Classified Graph Based on MST Prototypes")
    plt.show()


if __name__ == "__main__":
    main()
