# livret-a

Calculer les intérêts d'un Livret A ou d'un LDDS sur une année, en tenant compte de la règle des quinzaines, des dépôts et retraits et des changements de taux. Aucune dépendance.

Pratique pour vérifier les intérêts versés par la banque en janvier, ou pour choisir la bonne date d'un versement.

## Installation

```bash
pip install git+https://github.com/TheoPSR01/livret-a.git
```

Python 3.10 ou plus récent.

## En ligne de commande

10 000 € au 1er janvier 2026, puis 1 000 € versés le 10 mars :

```bash
livret-a 10000 --annee 2026 --depot 2026-03-10:1000
```

```
Intérêts 2026  : 172,71 €
Solde au 31/12 : 11 172,71 € (intérêts compris)
Taux appliqués : 1,5 %, 1,7 %
```

```bash
livret-a 10000 --annee 2026 --retrait 2026-09-20:500
livret-a 5000 --depot 2026-04-02:200 --depot 2026-06-02:200 --depot 2026-09-02:200
```

## En Python

```python
from datetime import date
from livret_a import interets, date_de_valeur, projection

interets(10000, 2026)                                   # Decimal('160.00')
interets(10000, 2026, [(date(2026, 3, 10), 1000)])      # Decimal('172.71')
date_de_valeur(date(2026, 3, 16), depot=True)          # 2026-04-01 : un jour trop tard
projection(10000, 5, 1.7)                               # solde fin d'année sur 5 ans
```

## Règles appliquées

Les intérêts se calculent par quinzaine : du 1er au 15, puis du 16 à la fin du mois, soit 24 quinzaines par an. Pour chaque quinzaine, intérêts = solde × taux / 24.

Un dépôt rapporte à partir de la quinzaine suivante : versé entre le 1er et le 15, il compte à partir du 16 ; versé après le 15, à partir du 1er du mois suivant. Un retrait cesse de rapporter dès le début de la quinzaine où il a lieu. Les intérêts sont ajoutés au capital le 31 décembre.

Taux inclus (Livret A et LDDS) : 1 % en février 2022, 2 % en août 2022, 3 % en février 2023, 2,4 % en février 2025, 1,7 % en août 2025, 1,5 % en février 2026, 1,7 % depuis le 1er août 2026. Plafond de versements : 22 950 € (intérêts capitalisés non compris).

## Limites

Les taux évoluent en général le 1er février et le 1er août : pensez à mettre à jour `TAUX`. Certaines banques arrondissent par quinzaine plutôt qu'en fin d'année, d'où des écarts de quelques centimes. Le LEP, qui a son propre taux, n'est pas couvert.

## Contribuer

```bash
git clone https://github.com/TheoPSR01/livret-a.git
cd livret-a
pip install -e ".[dev]"
pytest
```

## Licence

MIT
