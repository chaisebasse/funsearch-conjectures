import random
import math

# Classes de graphes
CLASSES = [
    "connexe",
    "biparti",
    "planaire",
    "sans_triangle",
    "sans_griffe"
]

# Invariants — liste complète selon le cahier des charges
INVARIANTS = [
    'n', 'm', 'deg_min', 'deg_max', 'deg_moyen',
    'diametre', 'rayon', 'densite', 'nb_triangles',
    'clique_max', 'independance_max', 'couplage_max',
    'domination_min', 'couverture_min',
]

# Fonctions f(X) : linéaires et plus complexes
# Chaque entrée est (fonction, description lisible)
FONCTIONS = [
    # Linéaires simples
    (lambda x: x / 4,            "X/4"),
    (lambda x: x / 3,            "X/3"),
    (lambda x: x / 2,            "X/2"),
    (lambda x: 2 * x / 3,        "2X/3"),
    (lambda x: 3 * x / 4,        "3X/4"),
    (lambda x: x - 1,            "X-1"),
    (lambda x: x - 2,            "X-2"),
    (lambda x: x + 1,            "X+1"),
    # Non-linéaires
    (lambda x: math.sqrt(x),           "sqrt(X)"),
    (lambda x: math.log2(x + 1),       "log2(X+1)"),
    (lambda x: math.sqrt(x) / 2,       "sqrt(X)/2"),
    (lambda x: x ** (2 / 3),           "X^(2/3)"),
    (lambda x: math.floor(x / 2) + 1,  "floor(X/2)+1"),
    (lambda x: math.ceil(x / 2),       "ceil(X/2)"),
    (lambda x: math.floor(math.sqrt(x)) + 1, "floor(sqrt(X))+1"),
]

def generer_conjecture():
    """Génère une conjecture aléatoire du type: Y ≤ f(X)"""
    classe = random.choice(CLASSES)
    Y = random.choice(INVARIANTS)
    X = random.choice([inv for inv in INVARIANTS if inv != Y])
    f, f_str = random.choice(FONCTIONS)

    texte = f"Pour tout graphe {classe}, {Y} <= {f_str}({X})"

    return {
        'classe': classe,
        'Y': Y,
        'X': X,
        'f': f,
        'f_str': f_str,
        'texte': texte,
    }

def generer_beaucoup_conjectures(n=100):
    return [generer_conjecture() for _ in range(n)]
