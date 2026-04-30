# Architecture du Logiciel de Tri et Fusion Intelligente

## Vue d'ensemble

Ce document décrit l'architecture complète du logiciel de tri et fusion intelligente de fichiers et dossiers.

## Principes architecturaux

### Clean Architecture

L'application suit strictement les principes de Clean Architecture :

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                    │
│  (PySide6 UI, Controllers, Adapters)                    │
│  - Aucune logique métier                                │
│  - Dépend de Application et Domain                      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   Application Layer                      │
│  (Use Cases, Orchestration)                             │
│  - Coordonne la logique métier                          │
│  - Dépend uniquement de Domain                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                     Domain Layer                         │
│  (Entities, Interfaces)                                 │
│  - Logique métier pure                                  │
│  - Aucune dépendance externe                            │
└─────────────────────────────────────────────────────────┘
                          ↑
┌─────────────────────────────────────────────────────────┐
│                 Infrastructure Layer                     │
│  (Algorithms, Filesystem, Persistence)                  │
│  - Implémentations concrètes                            │
│  - Dépend de Domain (interfaces)                        │
└─────────────────────────────────────────────────────────┘
```

### Séparation des responsabilités

1. **Domain** : Entités métier et interfaces (ports)
2. **Application** : Cas d'usage et orchestration
3. **Infrastructure** : Implémentations concrètes (algorithmes, filesystem)
4. **Presentation** : Interface utilisateur (UI, controllers)

## Couche Domain

### Entités principales

#### SemanticStructure

Structure sémantique extraite d'un nom de fichier :

- `title` : Titre normalisé
- `content_type` : Type de contenu (série, film, etc.)
- `season` : Information de saison (optionnel)
- `episode` : Information d'épisode (optionnel)
- `year` : Année (optionnel)
- `quality` : Informations de qualité (optionnel)
- `extraction_confidence` : Score de confiance (0.0 à 1.0)

#### FileItem

Représente un fichier ou dossier :

- `path` : Chemin absolu
- `name` : Nom du fichier
- `file_type` : Type de fichier
- `semantic` : Structure sémantique extraite
- Métadonnées système (dates, taille)

#### SimilarityScore

Score de similarité entre deux structures :

- `total` : Score global (0.0 à 1.0)
- Scores détaillés par composant (titre, structure, temporel, qualité)
- `reasoning` : Justifications traçables
- `weights` : Poids utilisés

#### GroupingDecision

Décision de regroupement :

- `items` : Fichiers à regrouper
- `group_name` : Nom du groupe proposé
- `confidence` : Score de confiance
- `requires_validation` : Nécessite validation utilisateur
- `reasoning` : Justifications

### Interfaces (Ports)

- `IFileSystemRepository` : Accès au système de fichiers
- `ISemanticExtractor` : Extraction de structure sémantique
- `ISimilarityCalculator` : Calcul de similarité
- `IGroupingStrategy` : Stratégie de regroupement
- `INormalizationService` : Normalisation de texte
- `IValidationService` : Validation utilisateur

## Couche Infrastructure

### Algorithmes

#### AdvancedNormalizationService

Normalisation avancée des noms :

- Suppression du bruit (tags, qualité, groupes de release)
- Normalisation Unicode
- Normalisation des séparateurs
- Génération de variantes orthographiques

**Capacités** :

- `juu-shiro`, `juushiro`, `juu shiro` → même entité
- Suppression intelligente de `[1080p]`, `(VOSTFR)`, etc.

#### SemanticExtractorService

Extraction de structure sémantique :

- Détection de saisons/épisodes (S01E01, Season 1, etc.)
- Extraction d'année
- Détection de qualité (résolution, codec, source)
- Détection de type de contenu
- Calcul de confiance

**Patterns reconnus** :

- Saisons : `S01`, `Season 1`, `1st season`
- Épisodes : `E01`, `Episode 1`, ` - 01`
- Années : `(2001)`, `2001`
- Qualité : `1080p`, `BluRay`, `x264`, etc.

#### AdvancedSimilarityCalculator

Calcul de similarité sémantique :

- **Titre** : Jaro-Winkler + Token Set Ratio + Partial Ratio
- **Structure** : Logique métier pour saisons/épisodes
- **Temporel** : Comparaison d'années
- **Qualité** : Comparaison de résolution/codec/source

**Pondération configurable** :

- Titre : 50%
- Structure : 30%
- Temporel : 10%
- Qualité : 10%

**Logique de décision** :

- Même saison, même épisode → 1.0 (doublon)
- Même saison, épisodes différents → 0.7 (même série)
- Saisons différentes → 0.5 (même série, groupes différents)

#### HierarchicalGroupingStrategy

Regroupement hiérarchique :

- Clustering par seuil de similarité
- Détection de hiérarchie (série → saisons → épisodes)
- Génération de décisions avec justifications
- Flagging des cas ambigus

**Structure générée** :

```
Naruto/
  Season 01/
    Episode 01.mkv
    Episode 02.mkv
  Season 02/
    Episode 01.mkv
