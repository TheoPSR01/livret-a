"""livret_a : intérêts du Livret A et du LDDS (règle des quinzaines).

Les intérêts se calculent par quinzaine (du 1er au 15, du 16 à la fin du
mois), soit 24 par an : solde × taux / 24. Un dépôt rapporte à partir de la
quinzaine suivante (date de valeur le 16 ou le 1er du mois suivant) ; un
retrait cesse de rapporter dès le début de la quinzaine en cours. Les
intérêts sont ajoutés au capital le 31 décembre.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Iterable, Union

__version__ = "0.1.0"

Montant = Union[int, float, str, Decimal]
PLAFOND = Decimal(22950)

#: Taux du Livret A (identique pour le LDDS), en %, par date d'entrée en vigueur.
TAUX = (
    (date(2022, 2, 1), Decimal("1")),
    (date(2022, 8, 1), Decimal("2")),
    (date(2023, 2, 1), Decimal("3")),
    (date(2025, 2, 1), Decimal("2.4")),
    (date(2025, 8, 1), Decimal("1.7")),
    (date(2026, 2, 1), Decimal("1.5")),
    (date(2026, 8, 1), Decimal("1.7")),
)


def _d(x: Montant) -> Decimal:
    return x if isinstance(x, Decimal) else Decimal(str(x).replace(",", ".").replace(" ", ""))


def taux_au(jour: date) -> Decimal:
    """Taux annuel en vigueur à une date, en %."""
    if jour < TAUX[0][0]:
        raise ValueError(f"historique des taux disponible à partir du {TAUX[0][0]:%d/%m/%Y}")
    t = TAUX[0][1]
    for debut, valeur in TAUX:
        if jour >= debut:
            t = valeur
    return t


def date_de_valeur(jour: date, depot: bool) -> date:
    """Date à partir de laquelle l'opération compte pour les intérêts."""
    if depot:
        if jour.day <= 15:
            return date(jour.year, jour.month, 16)
        return date(jour.year + 1, 1, 1) if jour.month == 12 else date(jour.year, jour.month + 1, 1)
    return date(jour.year, jour.month, 1 if jour.day <= 15 else 16)


def quinzaines(annee: int) -> list:
    """Les 24 dates de début de quinzaine de l'année."""
    return [date(annee, m, j) for m in range(1, 13) for j in (1, 16)]


def interets(solde_initial: Montant, annee: int, operations: Iterable = ()) -> Decimal:
    """Intérêts d'une année, arrondis au centime.

    ``operations`` : couples (date, montant), montant positif pour un dépôt,
    négatif pour un retrait.
    """
    mouvements = []
    for jour, montant in operations:
        m = _d(montant)
        if jour.year != annee:
            raise ValueError(f"opération du {jour:%d/%m/%Y} hors de l'année {annee}")
        mouvements.append((date_de_valeur(jour, m > 0), m))
    total = Decimal(0)
    for debut in quinzaines(annee):
        solde = _d(solde_initial) + sum((m for v, m in mouvements if v <= debut), Decimal(0))
        if solde > 0:
            total += solde * taux_au(debut) / Decimal(100) / Decimal(24)
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def projection(solde: Montant, annees: int, taux: Montant) -> list:
    """Solde au 31 décembre de chaque année, sans mouvement, à taux constant (capitalisation annuelle)."""
    s, t, res = _d(solde), _d(taux) / 100, []
    for _ in range(annees):
        s = (s * (1 + t)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        res.append(s)
    return res


def _operation(v: str):
    try:
        jour, montant = v.split(":")
        return date.fromisoformat(jour), _d(montant)
    except (ValueError, InvalidOperation):
        raise argparse.ArgumentTypeError(f"opération invalide : {v!r} (AAAA-MM-JJ:montant)")


def _fr(x: Decimal) -> str:
    return f"{x:,.2f}".replace(",", " ").replace(".", ",")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="livret-a", description="Intérêts du Livret A ou du LDDS sur une année.")
    p.add_argument("--version", action="version", version=f"livret-a {__version__}")
    p.add_argument("solde", help="solde au 1er janvier")
    p.add_argument("--annee", type=int, default=date.today().year)
    p.add_argument("--depot", type=_operation, action="append", default=[], help="AAAA-MM-JJ:montant (répétable)")
    p.add_argument("--retrait", type=_operation, action="append", default=[], help="AAAA-MM-JJ:montant (répétable)")
    args = p.parse_args(argv)
    ops = list(args.depot) + [(j, -abs(m)) for j, m in args.retrait]
    try:
        i = interets(args.solde, args.annee, ops)
    except (ValueError, InvalidOperation) as exc:
        print(f"livret-a : {exc}", file=sys.stderr)
        return 2
    fin = _d(args.solde) + sum((m for _, m in ops), Decimal(0)) + i
    print(f"Intérêts {args.annee}  : {_fr(i)} €")
    print(f"Solde au 31/12 : {_fr(fin)} € (intérêts compris)")
    taux = sorted({str(taux_au(q)) for q in quinzaines(args.annee)}, key=Decimal)
    print("Taux appliqués : " + ", ".join(t.replace(".", ",") + " %" for t in taux))
    if _d(args.solde) + sum((m for _, m in args.depot), Decimal(0)) > PLAFOND:
        print(f"Attention : les versements dépassent le plafond de {_fr(PLAFOND)} €.")
    return 0


__all__ = ["PLAFOND", "TAUX", "date_de_valeur", "interets", "main", "projection", "quinzaines", "taux_au"]
