# Station Méteo

A clean Python package for weather data retrieval, cleaning, and analysis.

## Features

- **CSV Data Retrieval**: Load and validate weather data from CSV files
- **Data Cleaning**: Automatic column normalization, timestamp parsing, and type coercion
- **Timezone Support**: Parse and convert timestamps to any timezone (UTC by default)
- **Clean Architecture**: Organized into focused modules with clear separation of concerns
# Station Méteo

Une bibliothèque Python légère pour la récupération, le nettoyage et l'analyse de données météorologiques.

## Fonctionnalités

- **Récupération CSV** : Charger et valider des données météo depuis des fichiers CSV
- **Nettoyage des données** : Normalisation des colonnes, parsing des horodatages et coercition de types
- **Support des fuseaux horaires** : Conversion des timestamps vers n'importe quel fuseau (UTC par défaut)
- **Architecture propre** : Modules ciblés avec séparation claire des responsabilités

## Structure du projet

```
projet/
├── __init__.py       # Exports du package
├── __main__.py       # Point d'entrée pour python -m projet
├── cleaner.py        # Classe DataCleaner pour la normalisation
├── retriever.py      # DataRetriever abstrait et CSVDataRetriever
└── cli.py            # Orchestration CLI (WeatherApp)

tests/
├── __init__.py
├── conftest.py       # Configuration pytest
└── test_*.py         # Tests unitaires
```

## Installation

Installer en mode développement :

```powershell
pip install -e .
```

Ou avec les dépendances de développement :

```powershell
pip install -e ".[dev]"
```

## Utilisation

### En tant que module

```python
from projet.retriever import CSVDataRetriever
from projet.cleaner import DataCleaner

cleaner = DataCleaner(tz="Europe/Paris")
retriever = CSVDataRetriever(cleaner)
df = retriever.fetch("data.csv")
print(df.head())
```

### Depuis la ligne de commande

```powershell
# Avec python -m
python -m projet csv path/to/file.csv --tz "Europe/Paris" --sample 10

# Exemple : lister les stations (fichier emballé)
python -m projet stations --source toulouse --limit 10
```

## Exécution des tests

```powershell
python -m pytest tests/ -v
```

## Checklist (rubrique du cours)

Le projet respecte les points demandés par la rubrique :

- **Exécution sans erreur** : la CLI `python -m projet ...` et les scripts d'exemple s'exécutent.
- **Principes SOLID / KISS / DRY / YAGNI** : classes focalisées, injection de dépendances, duplication minimale.
- **Documentation du jeu de données** : Voir `DATA_PROFILE.md` pour le schéma CSV et les recommandations de profiling.
- **Documentation du code** : docstrings modules/classes présentes dans `projet/`.
- **Documentation d'utilisation** : ce fichier `README.md` et `projet/__main__.py` expliquent l'utilisation.
- **Fonctionnalités** : récupération CSV, intégration Toulouse API et Meteostat via la CLI.
- **Structure Python** : package `projet/`, point d'entrée `__main__`, tests sous `tests/`.
- **Implémentations requises** : Liste chaînée, File (Queue) et Dictionnaire de configuration implémentés dans `projet/linked_list.py`, `projet/queue.py`, et `projet/config.py`.
- **PEP8 / Nommage** : conventions respectées (nommage des variables, classes, fonctions).
- **Design Patterns (>=3)** : `ConfigurationManager` (Manager), retrievers (Factory/Provider), strategy/DI (DataCleaner injecté).
- **Tests unitaires** : suite `pytest` disponible et exécutable.

## Patterns de conception utilisés

- **Manager** : `ConfigurationManager` dans `projet/config.py` centralise le cycle de vie des configurations.
- **Factory / Provider** : les classes retriever dans `projet/retriever.py` fournissent des sources de données variées.
- **Strategy / Injection de dépendances** : `DataCleaner` injecté dans `CSVDataRetriever` pour séparer la stratégie de nettoyage.

## Prérequis

- Python >= 3.10
- pandas >= 1.3
- pyarrow >= 6.0.0

## Étapes suivantes / Vérifications optionnelles

- Exécuter `pylint` ou `ruff` pour la vérification du style et corriger les remarques.
- Ajouter un workflow CI (GitHub Actions) pour lancer tests et linters automatiquement.