```

### Filesystem

#### WindowsFileSystemRepository

Accès au système de fichiers Windows :

- Scan récursif de répertoires
- Détection de type de fichier
- Gestion des fichiers cachés
- Déplacement de fichiers
- Création de répertoires

## Couche Application

### FileOrganizationUseCase

Cas d'usage principal orchestrant le workflow complet :

**Workflow** :

1. Scanner le répertoire
2. Extraire la structure sémantique
3. Calculer les similarités
4. Générer les décisions de regroupement
5. Valider avec l'utilisateur si nécessaire
6. Exécuter les regroupements validés

**Traçabilité** :

- Logging structuré de chaque étape
- Justifications pour chaque décision
- Métriques de confiance

## Couche Presentation

### MainWindow (PySide6)

Interface utilisateur moderne :

- Sélection de répertoire
- Table des décisions avec validation
- Détails des décisions
- Barre de progression
- Exécution des regroupements

### MainController

Contrôleur orchestrant UI et logique métier :

- Worker thread pour analyse asynchrone
- Gestion des signaux Qt
- Séparation stricte UI/métier

## Points d'extension futurs

### 1. Algorithmes de similarité

- **Extension facile** : Implémenter `ISimilarityCalculator`
- Possibilités :
  - Utilisation de modèles NLP (BERT, etc.)
  - Similarité basée sur métadonnées (durée, taille)
  - Apprentissage des préférences utilisateur

### 2. Stratégies de regroupement

- **Extension facile** : Implémenter `IGroupingStrategy`
- Possibilités :
  - Regroupement par genre
  - Regroupement par acteur/réalisateur
  - Regroupement chronologique

### 3. Sources de métadonnées

- **Extension facile** : Créer de nouveaux extracteurs
- Possibilités :
  - APIs externes (TMDB, TVDB, etc.)
  - Lecture de métadonnées embarquées (MKV, MP4)
  - OCR pour sous-titres

### 4. Validation utilisateur

- **Extension facile** : Implémenter `IValidationService`
- Possibilités :
  - Validation par IA
  - Apprentissage des décisions passées
  - Règles personnalisées

### 5. Exécution

- **Extension facile** : Modifier `FileOrganizationUseCase`
- Possibilités :
  - Mode simulation (dry-run)
  - Création de liens symboliques
  - Synchronisation cloud
  - Historique avec undo

## Garanties de qualité

### Testabilité

- Injection de dépendances
- Interfaces mockables
- Tests unitaires complets
- Pas de dépendances cachées

### Traçabilité

- Logging structuré (structlog)
- Justifications pour chaque décision
- Métriques de confiance
- Historique des actions

### Extensibilité

- Interfaces clairement définies
- Séparation des responsabilités
- Pas de couplage fort
- Configuration externalisée

### Maintenabilité

- Code documenté
- Architecture claire
- Patterns cohérents
- Pas de logique métier dans l'UI

## Configuration

### Seuils de similarité

- **Haute confiance** : ≥ 0.85 (validation automatique)
- **Ambigu** : 0.50 - 0.85 (validation utilisateur requise)
- **Faible** : < 0.50 (regroupement non recommandé)

### Poids de similarité

- Titre : 50%
- Structure (saison/épisode) : 30%
- Temporel (année) : 10%
- Qualité : 10%

Ces valeurs sont configurables via l'injection de dépendances.

## Exemples de cas d'usage

### Cas 1 : Variantes orthographiques

**Input** :

- `juu-shiro.mkv`
- `juushiro.mkv`
- `juu shiro.mkv`

**Résultat** :

- Regroupés ensemble (haute confiance)
- Nom du groupe : `Juu Shiro`

### Cas 2 : Série avec saisons

**Input** :

- `Naruto S01E01.mkv`
- `Naruto S01E02.mkv`
- `Naruto S02E01.mkv`

**Résultat** :

```
Naruto/
  Season 01/
    Episode 01.mkv
    Episode 02.mkv
  Season 02/
    Episode 01.mkv
```

### Cas 3 : Séries différentes

**Input** :

- `Naruto.mkv`
- `Naruto Shippuden.mkv`

**Résultat** :

- Non regroupés (ou validation utilisateur requise)
- Justification : "Titres similaires mais suffixes différents"

## Conclusion

Cette architecture garantit :

- ✅ Aucune implémentation naïve
- ✅ Séparation stricte des responsabilités
- ✅ Traçabilité complète
- ✅ Testabilité maximale
- ✅ Extensibilité future
- ✅ Qualité professionnelle
