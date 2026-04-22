import networkx as nx
import time
from generate_conjectures import generer_beaucoup_conjectures
from validate_conjecture import verifier_conjecture_sur_petits_graphes

conjectures = generer_beaucoup_conjectures(50);
for i in conjectures:
    print(f"conjecture : {i}")
    contre_exemple = verifier_conjecture_sur_petits_graphes(i);
    print(" ")
