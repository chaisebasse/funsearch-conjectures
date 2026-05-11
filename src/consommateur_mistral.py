"""
Consommateur de conjectures - À lancer séparément
Récupère les conjectures de la file et les soumet à Mistral
"""

import os
import time
import json
import requests
from gestion_file import FileConjectures
import sys
sys.path.append('/home/chaise/.local/lib/python3.10/site-packages')
from mistralai.client import Mistral

# Configuration Mistral
API_KEY = os.environ.get("MISTRAL_API_KEY")
if not API_KEY:
    print("Clé API non trouvée")
    exit(1)

client = Mistral(api_key=API_KEY)

def interroger_mistral(conjecture_texte):
    """Interroge Mistral API et retourne (verdict, raisonnement) ou (None, None) en cas d'erreur"""
    prompt = f"""
    Voici une conjecture sur les graphes : {conjecture_texte}

    Réponds uniquement avec un objet JSON valide, sans balises markdown, de cette forme exacte :
    {{
      "raisonnement": "ton raisonnement **court**, maximum 10 lignes, étape par étape ici, mais pas de retours à la ligne",
      "verdict": "VRAI ou FAUX"
    }}

    Pour le raisonnement, considère :
    1. Est-ce que la conjecture est triviale (vraie ou fausse par définition) ?
    2. Y a-t-il un contre-exemple simple ?
    3. Existe-t-il un théorème connu qui confirme ou infirme cette conjecture ?
    """

    try:
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        raw = response.choices[0].message.content
        clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

        print(f"${clean}")
        parsed = json.loads(clean)
        verdict = parsed.get("verdict", "INCONNU").strip().upper()
        raisonnement = parsed.get("raisonnement", "")
        return verdict, raisonnement
    except Exception as e:
        print(f"Erreur: {str(e)}")
        return None, None


def consommateur(nb_max=None, pause=1):
    """
    Consomme les conjectures de la file et les soumet à Mistral

    Args:
        nb_max: Nombre max de conjectures à traiter (None = illimité)
        pause: Pause entre deux traitements (secondes)
    """
    file = FileConjectures()

    print("Consommateur Mistral démarré")
    print(f"Conjectures en attente: {file.compter_a_traiter()}")
    print(f"Conjectures déjà traitées: {file.compter_traitees()}")

    print("(Appuie sur Ctrl+C pour arrêter)\n")

    compteur = 0

    try:
        while nb_max is None or compteur < nb_max:
            # Récupérer une conjecture
            conj = file.recuperer_conjecture()

            if conj is None:
                print("Plus de conjectures dans la file. Attente...")
                time.sleep(5)
                continue

            # Traiter la conjecture
            print(f"\n[{compteur+1}] {conj['texte']}")
            print(f"Score: {conj.get('score_str', '?')}")

            # Interroger Mistral
            verdict, raisonnement = interroger_mistral(conj['texte'])

            if verdict is None:
                print("Réponse non parseable, conjecture ignorée")
                time.sleep(30)
            else:
                conj['avis_mistral'] = verdict
                conj['raisonnement_mistral'] = raisonnement

                # Sauvegarder
                file.sauvegarder_traitee(conj)
                print("Sauvegardée")

                compteur += 1

                # Pause pour respecter les limites de l'API
                time.sleep(pause)

    except KeyboardInterrupt:
        print("\n\nArrêt demandé par l'utilisateur")

    print(f"\nConsommateur terminé!")
    print(f"Conjectures traitées: {compteur}")
    print(f"Encore en attente: {file.compter_a_traiter()}")

if __name__ == "__main__":
    nb = int(sys.argv[1]) if len(sys.argv) > 1 else None
    consommateur(nb_max=100)
