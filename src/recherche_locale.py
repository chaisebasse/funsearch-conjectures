import random
import networkx as nx
import copy
import time
import math
import os
import json
from chargement_graphes import charger_petits_graphes
from invariants import calculer_invariants
from generate_conjectures import generer_conjecture
from validate_conjecture import verifier_classe

# Convention : la fonction objectif d'une conjecture "Y <= f(X)" est
#   obj(G) = Y(G) - f(X(G))
# Un contre-exemple est un graphe où obj(G) > 0  (la conjecture est violée).
# Le score d'une conjecture = temps (en secondes) avant de trouver un tel
# contre-exemple, plafonné à temps_max. Un score élevé = conjecture difficile.

def evaluer_conjecture_sur_graphe(G, conjecture):
    """
    Retourne obj(G) = Y(G) - f(X(G)).
    - Si > 0 : contre-exemple (conjecture violée).
    - Si <= 0 : conjecture respectée sur ce graphe.
    - Retourne -inf si G n'appartient pas à la classe ou si f échoue.
    """
    if not verifier_classe(G, conjecture['classe']):
        return -float('inf')

    inv = calculer_invariants(G)
    Y_val = inv[conjecture['Y']]
    X_val = inv[conjecture['X']]
    
    try:
        fX = conjecture['f'](X_val)
    except Exception:
        return -float('inf')

    return Y_val - fX


def muter_graphe(G):
    """
    Applique une mutation aléatoire en préservant la connexité.
    Retourne le nouveau graphe, ou None si la mutation est impossible.
    """
    G2 = copy.deepcopy(G)
    n = G2.number_of_nodes()

    mutation_type = random.choice(['add_edge', 'remove_edge', 'add_node', 'remove_node'])

    if mutation_type == 'add_edge' and n >= 2:
        non_edges = [(u, v) for u in G2.nodes() for v in G2.nodes()
                     if u < v and not G2.has_edge(u, v)]
        if non_edges:
            u, v = random.choice(non_edges)
            G2.add_edge(u, v)
            return G2

    elif mutation_type == 'remove_edge' and G2.number_of_edges() > n - 1:
        edges = list(G2.edges())
        random.shuffle(edges)
        for u, v in edges:
            G2.remove_edge(u, v)
            if nx.is_connected(G2):
                return G2
            G2.add_edge(u, v)  # Annuler : rendrait le graphe déconnecté
        return None

    elif mutation_type == 'add_node':
        nouveau_id = max(G2.nodes()) + 1 if G2.nodes() else 0
        G2.add_node(nouveau_id)
        nb_voisins = random.randint(1, min(3, n)) if n > 0 else 1
        if n > 0:
            voisins = random.sample(list(G2.nodes() - {nouveau_id}), min(nb_voisins, n))
            for v in voisins:
                G2.add_edge(nouveau_id, v)
        return G2

    elif mutation_type == 'remove_node' and n > 3:
        sommets = list(G2.nodes())
        random.shuffle(sommets)
        for s in sommets:
            G3 = copy.deepcopy(G2)
            G3.remove_node(s)
            if nx.is_connected(G3):
                return G3
        return None

    return None


