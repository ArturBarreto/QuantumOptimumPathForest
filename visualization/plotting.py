import matplotlib.pyplot as plt
import networkx as nx

def draw_solution(G, solution, title="Minimum Spanning Tree Solution"):
    mst_edges = []
    for (i, j) in G.edges:
        var_name = f'y_{min(i, j)}_{max(i, j)}'
        if solution.get(var_name, 0) == 1:
            mst_edges.append((i, j))

    if mst_edges:
        pos = nx.spring_layout(G)
        nx.draw_networkx_nodes(G, pos)
        nx.draw_networkx_edges(G, pos, edgelist=mst_edges, edge_color='r', width=2)
        nx.draw_networkx_edges(
            G, pos, edgelist=[e for e in G.edges if e not in mst_edges], style='dotted'
        )
        nx.draw_networkx_labels(G, pos)
        plt.title(title)
        plt.show()
    else:
        print("No edges found in the MST solution. Please check the variable consistency.")
