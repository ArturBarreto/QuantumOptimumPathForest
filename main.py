# This algorithm seeks to solve an optimization problem over a graph using quantum optimization techniques,
# specifically the QAOA (Quantum Approximate Optimization Algorithm), to find an optimal configuration of the
# graph's edges that minimizes the total cost. It does so by considering a series of constraints that shape the
# problem into a minimum spanning tree with additional rules regarding depth and connectivity.

from graph.graph import Graph
from optimization.qubo_problem import QUBOProblem
from visualization.plotting import draw_solution
from utils.config import Config

def main():
    # Initial configurations
    config = Config()

    # Edge definitions with weights
    edges = [
        (0, 1, 2),
        (0, 2, 3),
        (1, 2, 1),
        (1, 3, 4),
        (2, 3, 5),
        (2, 4, 2),
        (3, 4, 1)#,
#        (0, 3, 6),
#        (1, 4, 3)
    ]

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

if __name__ == "__main__":
    main()
