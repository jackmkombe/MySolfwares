# Logiciel de Tri et Fusion Intelligente de Fichiers

## Vue d'ensemble

Application desktop Windows 11 pour le tri et la fusion intelligente de fichiers et dossiers basée sur l'analyse sémantique avancée.

## Architecture

### Principes

- **Clean Architecture** : Séparation stricte entre couches
- **Python 3.11+** avec PySide6
- **Algorithmes sémantiques** : Pas de comparaisons naïves de chaînes
- **Traçabilité** : Toute décision est loggée et justifiable
- **Extensibilité** : Points d'extension clairement définis

### Structure des couches

```
src/
├── domain/              # Couche métier (entités, interfaces)
├── application/         # Cas d'usage et orchestration
├── infrastructure/      # Implémentations concrètes
│   ├── filesystem/      # Accès système de fichiers
│   ├── algorithms/      # Algorithmes de similarité
│   └── persistence/     # Stockage des configurations
└── presentation/        # Interface utilisateur PySide6
```

## Capacités algorithmiques

### Normalisation

- Suppression des tags (`[1080p]`, `(2001)`, etc.)
- Unification des séparateurs (`-`, `_`, ` `)
- Normalisation Unicode et casse

### Analyse sémantique

- Extraction de structure : titre, saison, épisode, année, qualité
- Détection de variantes orthographiques (juu-shiro ≈ juushiro)
- Reconnaissance de contexte (naruto ≠ naruto shippuden)

### Regroupement hiérarchique

- Score de similarité pondéré multi-critères
- Seuils configurables par type de contenu
- Validation utilisateur pour cas ambigus

## Installation

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Lancement

```bash
python -m src.main
```

## Tests

```bash
pytest tests/ -v --cov=src
```
