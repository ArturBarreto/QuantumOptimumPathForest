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
    print(f'Node classes: {node_classes}')

    # Instantiate and create the graph
    graph = Graph()
    graph.create_graph(edges)
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
    prototypes = find_prototypes(mst_edges, graph.G)

    # Step 2: Perform the classification phase
    node_classes = classify_nodes(mst_edges, prototypes, graph.G)

    # Step 3: Print results
    print("Node classifications (by prototype):")
    for node, prototype in node_classes.items():
        print(f"Node {node} is classified under Prototype {prototype}")

    # Optional visualization
    colors = ['lightblue', 'lightgreen', 'orange', 'pink', 'yellow', 'red']
    node_colors = [colors[prototypes.index(node_classes[node])] for node in graph.G.nodes]
    pos = nx.spring_layout(graph.G, seed=42)
    nx.draw(graph.G, pos, with_labels=True, node_color=node_colors, node_size=500, font_size=10, font_weight='bold')
    labels = nx.get_edge_attributes(graph.G, 'weight')
    nx.draw_networkx_edge_labels(graph.G, pos, edge_labels=labels)
    plt.title("Classified Graph Based on MST Prototypes")
    plt.show()


if __name__ == "__main__":
    main()
