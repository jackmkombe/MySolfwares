# Points d'Extension Futurs

Ce document décrit les points d'extension prévus pour faire évoluer le logiciel.

## 1. Algorithmes de Similarité Avancés

### Extension NLP avec modèles de langage

**Interface** : `ISimilarityCalculator`

**Implémentation suggérée** :

```python
class BERTSimilarityCalculator(ISimilarityCalculator):
    """Utilise BERT pour similarité sémantique profonde"""

    def __init__(self, model_name: str = "bert-base-uncased"):
        self.model = load_bert_model(model_name)

    def calculate(self, item1, item2):
        # Encoder les titres avec BERT
        embedding1 = self.model.encode(item1.title)
        embedding2 = self.model.encode(item2.title)

        # Calculer similarité cosinus
        similarity = cosine_similarity(embedding1, embedding2)

        return SimilarityScore(...)
```

**Avantages** :

- Comprend le contexte sémantique
- Meilleure gestion des synonymes
- Détection de relations complexes

### Apprentissage des préférences utilisateur

**Interface** : `ISimilarityCalculator`

**Implémentation suggérée** :

```python
class AdaptiveSimilarityCalculator(ISimilarityCalculator):
    """Apprend des décisions utilisateur pour ajuster les poids"""

    def __init__(self):
        self.weights = default_weights()
        self.history = []

    def learn_from_decision(self, decision: GroupingDecision, validated: bool):
        # Ajuster les poids basés sur la validation
        if validated and decision.confidence < 0.85:
            # Augmenter les poids des composants similaires
            self._adjust_weights(decision)

        self.history.append((decision, validated))
```

**Avantages** :

- S'adapte aux préférences de l'utilisateur
- Améliore la précision au fil du temps
- Réduit le besoin de validation manuelle

## 2. Sources de Métadonnées Externes

### API TMDB/TVDB

**Interface** : `ISemanticExtractor`

**Implémentation suggérée** :

```python
class TMDBSemanticExtractor(ISemanticExtractor):
    """Enrichit avec métadonnées de TMDB"""

    def __init__(self, api_key: str):
        self.api = TMDBClient(api_key)

    def extract(self, filename: str):
        # Extraction basique
        basic_struct = basic_extraction(filename)

        # Recherche sur TMDB
        results = self.api.search(basic_struct.title)

        if results:
            # Enrichir avec métadonnées
            return enrich_with_tmdb(basic_struct, results[0])

        return basic_struct
```

**Métadonnées supplémentaires** :

- Genre (action, comédie, etc.)
- Acteurs/réalisateurs
- Note/popularité
- Synopsis
- Poster/artwork

### Lecture de métadonnées embarquées

**Interface** : `ISemanticExtractor`

**Implémentation suggérée** :

```python
class EmbeddedMetadataExtractor(ISemanticExtractor):
    """Lit les métadonnées embarquées (MKV, MP4)"""

    def extract(self, filename: str):
        # Lire les métadonnées du fichier
        metadata = read_file_metadata(filename)

        return SemanticStructure(
            title=metadata.get('title'),
            year=metadata.get('year'),
            # etc.
        )
```

**Formats supportés** :

- MKV (Matroska tags)
- MP4 (iTunes tags)
- AVI (RIFF tags)

## 3. Stratégies de Regroupement Avancées

### Regroupement par genre

**Interface** : `IGroupingStrategy`

**Implémentation suggérée** :

```python
class GenreBasedGroupingStrategy(IGroupingStrategy):
    """Regroupe par genre en plus de la similarité"""

    def group(self, items, similarity_matrix):
        # Grouper par genre d'abord
        genre_groups = defaultdict(list)
        for item in items:
            if item.semantic and item.semantic.genre:
                genre_groups[item.semantic.genre].append(item)

        # Puis appliquer similarité dans chaque groupe
        decisions = []
        for genre, genre_items in genre_groups.items():
            sub_decisions = hierarchical_grouping(genre_items, similarity_matrix)
            decisions.extend(sub_decisions)

        return decisions
```

**Structure générée** :

```
Media/
  Action/
    Movie 1/
    Movie 2/
  Comedy/
    Movie 3/
```

### Regroupement chronologique

**Interface** : `IGroupingStrategy`

**Implémentation suggérée** :

```python
class ChronologicalGroupingStrategy(IGroupingStrategy):
    """Regroupe par période temporelle"""

    def group(self, items, similarity_matrix):
        # Grouper par décennie
        decade_groups = defaultdict(list)
        for item in items:
            if item.semantic and item.semantic.year:
                decade = (item.semantic.year // 10) * 10
                decade_groups[decade].append(item)

        return create_decade_decisions(decade_groups)
```

**Structure générée** :

```
Media/
  2020s/
    Movie 1 (2020)/
    Movie 2 (2023)/
  2010s/
    Movie 3 (2015)/
```

## 4. Modes d'Exécution Avancés

### Mode simulation (dry-run)

**Extension** : `FileOrganizationUseCase`

```python
class FileOrganizationUseCase:
    def execute(self, directory_path, recursive=True, dry_run=False):
        # ... analyse normale ...

        if dry_run:
            # Générer un rapport sans modifier les fichiers
            return self._generate_simulation_report(decisions)
        else:
            # Exécution réelle
            self._execute_groupings(decisions)
```

**Rapport de simulation** :

