Este script implementa um algoritmo de otimização quântica para resolver um problema de Programação Quadrática Binária (QUBO) utilizando o Quantum Approximate Optimization Algorithm (QAOA) do Qiskit. Aqui está uma explicação passo a passo do que o algoritmo faz:

### 1. Importação de Bibliotecas
As bibliotecas importadas são do Qiskit e NetworkX:
- `qiskit_aer`: Para simulação de circuitos quânticos.
- `qiskit_ibm_runtime`: Para executar algoritmos de otimização quântica.
- `qiskit_optimization`: Para formular problemas de otimização.
- `qiskit_algorithms`: Para aplicar o algoritmo QAOA.
- `networkx`: Para manipulação e criação de grafos.

### 2. Definição do Grafo
O grafo \( G \) é definido com um conjunto de arestas ponderadas. Essas arestas representam conexões entre nós, com pesos associados que influenciam na função objetivo do problema de otimização.

### 3. Criação do Problema QUBO
- Um problema de otimização binária quadrática (QUBO) é criado usando a classe `QuadraticProgram`.
- Variáveis binárias são adicionadas ao problema representando as arestas do grafo. As variáveis são nomeadas de forma consistente para evitar duplicações (ex: `y_0_1` para a aresta entre os nós 0 e 1).

### 4. Função Objetivo
- A função objetivo do QUBO é minimizar o custo total das arestas incluídas no grafo. Os custos são definidos pelos pesos das arestas.

### 5. Restrições
O script adiciona várias restrições para moldar o problema de forma a buscar a Árvore Geradora Mínima (MST) com requisitos adicionais:
1. **Restrição do Nó Raiz:** Garante que uma aresta conecte o grafo a partir de um nó raiz.
2. **Atribuição de Profundidade dos Nós:** Assegura que a profundidade de cada nó seja corretamente definida.
3. **Inclusão da Aresta e Correspondência de Profundidade:** Verifica a correspondência entre a inclusão da aresta e a profundidade do nó.
4. **Conectividade:** Garante que cada nó, exceto a raiz, esteja conectado a pelo menos outro nó.
5. **Restrição de Grau:** Limita o grau de cada nó a um valor máximo (neste exemplo, 2), o que controla a quantidade de conexões que um nó pode ter.

### 6. Configuração do QAOA
- Um simulador quântico (`AerSimulator`) é usado como backend para executar o QAOA.
- Um otimizador clássico, `COBYLA`, é utilizado para ajustar os parâmetros do QAOA.
- O QAOA é configurado com um sampler que executa a simulação quântica e um ponto inicial para os parâmetros do circuito quântico.

### 7. Solução do Problema
- O `MinimumEigenOptimizer` é usado com o QAOA para encontrar a solução ótima para o problema QUBO formulado.
- A solução final, que é a configuração das variáveis que minimiza a função objetivo, é impressa.

### 8. Resultados
- O script imprime os resultados da otimização, que incluem as variáveis binárias que definem a solução ótima para o problema QUBO, respeitando as restrições impostas.
