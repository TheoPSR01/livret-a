from datetime import date
from decimal import Decimal

import pytest

from livret_a import date_de_valeur, interets, main, projection, quinzaines, taux_au


def test_taux():
    assert taux_au(date(2026, 1, 15)) == Decimal("1.7")
    assert taux_au(date(2026, 2, 1)) == Decimal("1.5")
    assert taux_au(date(2026, 11, 20)) == Decimal("1.7")
    with pytest.raises(ValueError):
        taux_au(date(2020, 1, 1))


@pytest.mark.parametrize("jour,depot,attendu", [
    (date(2026, 3, 10), True, date(2026, 3, 16)),
    (date(2026, 3, 15), True, date(2026, 3, 16)),
    (date(2026, 3, 16), True, date(2026, 4, 1)),
    (date(2026, 12, 20), True, date(2027, 1, 1)),
    (date(2026, 3, 10), False, date(2026, 3, 1)),
    (date(2026, 9, 20), False, date(2026, 9, 16)),
])
def test_dates_de_valeur(jour, depot, attendu):
    assert date_de_valeur(jour, depot) == attendu


def test_24_quinzaines():
    assert len(quinzaines(2026)) == 24


def test_annee_2026_sans_mouvement():
    # 2 quinzaines à 1,7 %, 12 à 1,5 %, 10 à 1,7 %
    assert interets(10000, 2026) == Decimal("160.00")


def test_depot_en_cours_d_annee():
    # 1 000 € versés le 10 mars rapportent à partir du 16 mars
    assert interets(10000, 2026, [(date(2026, 3, 10), 1000)]) == Decimal("172.71")


def test_retrait():
    # 500 € retirés le 20 septembre ne rapportent plus dès le 16 septembre
    assert interets(10000, 2026, [(date(2026, 9, 20), -500)]) == Decimal("157.52")


def test_operation_hors_annee():
    with pytest.raises(ValueError):
        interets(1000, 2026, [(date(2025, 12, 1), 100)])


def test_projection():
    assert projection(1000, 2, "1,5") == [Decimal("1015.00"), Decimal("1030.23")]


def test_cli(capsys):
    assert main(["10000", "--annee", "2026", "--depot", "2026-03-10:1000"]) == 0
    out = capsys.readouterr().out
    assert "172,71 €" in out and "11 172,71 €" in out
    assert main(["22000", "--annee", "2026", "--depot", "2026-05-02:2000"]) == 0
    assert "plafond" in capsys.readouterr().out


def test_cli_aide():
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
