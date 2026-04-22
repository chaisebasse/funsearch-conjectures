import networkx as nx
import os

def charger_petits_graphes(max_nodes=8):
    filepath = f"data/graphs/graphs{max_nodes}.g6"

    if not os.path.exists(filepath):
        print(f"Fichier {filepath} non trouvé")
        return []

    graphs = []
    with open(filepath, 'r') as f:
        for line in f:
            g6_str = line.strip()
            if g6_str:
                G = nx.from_graph6_bytes(g6_str.encode())
                graphs.append(G)

    print(f"Chargé {len(graphs)} graphes")
    return graphs
