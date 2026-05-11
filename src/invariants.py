import networkx as nx
import math
import itertools

def independance_max_exact(G):
    """
    Calcule exactement la cardinalité du plus grand ensemble indépendant.
    Faisable en temps raisonnable pour les petits graphes (<=~20 sommets).
    """
    nodes = list(G.nodes())
    n = len(nodes)
    best = 0
    for r in range(n, 0, -1):
        if r <= best:
            break
        for subset in itertools.combinations(nodes, r):
            if all(not G.has_edge(u, v) for u, v in itertools.combinations(subset, 2)):
                best = r
                break
        if best == r:
            break
    return best

def calculer_invariants(G):
    """ Retourne un dictionnaire des invariants classiques """
    n = G.number_of_nodes()
    m = G.number_of_edges()

    # Degrés
    degres = [d for _, d in G.degree()]
    deg_min = min(degres) if degres else 0
    deg_max = max(degres) if degres else 0
    deg_moyen = 2 * m / n if n > 0 else 0

    # Distance
    if nx.is_connected(G) and n > 1:
        diametre = nx.diameter(G)
        rayon = nx.radius(G)
    else:
        diametre = 0
        rayon = 0

    # Densité
    densite = 2 * m / (n * (n - 1)) if n > 1 else 0

    # Triangles
    nb_triangles = sum(nx.triangles(G).values()) // 3

    # Clique maximum
    try:
        clique_max = len(nx.max_weight_clique(G)[0])
    except Exception:
        cliques = list(nx.find_cliques(G))
        clique_max = len(max(cliques, key=len)) if cliques else 1

    # Ensemble indépendant maximum
    independance_max = independance_max_exact(G)

    # Couplage maximum
    couplage_max = len(nx.max_weight_matching(G))

    # Nombre de domination minimum
    try:
        domination_min = len(nx.algorithms.dominating_set.min_weighted_dominating_set(G))
    except Exception:
        domination_min = n // (deg_max + 1) if deg_max >= 0 else n

    # Couverture minimum
    couverture_min = n - independance_max

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
        'domination_min': domination_min,
        'couverture_min': couverture_min,
    }
