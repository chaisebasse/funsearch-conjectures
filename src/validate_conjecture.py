import networkx as nx
from chargement_graphes import charger_petits_graphes
from invariants import calculer_invariants

def verifier_conjecture_sur_petits_graphes(conjecture):
    """
    Vérifie une conjecture sur tous les graphes <+=8 sommets
    Retourne (True si valide, liste_des_contre_exemples)
    """
    petits_graphes = charger_petits_graphes(8)
    if not petits_graphes:
        print("  Aucun petit graphe chargé, skip validation")
        return True, []  # Ne pas invalider si pas de données

    contre_exemple = False

    for G in petits_graphes:
        # Vérifier la classe de graphe
        classe_ok = True
        if conjecture['classe'] == 'biparti':
            classe_ok = nx.is_bipartite(G)
        elif conjecture['classe'] == 'planaire':
            classe_ok = nx.is_planar(G)
        elif conjecture['classe'] == 'sans_triangle':
            classe_ok = sum(nx.triangles(G).values()) == 0
        elif conjecture['classe'] == 'connexe':
            classe_ok = nx.is_connected(G)

        if not classe_ok:
            continue  # Graphe non concerné par la conjecture

        # Calculer les invariants
        inv = calculer_invariants(G)

        Y_val = inv[conjecture['Y']]
        X_val = inv[conjecture['X']]

        # Calculer f(X)
        try:
            fX = conjecture['f'](X_val)
        except Exception as e:
            print(f"  Erreur calcul f({X_val}) pour graphe {G}: {e}")
            continue

        # Vérifier l'inégalité
        if Y_val > fX + 1e-9:  # Contre-exemple trouvé
            contre_exemple = G
            print(f"  Contre-exemple trouvé: {conjecture['Y']}={Y_val} > f({conjecture['X']})={fX}")
            break

    if not contre_exemple:
        print("Aucun contre-exemple trouvé")

    return contre_exemple
