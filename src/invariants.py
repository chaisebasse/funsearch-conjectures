import networkx as nx
import math

def calculer_invariants(G):
    """ Retourne un dictionnaire des invariants classiques """
    n = G.number_of_nodes()
    m = G.number_of_edges()

    # Degrés
    degres = [d for n, d in G.degree()]
    deg_min = min(degres) if degres else 0
    deg_max = max(degres) if degres else 0
    deg_moyen = 2*m / n if n > 0 else 0

    # Distance
    if nx.is_connected(G) and n > 1:
        diametre = nx.diameter(G)
        rayon = nx.radius(G)
    else:
        diametre = 0
        rayon = 0

    # Densité
    densite = 2*m / (n*(n-1)) if n > 1 else 0

    # Triangles
    nb_triangles = sum(nx.triangles(G).values()) // 3

    # Clique maximum
    try:
        # Méthode 1: utiliser max_weight_clique (plus efficace)
        clique_max = len(nx.max_weight_clique(G)[0])  # Retourne (clique, poids)
    except:
        # Méthode 2: fallback sur find_cliques
        cliques = list(nx.find_cliques(G))
        clique_max = len(max(cliques, key=len)) if cliques else 1

    # Ensemble indépendant maximum (approximation rapide)
    # Pour les petits graphes on peut faire exact
    try:
        independance_max = len(nx.maximal_independent_set(G))
    except:
        independance_max = nx.approximation.maximum_independent_set(G)
        independance_max = len(independance_max)

    # Couplage maximum
    couplage_max = len(nx.max_weight_matching(G))

    # Nombre de domination (approximation)
    try:
        # Pour les petits graphes on peut calculer exact
        domination_min = len(nx.algorithms.dominating_set.min_weighted_dominating_set(G))
    except:
        domination_min = n // (deg_max + 1)  # borne simple

    return {
        'n': n,
        'm': m,
        'deg_min': deg_min,
        'deg_max': deg_max,
        'deg_moyen': deg_moyen,
        'diametre': diametre,
        'rayon': rayon,
        'densite': densite,
        'nb_triangles': nb_triangles,
        'clique_max': clique_max,
        'independance_max': independance_max,
        'couplage_max': couplage_max,
        'domination_min': domination_min
    }

if __name__ == "__main__":
    # Test sur un graphe simple
    G = nx.cycle_graph(5)
    inv = calculer_invariants(G)
    print("Invariants pour C5 :", inv)
