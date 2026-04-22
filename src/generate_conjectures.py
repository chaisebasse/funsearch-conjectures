import random
import itertools
import math

# Classes de graphes (à vérifier)
CLASSES = [
    "connexe",  # toujours vérifié
    "biparti",
    "planaire",
    "sans_triangle",
    "sans_griffe"
]

# Invariants
INVARIANTS = [
    'n', 'm', 'deg_min', 'deg_max', 'deg_moyen',
    'diametre', 'rayon', 'densite', 'nb_triangles',
    'clique_max', 'independance_max', 'couplage_max',
    'domination_min'
]

# Fonctions possibles
FONCTIONS = [
    lambda x: x/4,
    lambda x: x/3,
    lambda x: x/2,
    lambda x: 2*x/3,
    lambda x: math.sqrt(x),
    lambda x: math.log2(x+1),
    lambda x: x - 3,
]

def generer_conjecture():
    """Génère une conjecture aléatoire du type: Y ≤ f(X)"""
    classe = random.choice(CLASSES)
    Y = random.choice(INVARIANTS)
    X = random.choice(INVARIANTS)

    # Éviter des trivialités
    while X == Y:
        X = random.choice(INVARIANTS)

    f = random.choice(FONCTIONS)

    return {
        'classe': classe,
        'Y': Y,
        'X': X,
        'f': f,
        'texte': f"Pour tout graphe {classe}, {Y} <= f({X})"
    }

def generer_beaucoup_conjectures(n=100):
    return [generer_conjecture() for _ in range(n)]

if __name__ == "__main__":
    for _ in range(5):
        c = generer_conjecture()
        print(c['texte'])
