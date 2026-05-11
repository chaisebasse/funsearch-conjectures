import json
import os
import threading

class FileConjectures:
    """Gestion thread-safe de la file d'attente des conjectures"""

    def __init__(self, fichier_a_traiter="conjectures/a_traiter.json",
                 fichier_traitees="conjectures/traitees.json"):
        self.fichier_a_traiter = fichier_a_traiter
        self.fichier_traitees = fichier_traitees
        self.verrou = threading.Lock()

        # Créer les dossiers si besoin
        os.makedirs(os.path.dirname(fichier_a_traiter), exist_ok=True)

        # Initialiser les fichiers s'ils n'existent pas
        if not os.path.exists(fichier_a_traiter):
            with open(fichier_a_traiter, 'w') as f:
                json.dump([], f)
        if not os.path.exists(fichier_traitees):
            with open(fichier_traitees, 'w') as f:
                json.dump([], f)

    def ajouter_conjecture(self, conjecture):
        """Ajoute une conjecture à la file d'attente (producteur)"""
        with self.verrou:
            with open(self.fichier_a_traiter, 'r') as f:
                file = json.load(f)

            # Éviter les doublons
            if not any(c['texte'] == conjecture['texte'] for c in file):
                file.append(conjecture)

                with open(self.fichier_a_traiter, 'w') as f:
                    json.dump(file, f, indent=2, default=str)
                return True
        return False

    def recuperer_conjecture(self):
        """Récupère une conjecture à traiter (consommateur)"""
        with self.verrou:
            with open(self.fichier_a_traiter, 'r') as f:
                file = json.load(f)

            if not file:
                return None

            conjecture = file.pop(0)

            with open(self.fichier_a_traiter, 'w') as f:
                json.dump(file, f, indent=2, default=str)

            return conjecture

    def sauvegarder_traitee(self, conjecture):
        """Sauvegarde une conjecture traitée avec son avis"""
        with self.verrou:
            with open(self.fichier_traitees, 'r') as f:
                traitees = json.load(f)

            traitees.append(conjecture)

            with open(self.fichier_traitees, 'w') as f:
                json.dump(traitees, f, indent=2, default=str)

    def compter_a_traiter(self):
        """Retourne le nombre de conjectures en attente"""
        with open(self.fichier_a_traiter, 'r') as f:
            return len(json.load(f))

    def compter_traitees(self):
        """Retourne le nombre de conjectures déjà traitées"""
        with open(self.fichier_traitees, 'r') as f:
            return len(json.load(f))
