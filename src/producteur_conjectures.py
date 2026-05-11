"""
Producteur de conjectures - À lancer en arrière-plan
Génère des conjectures et les ajoute à la file d'attente
"""

import time
from generate_conjectures import generer_conjecture
from recherche_locale import calculer_score_conjecture
from gestion_file import FileConjectures

def producteur(nb_conjectures=100, temps_max=60, pause=2):
    """
    Génère des conjectures et les ajoute à la file d'attente

    Args:
        nb_conjectures: Nombre total de conjectures à générer
        temps_max: Temps max pour la recherche locale
        pause: Pause entre deux générations (secondes)
    """
    file = FileConjectures()

    print(f"Producteur démarré - Objectif: {nb_conjectures} conjectures")
    print(f"   Conjectures déjà dans la file: {file.compter_a_traiter()}")
    print(f"   Conjectures déjà traitées: {file.compter_traitees()}")

    for i in range(nb_conjectures):
        # 1. Générer une conjecture aléatoire
        conj = generer_conjecture()
        print(f"\n[{i+1}/{nb_conjectures}] Génération: {conj['texte']}")

        # 2. Calculer son score (optionnel - peut être long)
        #    Si tu veux accélérer, tu peux sauter cette étape et
        #    ne calculer le score que pour les conjectures prometteuses
        try:
            score = calculer_score_conjecture(conj, temps_max=temps_max)
            conj['score'] = score
            conj['score_str'] = f"{score:.1f}s"
            print(f"   Score: {score:.1f}s")
        except Exception as e:
            print(f"   Erreur calcul score: {e}")
            continue

        file.ajouter_conjecture(conj)
        print(f"Ajoutée à la file (score={score:.1f}s)")

        # Pause pour éviter de surcharger
        time.sleep(pause)

    print(f"\nProducteur terminé!")
    print(f"   Conjectures en attente: {file.compter_a_traiter()}")
    print(f"   Conjectures traitées: {file.compter_traitees()}")

if __name__ == "__main__":
    import sys
    nb = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    producteur(nb_conjectures=nb)
