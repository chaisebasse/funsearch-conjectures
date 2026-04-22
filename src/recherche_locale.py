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

def verifier_classe(G, classe):
    """
    Vérifie si G appartient à la classe donnée
    """
    if classe == "connexe":
        return nx.is_connected(G)
    elif classe == "biparti":
        return nx.is_bipartite(G)
    elif classe == "planaire":
        return nx.is_planar(G)
    elif classe == "sans_triangle":
        return sum(nx.triangles(G).values()) == 0
    elif classe == "sans_griffe":
        # Vérification simplifiée pour les petits graphes
        for v in G.nodes():
            voisins = list(G.neighbors(v))
            if len(voisins) >= 3:
                # Chercher 3 voisins indépendants
                for i in range(len(voisins)):
                    for j in range(i+1, len(voisins)):
                        if G.has_edge(voisins[i], voisins[j]):
                            break
                    else:
                        continue
                    break
                else:
                    return False
        return True
    else:
        return nx.is_connected(G)  # Par défaut

def evaluer_conjecture_sur_graphe(G, conjecture):
    """
    Retourne Y - f(X)
    Si > 0, la conjecture est violée (contre-exemple)
    """
    inv = calculer_invariants(G)

    # Vérifier la classe
    if not verifier_classe(G, conjecture['classe']):
        return -float('inf')

    Y_val = inv[conjecture['Y']]
    X_val = inv[conjecture['X']]

    try:
        fX = conjecture['f'](X_val)
    except Exception as e:
        print(f"  Erreur calcul f({X_val}): {e}")
        return -float('inf')

    return Y_val - fX

def muter_graphe(G):
    """
    Applique une mutation aléatoire en gardant la connexité
    """
    G2 = copy.deepcopy(G)
    n = G2.number_of_nodes()

    mutation_type = random.choice(['add_edge', 'remove_edge', 'add_node', 'remove_node'])

    # 1. Ajouter une arête
    if mutation_type == 'add_edge' and n >= 2:
        non_edges = [(u,v) for u in range(n) for v in range(u+1,n) if not G2.has_edge(u,v)]
        if non_edges:
            u,v = random.choice(non_edges)
            G2.add_edge(u,v)
            return G2

    # 2. Supprimer une arête (en gardant connexe)
    elif mutation_type == 'remove_edge' and G2.number_of_edges() > n-1:
        edges = list(G2.edges())
        random.shuffle(edges)
        for u,v in edges:
            G2.remove_edge(u,v)
            if nx.is_connected(G2):
                return G2
            G2.add_edge(u,v)
        return None

    # 3. Ajouter un sommet
    elif mutation_type == 'add_node':
        nouveau_id = n
        G2.add_node(nouveau_id)
        nb_voisins = random.randint(1, min(3, n)) if n > 0 else 1
        if n > 0:
            voisins = random.sample(range(n), min(nb_voisins, n))
            for v in voisins:
                G2.add_edge(nouveau_id, v)
        return G2

    # 4. Supprimer un sommet (en gardant connexe)
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

def recherche_contre_exemple(conjecture, temps_max=60, taille_initiale=10):
    """
    Recherche un contre-exemple par recherche locale
    Retourne (temps_trouve, graphe_contre_exemple) ou (None, None)
    """
    start_time = time.time()

    # Générer graphe initial aléatoire connexe
    G = nx.gnm_random_graph(taille_initiale, taille_initiale + random.randint(1, 3))
    while not nx.is_connected(G):
        G = nx.gnm_random_graph(taille_initiale, taille_initiale + random.randint(1, 5))

    meilleur_score = evaluer_conjecture_sur_graphe(G, conjecture)
    meilleur_graphe = G
    tentatives_sans_progres = 0
    temperature = 1.0
    iteration = 0

    while time.time() - start_time < temps_max:
        iteration += 1

        # Mutation
        nouveau_G = muter_graphe(meilleur_graphe)
        if nouveau_G is None:
            # Redémarrage aléatoire
            nouveau_G = nx.gnm_random_graph(taille_initiale, taille_initiale + random.randint(1, 5))
            while not nx.is_connected(nouveau_G):
                nouveau_G = nx.gnm_random_graph(taille_initiale, taille_initiale + random.randint(1, 5))

        # Évaluer
        nouveau_score = evaluer_conjecture_sur_graphe(nouveau_G, conjecture)

        # Si contre-exemple trouvé (score > 0)
        if nouveau_score > 0:
            temps_trouve = time.time() - start_time
            return temps_trouve, nouveau_G

        # Critère d'acceptation
        if nouveau_score > meilleur_score:
            meilleur_score = nouveau_score
            meilleur_graphe = nouveau_G
            tentatives_sans_progres = 0
        else:
            delta = nouveau_score - meilleur_score
            if random.random() < math.exp(delta / temperature):
                meilleur_graphe = nouveau_G
                tentatives_sans_progres = 0
            else:
                tentatives_sans_progres += 1

        # Refroidissement et redémarrage si stagnation
        temperature *= 0.99
        if tentatives_sans_progres > 50:
            G = nx.gnm_random_graph(taille_initiale, taille_initiale + random.randint(1, 5))
            while not nx.is_connected(G):
                G = nx.gnm_random_graph(taille_initiale, taille_initiale + random.randint(1, 5))
            meilleur_graphe = G
            meilleur_score = evaluer_conjecture_sur_graphe(G, conjecture)
            tentatives_sans_progres = 0
            temperature = 1.0

    return None, None

def calculer_score_conjecture(conjecture, temps_max=60):
    """
    Calcule le score d'une conjecture :
    - 0 si contre-exemple trouvé sur petits graphes
    - temps mis pour trouver contre-exemple (ou temps_max si résiste)
    """
    # 1. Vérification sur petits graphes (≤8 sommets)
    petits_graphes = charger_petits_graphes(8)

    for G in petits_graphes:
        if verifier_classe(G, conjecture['classe']):
            inv = calculer_invariants(G)
            Y_val = inv[conjecture['Y']]
            X_val = inv[conjecture['X']]
            try:
                fX = conjecture['f'](X_val)
                if Y_val > fX + 1e-9:
                    print(f"  Contre-exemple trouvé sur petits graphes !")
                    return 0.0
            except:
                pass

    # 2. Recherche locale
    print(f"  Lancement recherche locale (max {temps_max}s)...")
    temps_trouve, _ = recherche_contre_exemple(conjecture, temps_max)

    if temps_trouve is None:
        print(f"  Aucun contre-exemple trouvé en {temps_max}s")
        return temps_max
    else:
        print(f"  Contre-exemple trouvé en {temps_trouve:.2f}s")
        return temps_trouve

def explorer_conjectures(nb_conjectures=100):
    """
    Génère et évalue un grand nombre de conjectures
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

    # Trier par score
    results.sort(key=lambda x: x['score'], reverse=True)

    # Sauvegarder les meilleures
    top_conjectures = [c for c in results if c['score'] >= 20]
    with open('conjectures/top_conjectures.json', 'w') as f:
        json.dump(top_conjectures, f, indent=2, default=str)

    print("\n=== TOP 5 CONJECTURES ===")
    for i, conj in enumerate(results[:5]):
        print(f"{i+1}. {conj['texte']} -> {conj['score']:.1f}s")

    return results

if __name__ == "__main__":
    explorer_conjectures(nb_conjectures=100)
