# Este algoritmo busca resolver um problema de otimização sobre um grafo usando técnicas de otimização quântica, 
# especificamente o QAOA, para encontrar uma configuração ótima das arestas do grafo que minimiza o custo total, 
# considerando uma série de restrições que moldam o problema para uma árvore geradora mínima com regras adicionais 
# sobre profundidade e conectividade.

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
