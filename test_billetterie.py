
import pytest
from unittest.mock import Mock
from billetterie import Billetterie


@pytest.fixture
def billetterie():
    return Billetterie(100)


@pytest.fixture
def service():
    svc = Mock()
    svc.envoyer_confirmation.return_value = True
    return svc


# Tests de départ

def test_reservation_simple(billetterie, service):
    montant = billetterie.reserver(2, 20, service)
    assert montant == 40
    assert billetterie.places_restantes() == 98


def test_places_initiales():
    assert Billetterie(50).places_restantes() == 50


def test_reservation_avec_reduction(billetterie, service):
    assert billetterie.reserver(5, 20, service) == 90


def test_annulation_simple(service):
    b = Billetterie(20)
    b.reserver(5, 10, service)
    b.annuler(2)
    assert b.places_restantes() == 17


# Validation des données

@pytest.mark.parametrize(
    "capacite",
    [0, -1, 1.5, True, "100", None]
)
def test_capacite_invalide(capacite):
    with pytest.raises(ValueError):
        Billetterie(capacite)


@pytest.mark.parametrize(
    "quantite",
    [0, -1, 2.5, True, "2", None]
)
def test_quantite_invalide(billetterie, service, quantite):
    with pytest.raises(ValueError):
        billetterie.reserver(quantite, 20, service)

    assert billetterie.places_restantes() == 100
    service.envoyer_confirmation.assert_not_called()


@pytest.mark.parametrize(
    "prix",
    [0, -5, True, "20", None, float("nan"), float("inf")]
)
def test_prix_invalide(billetterie, service, prix):
    with pytest.raises(ValueError):
        billetterie.reserver(1, prix, service)

    assert billetterie.places_restantes() == 100
    service.envoyer_confirmation.assert_not_called()


# Remises et promotions

@pytest.mark.parametrize(
    "quantite, prix, attendu",
    [
        (3, 20, 60),
        (4, 20, 72),
        (5, 20, 90)
    ]
)
def test_seuil_remise(billetterie, quantite, prix, attendu):
    assert billetterie.calculer_montant(
        quantite, prix
    ) == attendu


@pytest.mark.parametrize(
    "quantite, prix, attendu",
    [
        (1, 79, 79),
        (1, 80, 75),
        (4, 20, 67)
    ]
)
def test_promotion(billetterie, quantite, prix, attendu):
    assert billetterie.calculer_montant(
        quantite, prix, "FESTIVAL"
    ) == attendu


def test_code_inconnu(billetterie, service):
    with pytest.raises(ValueError):
        billetterie.reserver(
            1, 20, service, "INCONNU"
        )

    service.envoyer_confirmation.assert_not_called()


# Disponibilité et réservations

def test_reserver_dernieres_places(service):
    b = Billetterie(2)

    assert b.reserver(2, 20, service) == 40
    assert b.places_restantes() == 0


def test_stock_insuffisant(billetterie, service):
    with pytest.raises(ValueError):
        billetterie.reserver(101, 20, service)

    assert billetterie.statistiques() == {
        "capacite": 100,
        "disponibles": 100,
        "reservees": 0,
        "occupation": 0.0,
        "chiffre_affaires": 0
    }

    service.envoyer_confirmation.assert_not_called()


# Mocks et confirmation

def test_confirmation_unique(billetterie, service):
    billetterie.reserver(2, 20, service)

    service.envoyer_confirmation.assert_called_once_with(40)


def test_confirmation_refusee(billetterie, service):
    service.envoyer_confirmation.return_value = False
    avant = billetterie.statistiques()

    with pytest.raises(RuntimeError):
        billetterie.reserver(2, 20, service)

    assert billetterie.statistiques() == avant
    service.envoyer_confirmation.assert_called_once_with(40)


def test_confirmation_exception(billetterie, service):
    service.envoyer_confirmation.side_effect = ConnectionError(
        "Service indisponible"
    )
    avant = billetterie.statistiques()

    with pytest.raises(ConnectionError):
        billetterie.reserver(2, 20, service)

    assert billetterie.statistiques() == avant
    service.envoyer_confirmation.assert_called_once_with(40)


# Annulations

@pytest.mark.parametrize(
    "quantite",
    [0, -1, 1.5, True]
)
def test_annulation_invalide(billetterie, quantite):
    avant = billetterie.statistiques()

    with pytest.raises(ValueError):
        billetterie.annuler(quantite)

    assert billetterie.statistiques() == avant


def test_annulation_excessive(billetterie, service):
    billetterie.reserver(2, 20, service)
    avant = billetterie.statistiques()

    with pytest.raises(ValueError):
        billetterie.annuler(3)

    assert billetterie.statistiques() == avant


# Statistiques

def test_statistiques_et_invariant(service):
    b = Billetterie(3)

    b.reserver(1, 10, service)

    stats = b.statistiques()

    assert stats["disponibles"] + stats["reservees"] == 3
    assert stats["occupation"] == 33.33
    assert stats["chiffre_affaires"] == 10

    b.annuler(1)

    assert b.statistiques()["chiffre_affaires"] == 10
    assert b.statistiques()["occupation"] == 0




def test_reservation_dernieres_places():
    billetterie = Billetterie(10)
    service = Mock()
    service.envoyer_confirmation.return_value = True

    montant = billetterie.reserver(
        10, 20, service
    )

    assert montant == 180
    assert billetterie.places_restantes() == 0
    assert billetterie.places_reservees() == 10

    service.envoyer_confirmation.assert_called_once_with(180)
