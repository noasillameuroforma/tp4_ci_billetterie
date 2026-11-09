
import math


class Billetterie:

    def __init__(self, capacite):
        if type(capacite) is not int or capacite <= 0:
            raise ValueError("Capacité invalide")

        self.capacite = capacite
        self.places_disponibles = capacite
        self.reservations = 0
        self.chiffre_affaires = 0

    @staticmethod
    def _verifier_quantite(quantite):
        if type(quantite) is not int or quantite <= 0:
            raise ValueError("Quantité invalide")

    @staticmethod
    def _verifier_prix(prix):
        if (
            type(prix) not in (int, float)
            or not math.isfinite(prix)
            or prix <= 0
        ):
            raise ValueError("Prix invalide")

    def calculer_montant(self, quantite, prix, code_promo=None):
        self._verifier_quantite(quantite)
        self._verifier_prix(prix)

        if code_promo not in (None, "FESTIVAL"):
            raise ValueError("Code promotionnel inconnu")

        montant_initial = quantite * prix
        montant = montant_initial

        # Remise de 10 % dès quatre billets
        if quantite >= 4:
            montant *= 0.90

        # La condition dépend du montant initial
        if code_promo == "FESTIVAL" and montant_initial >= 80:
            montant -= 5

        # Empêcher les montants négatifs
        montant = max(0, montant)

        return round(montant, 2)

    def reserver(
        self,
        quantite,
        prix,
        service,
        code_promo=None
    ):
        self._verifier_quantite(quantite)
        self._verifier_prix(prix)

        if quantite > self.places_disponibles:
            raise ValueError("Places insuffisantes")

        montant = self.calculer_montant(
            quantite,
            prix,
            code_promo
        )

        # Vérifier la confirmation avant toute mutation
        confirmation = service.envoyer_confirmation(montant)

        if confirmation is not True:
            raise RuntimeError("Confirmation refusée")

        self.places_disponibles -= quantite
        self.reservations += quantite
        self.chiffre_affaires += montant

        return montant

    def annuler(self, quantite):
        self._verifier_quantite(quantite)

        if quantite > self.reservations:
            raise ValueError("Annulation impossible")

        self.places_disponibles += quantite
        self.reservations -= quantite

        # Pas de remboursement automatique dans ce TP
        return self.places_disponibles

    def places_restantes(self):
        return self.places_disponibles

    def taux_occupation(self):
        taux = self.reservations / self.capacite * 100
        return round(taux, 2)

    def places_reservees(self):
        return self.reservations

    def statistiques(self):
        return {
            "capacite": self.capacite,
            "disponibles": self.places_disponibles,
            "reservees": self.reservations,
            "occupation": self.taux_occupation(),
            "chiffre_affaires": self.chiffre_affaires
        }
