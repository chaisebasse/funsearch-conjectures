import networkx as nx
from chargement_graphes import charger_petits_graphes
from invariants import calculer_invariants

def verifier_classe(G, classe):
    """Vérifie si G appartient à la classe donnée."""
    if classe == 'connexe':
        return nx.is_connected(G)
    elif classe == 'biparti':
        return nx.is_bipartite(G)
    elif classe == 'planaire':
        return nx.is_planar(G)
    elif classe == 'sans_triangle':
        return sum(nx.triangles(G).values()) == 0
    elif classe == 'sans_griffe':
        return est_sans_griffe(G)
    return nx.is_connected(G)

def est_sans_griffe(G):
    """
    Un graphe est sans griffe si aucun sommet n'a
    3 voisins deux-à-deux non adjacents (i.e. pas de K_{1,3} induit).
    """
    for v in G.nodes():
        voisins = list(G.neighbors(v))
        if len(voisins) < 3:
            continue
        # Chercher 3 voisins formant un ensemble indépendant
        for i in range(len(voisins)):
            for j in range(i + 1, len(voisins)):
                if G.has_edge(voisins[i], voisins[j]):
                    continue  # Cette paire est adjacente, pas indépendante
                for k in range(j + 1, len(voisins)):
                    if (not G.has_edge(voisins[i], voisins[k]) and
                            not G.has_edge(voisins[j], voisins[k])):
                        # Trouvé K_{1,3} : griffe détectée
                        return False
    return True

def verifier_conjecture_sur_petits_graphes(conjecture):
    """
    Vérifie une conjecture sur tous les graphes connexes à <=8 sommets.

    Retourne:
        (valide: bool, contre_exemple: Graph ou None)
        - valide=True  → aucun contre-exemple trouvé
        - valide=False → contre_exemple est le graphe qui viole la conjecture
    """
    petits_graphes = charger_petits_graphes(8)
    if not petits_graphes:
        print("  Aucun petit graphe chargé, skip validation")
        return True, None

    for G in petits_graphes:
        if not verifier_classe(G, conjecture['classe']):
            continue  # Graphe hors de la classe, non concerné

        inv = calculer_invariants(G)
        Y_val = inv[conjecture['Y']]
        X_val = inv[conjecture['X']]

        try:
            fX = conjecture['f'](X_val)
        except Exception as e:
            print(f"  Erreur calcul f({X_val}): {e}")
            continue

        # Contre-exemple : Y > f(X)
        if Y_val > fX + 1e-9:
            print(f"  Contre-exemple trouvé : {conjecture['Y']}={Y_val:.4f} > "
                  f"f({conjecture['X']})={fX:.4f}")
            return False, G

    print("  Aucun contre-exemple trouvé sur les petits graphes")
    return True, None
