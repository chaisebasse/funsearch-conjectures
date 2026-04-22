import json
import os
import sys
import sys
sys.path.append('/home/chaise/.local/lib/python3.10/site-packages')
from mistralai.client import Mistral

# Lit les conjectures résistantes
with open('conjectures/top_conjectures.json', 'r') as f:
    conjectures = json.load(f)

API_KEY = os.environ.get("MISTRAL_API_KEY")
if not API_KEY:
    print("Clé API non trouvée. Configure MISTRAL_API_KEY")
    print("   export MISTRAL_API_KEY='ta_clé_ici'")
    exit(1)

client = Mistral(api_key=API_KEY)

resultats = []  # Pour sauvegarder les avis

for i, conj in enumerate(conjectures):
    print(f"\n[{i+1}/{len(conjectures)}] {conj['texte']}")
    print(f"   Score: {conj['score']}s")

    prompt = f"""
    Est-ce que cette conjecture mathématique est vraie, fausse, ou connue ?
    Conjecture : {conj['texte']}
    Score de résistance : {conj['score']} secondes

    Réponds en un mot.
    """

    try:
        response = client.chat.complete(
            model="mistral-large-latest",  # small suffit, moins cher
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        avis = response.choices[0].message.content

        # Sauvegarde
        conj['avis_mistral'] = avis
        resultats.append(conj)

        print(f"   📝 Avis: {avis}")

        # Sauvegarde progressive
        with open('conjectures/avis_mistral.json', 'w') as f:
            json.dump(resultats, f, indent=2, default=str)

        # Petit délai pour éviter de surcharger l'API
        import time
        time.sleep(2)

    except Exception as e:
        print(f"Erreur: {e}")
        conj['avis_mistral'] = f"Erreur: {e}"
        resultats.append(conj)

print("\n" + "="*60)
print(f"✅ Terminé ! {len(resultats)} conjectures analysées")
print(f"Résultats sauvegardés dans conjectures/avis_mistral.json")
