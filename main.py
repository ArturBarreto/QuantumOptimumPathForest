# Este algoritmo busca resolver um problema de otimização sobre um grafo usando técnicas de otimização quântica, 
# especificamente o QAOA, para encontrar uma configuração ótima das arestas do grafo que minimiza o custo total, 
# considerando uma série de restrições que moldam o problema para uma árvore geradora mínima com regras adicionais 
# sobre profundidade e conectividade.

from qiskit_aer import AerSimulator
from qiskit.primitives import BackendSampler
from qiskit_optimization.problems import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_ibm_runtime import QiskitRuntimeService
import matplotlib.pyplot as plt
import os
import time
import networkx as nx

%set_env QXToken=MY_QISKIT_TOKEN
%set_env SIMULATION=False

# Definindo o grafo com 5 nós e arestas com pesos variados
G = nx.Graph()

# Lista de arestas com pesos (i, j, peso)
edges = [
    (0, 1, 2),  # Aresta entre nó 0 e nó 1 com peso 2
    (0, 2, 3),  # Aresta entre nó 0 e nó 2 com peso 3
    (1, 2, 1),  # Aresta entre nó 1 e nó 2 com peso 1
    (1, 3, 4),  # Aresta entre nó 1 e nó 3 com peso 4
    (2, 3, 5),  # Aresta entre nó 2 e nó 3 com peso 5
    (2, 4, 2),  # Aresta entre nó 2 e nó 4 com peso 2
    (3, 4, 1),  # Aresta entre nó 3 e nó 4 com peso 1
    (0, 3, 6),  # Aresta entre nó 0 e nó 3 com peso 6
    (1, 4, 3)   # Aresta entre nó 1 e nó 4 com peso 3
]

# Adiciona as arestas ao grafo
G.add_weighted_edges_from(edges)

# Definir o número de nós
n = G.number_of_nodes()

# Exibe informações sobre o grafo criado
print(f"Número de nós: {n}")
print(f"Número de arestas: {G.number_of_edges()}")
print("Arestas e pesos:")
for edge in G.edges(data=True):
    print(edge)

# Desenhar o grafo
pos = nx.spring_layout(G)  # Layout das posições dos nós
nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=10, font_weight='bold')
labels = nx.get_edge_attributes(G, 'weight')  # Obtém os pesos das arestas
nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
plt.title("Grafo com " + f'{n}' + " Nós e Arestas Ponderadas")
plt.show()

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
# 1. Restrição do Número de Arestas
edge_count_constraint = {f'y_{min(i, j)}_{max(i, j)}': 1 for (i, j) in G.edges()}
qubo.linear_constraint(
    linear=edge_count_constraint,
    sense='==',
    rhs=n - 1,
    name='edge_count_constraint'
)

# 4. Conectividade: Cada nó (exceto a raiz) deve estar conectado a um outro nó
for v in range(1, n):
    connectivity_constraint = {f'y_{min(i, j)}_{max(i, j)}': 1 for (i, j) in G.edges(v)}
    qubo.linear_constraint(
        linear=connectivity_constraint,
        sense='>=',
        rhs=1,
        name=f'connectivity_{v}'
    )

# 5. Restrição de Grau: Limita o grau de cada nó
max_degree = n-1  # Exemplo de limite de grau
for v in range(n):
    degree_constraint = {f'y_{min(i, j)}_{max(i, j)}': 1 for (i, j) in G.edges(v)}
    qubo.linear_constraint(
        linear=degree_constraint,
        sense='<=',
        rhs=max_degree,
        name=f'degree_constraint_{v}'
    )

# Backend

if os.environ['SIMULATION'] == "True":
    # Configurar o backend simulado
    print("Prosseguindo com a simulação...")
    backend = AerSimulator()
else:
    # Configurar o backend para um dispositivo real da IBM
    print("Prosseguindo com hardware quântico da IBM...")
    service = QiskitRuntimeService(channel='ibm_quantum', token=os.environ['QXToken'])
    backend = service.least_busy(n_qubits=127, operational=True, simulator=False)
    print("Conectado ao " + backend.name + "!")
    
sampler = BackendSampler(backend=backend)
optimizer = COBYLA()

# QAOA
p = 1  # Profundidade do circuito QAOA
qaoa_mes = QAOA(sampler=sampler, optimizer=optimizer, reps=p)
qaoa = MinimumEigenOptimizer(qaoa_mes)

# Ponto inicial
start_time = time.time()

# Solução do problema
qaoa_result = qaoa.solve(qubo)

# Ponto final
end_time = time.time()

# Tempo total
execution_time = end_time - start_time
print(f"Tempo de execução: {execution_time} segundos")

# Imprime os resultados
print(qaoa_result.prettyprint())

# Extrair a solução
solution = qaoa_result.variables_dict  # Dicionário de nomes de variáveis para valores

# Desenha a solução MST encontrada
mst_edges = []
for (i, j) in G.edges:
    var_name = f'y_{min(i, j)}_{max(i, j)}'  # Garante que o nome esteja correto
    # Verifica se a variável existe na solução e se o valor é 1
    if solution.get(var_name, 0) == 1:
        mst_edges.append((i, j))

# Verificar se existem arestas na solução MST antes de desenhar
if mst_edges:
    # Desenhar o grafo e a árvore geradora mínima obtida
    pos = nx.spring_layout(G)  # Layout do grafo
    nx.draw_networkx_nodes(G, pos)  # Desenho dos nós
    nx.draw_networkx_edges(G, pos, edgelist=mst_edges, edge_color='r', width=2)  # Arestas da solução MST em vermelho
    nx.draw_networkx_edges(G, pos, edgelist=[e for e in G.edges if e not in mst_edges], style='dotted')  # Outras arestas como pontilhadas
    nx.draw_networkx_labels(G, pos)  # Rótulos dos nós
    plt.title("Solução da Árvore Geradora Mínima")
    plt.show()
else:
    print("Nenhuma aresta encontrada na solução MST. Verifique a consistência das variáveis.")
