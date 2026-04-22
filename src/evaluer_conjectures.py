from generate_conjectures import generer_beaucoup_conjectures
from validate_conjecture import verifier_conjecture_sur_petits_graphes

# Générer 100 conjectures
conjectures = generer_beaucoup_conjectures(100)

bonnes_conjectures = []

for conj in conjectures:
    contre_exemple = verifier_conjecture_sur_petits_graphes(conj)
    if not contre_exemple:
        bonnes_conjectures.append(conj)
        print(f"✅ {conj['texte']}")

print(f"\n\n{len(bonnes_conjectures)} conjectures résistent aux petits graphes")

# Sauvegarder les bonnes
import json
with open('/conjectures/bonnes_conjectures.json', 'w') as f:
    json.dump(bonnes_conjectures, f, indent=2, default=str)
