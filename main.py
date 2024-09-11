from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import Sampler
from qiskit_optimization.problems import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
import networkx as nx

# Define o grafo com ordenação consistente
G = nx.Graph()
edges = [(0, 1, 1), (0, 2, 2), (1, 2, 1), (1, 3, 3), (2, 3, 2)]
G.add_weighted_edges_from(edges)
n = G.number_of_nodes()

# Cria o problema QUBO
qubo = QuadraticProgram()

# Adiciona variáveis binárias para cada aresta com uma ordenação consistente de índices
for (i, j, w) in G.edges(data='weight'):
    # Certifique-se de que os nomes das variáveis são consistentes
    if i < j:
        qubo.binary_var(name=f'y_{i}_{j}')
    else:
        qubo.binary_var(name=f'y_{j}_{i}')

# Função objetivo: Minimizar o custo total das arestas incluídas
objective_terms = {f'y_{min(i, j)}_{max(i, j)}': w for (i, j, w) in G.edges(data='weight')}
qubo.minimize(linear=objective_terms)

# Restrições do MST
# 1. Restrição do Nó Raiz
root_constraint = {f'y_{min(i, j)}_{max(i, j)}': 1 for (i, j) in G.edges()}
qubo.linear_constraint(
    linear=root_constraint,
    sense='==',
    rhs=1,
    name='root_constraint'
)

# 2. Atribuição de Profundidade dos Nós
for v in range(n):
    depth_constraint = {f'y_{min(i, j)}_{max(i, j)}': 1 for (i, j) in G.edges(v)}
    qubo.linear_constraint(
        linear=depth_constraint,
        sense='==',
        rhs=1,
        name=f'depth_assignment_{v}'
    )

# 3. Inclusão da Aresta e Correspondência de Profundidade
for (i, j) in G.edges():
    edge_depth_constraint = {f'y_{min(i, j)}_{max(i, j)}': 1}
    qubo.linear_constraint(
        linear=edge_depth_constraint,
        sense='==',
        rhs=0,
        name=f'edge_depth_{i}_{j}'
    )

# 4. Conectividade: Cada nó (exceto a raiz) deve estar conectado a um outro nó
for v in range(1, n):
    connectivity_constraint = {f'y_{min(i, j)}_{max(i, j)}': 1 for (i, j) in G.edges(v)}
    qubo.linear_constraint(
        linear=connectivity_constraint,
        sense='==',
        rhs=1,
        name=f'connectivity_{v}'
    )

# 5. Restrição de Grau: Limita o grau de cada nó
max_degree = 2  # Exemplo de limite de grau
for v in range(n):
    degree_constraint = {f'y_{min(i, j)}_{max(i, j)}': 1 for (i, j) in G.edges(v)}
    qubo.linear_constraint(
        linear=degree_constraint,
        sense='<=',
        rhs=max_degree,
        name=f'degree_constraint_{v}'
    )

# QAOA
backend = AerSimulator()
sampler = Sampler(backend=backend)

optimizer = COBYLA()

qaoa_mes = QAOA(sampler=sampler, optimizer=COBYLA(), initial_point=[0.0, 0.0])
qaoa = MinimumEigenOptimizer(qaoa_mes)

# Solução do problema
qaoa_result = qaoa.solve(qubo)

# Imprime os resultados
print(qaoa_result.prettyprint())