- Aperçu des changements
- Estimation de l'espace disque
- Détection de conflits potentiels

### Création de liens symboliques

**Extension** : `IFileSystemRepository`

```python
class WindowsFileSystemRepository(IFileSystemRepository):
    def create_symlink(self, source: Path, destination: Path) -> bool:
        """Crée un lien symbolique au lieu de déplacer"""
        import os
        os.symlink(source, destination)
        return True
```

**Avantages** :

- Pas de duplication
- Organisation virtuelle
- Fichiers restent à leur emplacement original

### Historique avec undo

**Nouvelle interface** :

```python
class IHistoryManager(ABC):
    @abstractmethod
    def record_action(self, action: Action) -> None:
        """Enregistre une action"""
        pass

    @abstractmethod
    def undo_last_action(self) -> bool:
        """Annule la dernière action"""
        pass

    @abstractmethod
    def get_history(self) -> list[Action]:
        """Récupère l'historique"""
        pass
```

**Implémentation** :

```python
class FileHistoryManager(IHistoryManager):
    def __init__(self):
        self.history = []

    def record_action(self, action: Action):
        self.history.append(action)
        # Sauvegarder dans une DB SQLite
        self._persist_action(action)

    def undo_last_action(self):
        if not self.history:
            return False

        action = self.history.pop()
        # Inverser l'action
        action.undo()
        return True
```

## 5. Interface Utilisateur Avancée

### Mode batch/CLI

**Nouvelle interface** :

```python
class CLIInterface:
    """Interface en ligne de commande"""

    def run(self, args):
        # Parser les arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('directory')
        parser.add_argument('--recursive', action='store_true')
        parser.add_argument('--auto-execute', action='store_true')

        # Exécuter
        use_case.execute(...)
```

**Utilisation** :

```bash
python -m src.cli /path/to/directory --recursive --auto-execute
```

### Prévisualisation graphique

**Extension** : `MainWindow`

```python
class MainWindow(QMainWindow):
    def show_preview(self, decision: GroupingDecision):
        """Affiche une prévisualisation de la structure"""
        tree_widget = QTreeWidget()

        # Construire l'arbre
        root = QTreeWidgetItem([decision.group_name])
        for item in decision.items:
            child = QTreeWidgetItem([item.name])
            root.addChild(child)

        tree_widget.addTopLevelItem(root)
        # ...
```

### Dashboard de statistiques

**Nouvelle fenêtre** :

```python
class StatisticsWindow(QWidget):
    """Affiche des statistiques sur la collection"""

    def show_statistics(self, items: list[FileItem]):
        # Calculer statistiques
        total_size = sum(item.size for item in items)
        by_type = Counter(item.file_type for item in items)
        by_year = Counter(item.semantic.year for item in items if item.semantic)

        # Afficher graphiques
        self._show_pie_chart(by_type)
        self._show_bar_chart(by_year)
```

## 6. Optimisations de Performance

### Cache de résultats

**Nouvelle interface** :

```python
class ICacheManager(ABC):
    @abstractmethod
    def get_semantic_structure(self, filename: str) -> Optional[SemanticStructure]:
        pass

    @abstractmethod
    def cache_semantic_structure(self, filename: str, structure: SemanticStructure):
        pass
```

**Implémentation** :

```python
class RedisCacheManager(ICacheManager):
    """Cache avec Redis"""

    def __init__(self, redis_client):
        self.redis = redis_client

    def get_semantic_structure(self, filename: str):
        cached = self.redis.get(f"semantic:{filename}")
        if cached:
            return deserialize(cached)
        return None
```

### Traitement parallèle

**Extension** : `FileOrganizationUseCase`

```python
from concurrent.futures import ThreadPoolExecutor

class FileOrganizationUseCase:
    def _extract_semantic_structures(self, items):
        # Traitement parallèle
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(self.semantic_extractor.extract, item.name)
                for item in items
            ]

            results = [future.result() for future in futures]

        return results
```

## 7. Intégrations Cloud

### Synchronisation cloud

**Nouvelle interface** :

```python
class ICloudSync(ABC):
    @abstractmethod
    def sync_to_cloud(self, local_path: Path, cloud_path: str) -> bool:
        pass

    @abstractmethod
    def sync_from_cloud(self, cloud_path: str, local_path: Path) -> bool:
        pass
```

**Implémentations possibles** :

- Google Drive
- OneDrive
- Dropbox
- S3

### Backup automatique

**Extension** : `FileOrganizationUseCase`

```python
class FileOrganizationUseCase:
    def execute(self, directory_path, backup_before=True):
        if backup_before:
            # Créer backup avant modifications
            self.backup_service.create_backup(directory_path)

        # Exécution normale
        decisions = self._process(directory_path)

        return decisions
```

## Conclusion

Tous ces points d'extension sont **facilement implémentables** grâce à :

1. **Clean Architecture** : Séparation stricte des responsabilités
2. **Interfaces clairement définies** : Contrats stables
3. **Injection de dépendances** : Remplacement facile des implémentations
4. **Pas de couplage fort** : Chaque composant est indépendant

Pour ajouter une nouvelle fonctionnalité :

1. Identifier l'interface appropriée
2. Créer une nouvelle implémentation
3. Injecter dans `src/main.py`
4. Tester de manière isolée

**Aucune modification du code existant n'est nécessaire** pour la plupart des extensions !