def _graphe_connexe_aleatoire(taille):
    """Génère un graphe connexe aléatoire de `taille` sommets."""
    while True:
        G = nx.gnm_random_graph(taille, taille + random.randint(1, max(1, taille // 2)))
        if nx.is_connected(G):
            return G


def recherche_contre_exemple(conjecture, temps_max=60, taille_initiale=10):
    """
    Recherche un contre-exemple par recuit simulé (simulated annealing).

    Retourne:
        (temps_trouve: float, graphe: Graph) si contre-exemple trouvé
        (None, None) si aucun contre-exemple dans le délai imparti
    """
    start_time = time.time()

    G = _graphe_connexe_aleatoire(taille_initiale)
    meilleur_score = evaluer_conjecture_sur_graphe(G, conjecture)
    meilleur_graphe = G
    tentatives_sans_progres = 0
    temperature = 1.0

    while time.time() - start_time < temps_max:
        nouveau_G = muter_graphe(meilleur_graphe)
        if nouveau_G is None:
            nouveau_G = _graphe_connexe_aleatoire(taille_initiale)

        nouveau_score = evaluer_conjecture_sur_graphe(nouveau_G, conjecture)

        # Contre-exemple trouvé (obj > 0)
        if nouveau_score > 0:
            return time.time() - start_time, nouveau_G

        # Critère d'acceptation
        if nouveau_score > meilleur_score:
            meilleur_score = nouveau_score
            meilleur_graphe = nouveau_G
            tentatives_sans_progres = 0
        else:
            delta = nouveau_score - meilleur_score
            if temperature > 1e-10 and random.random() < math.exp(delta / temperature):
                meilleur_graphe = nouveau_G
                tentatives_sans_progres = 0
            else:
                tentatives_sans_progres += 1

        temperature *= 0.99

        # Redémarrage si stagnation
        if tentatives_sans_progres > 50:
            G = _graphe_connexe_aleatoire(taille_initiale)
            meilleur_graphe = G
            meilleur_score = evaluer_conjecture_sur_graphe(G, conjecture)
            tentatives_sans_progres = 0
            temperature = 1.0

    return None, None


def calculer_score_conjecture(conjecture, temps_max=60):
    """
    Score d'une conjecture :
    - 0.0  → contre-exemple trouvé immédiatement sur les petits graphes (<=8 sommets)
    - t    → temps (secondes) mis par la recherche locale pour trouver un contre-exemple
    - temps_max → aucun contre-exemple trouvé dans le délai : conjecture résistante
    """
    petits_graphes = charger_petits_graphes(8)
    for G in petits_graphes:
        if verifier_classe(G, conjecture['classe']):
            inv = calculer_invariants(G)
            Y_val = inv[conjecture['Y']]
            X_val = inv[conjecture['X']]
            try:
                fX = conjecture['f'](X_val)
                if Y_val > fX + 1e-9:
                    print("  Contre-exemple trouvé sur petits graphes → score = 0")
                    return 0.0
            except Exception:
                pass

    print(f"  Lancement recherche locale (max {temps_max}s)...")
    temps_trouve, _ = recherche_contre_exemple(conjecture, temps_max)

    if temps_trouve is None:
        print(f"  Aucun contre-exemple trouvé en {temps_max}s → score = {temps_max}")
        return float(temps_max)
    else:
        print(f"  Contre-exemple trouvé en {temps_trouve:.2f}s → score = {temps_trouve:.2f}")
        return temps_trouve


def explorer_conjectures(nb_conjectures=100):
    """
    Génère et évalue un grand nombre de conjectures, sauvegarde les meilleures.
    """
    results = []
    os.makedirs('conjectures', exist_ok=True)
    os.makedirs('results', exist_ok=True)

    for i in range(nb_conjectures):
        print(f"\n--- Conjecture {i+1}/{nb_conjectures} ---")

        conj = generer_conjecture()
        print(f"Test : {conj['texte']}")

        try:
            score = calculer_score_conjecture(conj, temps_max=30)
            conj['score'] = score
            conj['score_str'] = f"{score:.1f}s"
            print(f"Score : {score:.1f} secondes")
        except Exception as e:
            print(f"Erreur : {e}")
            conj['score'] = 0
            conj['score_str'] = "erreur"

        results.append(conj)

        # Sauvegarde progressive
        with open('results/conjectures_evaluees.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)

    # Trier par score décroissant
    results.sort(key=lambda x: x['score'], reverse=True)

    # Sauvegarder les meilleures (score >= 20s)
    conjectures = [c for c in results]
    with open('conjectures/conjectures.json', 'w') as f:
        json.dump(conjectures, f, indent=2, default=str)

    print("\n=== TOP 5 CONJECTURES ===")
    for i, conj in enumerate(results[:5]):
        print(f"{i+1}. {conj['texte']} → {conj['score']:.1f}s")

    return results
