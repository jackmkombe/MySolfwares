# Guide de Démarrage Rapide

## Installation

### 1. Prérequis

- Python 3.11 ou supérieur
- Windows 11
- Git (optionnel)

### 2. Installation des dépendances

```bash
# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel (Windows)
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration (optionnel)

Copiez `.env.example` vers `.env` et modifiez les valeurs si nécessaire :

```bash
copy .env.example .env
```

## Lancement de l'application

```bash
python -m src.main
```

## Utilisation

### Interface utilisateur

1. **Sélectionner un répertoire** : Cliquez sur "Parcourir" ou entrez le chemin manuellement
2. **Options** : Cochez "Récursif" pour scanner les sous-dossiers
3. **Analyser** : Cliquez sur "Analyser" pour lancer l'analyse
4. **Réviser les décisions** : Consultez les regroupements proposés dans la table
5. **Valider** : Cochez les décisions à exécuter (ou "Valider tout")
6. **Exécuter** : Cliquez sur "Exécuter" pour appliquer les regroupements

### Comprendre les résultats

#### Scores de confiance

- **✓ Auto (≥85%)** : Haute confiance, validation automatique
- **⚠ Validation requise (50-85%)** : Score ambigu, révision recommandée
- **Faible (<50%)** : Non proposé pour regroupement

#### Détails des décisions

Sélectionnez une décision dans la table pour voir :

- Justifications détaillées
- Liste des fichiers concernés
- Métriques de similarité

## Tests

### Lancer tous les tests

```bash
pytest tests/ -v
```

### Lancer avec couverture

```bash
pytest tests/ -v --cov=src --cov-report=html
```

### Lancer des tests spécifiques

```bash
# Tests de similarité
pytest tests/test_similarity.py -v

# Tests d'extraction sémantique
pytest tests/test_semantic_extractor.py -v
```

## Exemples de cas d'usage

### Cas 1 : Organiser une série avec saisons

**Structure initiale :**

```
Downloads/
  Naruto S01E01 [1080p].mkv
  Naruto S01E02 [720p].mkv
  Naruto S02E01.mkv
  Naruto S02E02.mkv
```

**Résultat proposé :**

```
Downloads/
  Naruto/
    Season 01/
      Naruto S01E01 [1080p].mkv
      Naruto S01E02 [720p].mkv
    Season 02/
      Naruto S02E01.mkv
      Naruto S02E02.mkv
```

### Cas 2 : Détecter les doublons

**Structure initiale :**

```
Downloads/
  movie-1080p.mkv
  movie.1080p.BluRay.mkv
  movie [1080p].mkv
```

**Résultat :** Les trois fichiers seront détectés comme similaires (possibles doublons)

### Cas 3 : Gérer les variantes orthographiques

**Structure initiale :**

```
Downloads/
  juu-shiro episode 1.mkv
  juushiro episode 2.mkv
  juu shiro episode 3.mkv
```

**Résultat :** Tous regroupés sous "Juu Shiro"

## Configuration avancée

### Ajuster les poids de similarité

Éditez `.env` :

```env
# Augmenter l'importance du titre
ALGO_TITLE_WEIGHT=0.6
ALGO_STRUCTURAL_WEIGHT=0.25
ALGO_TEMPORAL_WEIGHT=0.1
ALGO_QUALITY_WEIGHT=0.05
```

### Ajuster les seuils

```env
# Plus strict (moins de faux positifs)
ALGO_HIGH_CONFIDENCE_THRESHOLD=0.90
ALGO_AMBIGUOUS_MIN_THRESHOLD=0.60

# Plus permissif (plus de regroupements)
ALGO_HIGH_CONFIDENCE_THRESHOLD=0.80
ALGO_AMBIGUOUS_MIN_THRESHOLD=0.40
```

## Architecture

Consultez [ARCHITECTURE.md](ARCHITECTURE.md) pour une documentation complète de l'architecture.

### Structure du projet

```
src/
├── domain/              # Logique métier pure
│   ├── entities.py      # Entités (SemanticStructure, FileItem, etc.)
│   └── interfaces.py    # Interfaces (ports)
├── application/         # Cas d'usage
│   └── use_cases.py     # FileOrganizationUseCase
├── infrastructure/      # Implémentations
│   ├── algorithms/      # Algorithmes de similarité
│   │   ├── normalization.py
│   │   ├── semantic_extractor.py
│   │   ├── similarity.py
│   │   └── grouping.py
│   └── filesystem/      # Accès système de fichiers
│       └── repository.py
└── presentation/        # Interface utilisateur
    ├── main_window.py   # UI PySide6
    └── controller.py    # Contrôleur
```

## Dépannage

### Erreur : Module not found

Assurez-vous que l'environnement virtuel est activé :

```bash
venv\Scripts\activate
```

### Erreur : Permission denied

Exécutez l'application avec les droits administrateur ou sélectionnez un répertoire accessible.

### L'analyse est lente

Pour de gros répertoires :

- Désactivez le scan récursif si non nécessaire
- Excluez les dossiers système (déjà fait par défaut)

### Aucun regroupement proposé

Vérifiez que :

- Les fichiers ont des noms structurés
- Les seuils ne sont pas trop stricts
- Il y a au moins 2 fichiers similaires

## Points d'extension

### Ajouter un nouvel algorithme de similarité

1. Créer une classe implémentant `ISimilarityCalculator`
2. Implémenter `calculate()` et `calculate_matrix()`
3. Injecter dans `src/main.py`

### Ajouter une nouvelle source de métadonnées

1. Créer une classe implémentant `ISemanticExtractor`
2. Implémenter `extract()` et `extract_batch()`
3. Combiner avec l'extracteur existant

### Personnaliser la stratégie de regroupement

1. Créer une classe implémentant `IGroupingStrategy`
2. Implémenter `group()`
3. Injecter dans `src/main.py`

## Support

Pour toute question ou problème :

1. Consultez [ARCHITECTURE.md](ARCHITECTURE.md)
2. Vérifiez les tests pour des exemples d'utilisation
3. Examinez les logs pour le diagnostic

## Licence

Ce projet est un logiciel professionnel développé selon les principes de Clean Architecture.
