"""
SmartSort - Merger Module
Logique de clustering et fusion intelligente avec règles métier
"""

from typing import List, Dict, Tuple, Set
from dataclasses import dataclass, field
from pathlib import Path
from thefuzz import fuzz
from normalizer import Normalizer, NormalizedData


@dataclass
class MergeAction:
    """Représente une action de fusion à effectuer"""
    source_paths: List[Path]
    destination_path: Path
    action_type: str  # 'merge', 'hierarchy', 'rename'
    reason: str
    conflicts: List[str] = field(default_factory=list)


class DirectoryMerger:
    """
    Moteur de clustering et fusion avec règles métier avancées
    Utilise fuzzy matching (thefuzz) pour la comparaison sémantique
    """
    
    # Seuils de similarité
    EXACT_MATCH_THRESHOLD = 100
    FUZZY_MATCH_THRESHOLD = 92
    
    def __init__(self, normalizer: Normalizer):
        self.normalizer = normalizer
        self.merge_actions: List[MergeAction] = []
    
    def analyze_directories(self, root_path: Path) -> List[MergeAction]:
        """
        Analyse un répertoire et génère les actions de fusion
        
        Args:
            root_path: Chemin racine à analyser
            
        Returns:
            Liste des actions de fusion proposées
        """
        if not root_path.exists() or not root_path.is_dir():
            raise ValueError(f"Chemin invalide : {root_path}")
        
        # Récupère tous les sous-répertoires
        directories = [d for d in root_path.iterdir() if d.is_dir()]
        
        if not directories:
            return []
        
        # Normalise tous les noms
        normalized_data: Dict[Path, NormalizedData] = {}
        for directory in directories:
            norm = self.normalizer.preprocess(directory.name)
            if norm.is_valid:
                normalized_data[directory] = norm
        
        # Groupe par similarité
        clusters = self._cluster_by_similarity(normalized_data)
        
        # Génère les actions de fusion
        self.merge_actions = []
        for cluster in clusters:
            if len(cluster) > 1:
                action = self._create_merge_action(cluster, normalized_data)
                if action:
                    self.merge_actions.append(action)
        
        return self.merge_actions
    
    def _cluster_by_similarity(
        self, 
        normalized_data: Dict[Path, NormalizedData]
    ) -> List[List[Path]]:
        """
        Clustering par similarité fuzzy
        Utilise Union-Find pour regrouper les éléments similaires
        """
        paths = list(normalized_data.keys())
        n = len(paths)
        
        # Union-Find structure
        parent = {i: i for i in range(n)}
        
        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]
        
        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py
        
        # Compare toutes les paires
        for i in range(n):
            for j in range(i + 1, n):
                if self._should_merge(
                    normalized_data[paths[i]], 
                    normalized_data[paths[j]]
                ):
                    union(i, j)
        
        # Regroupe par cluster
        clusters_dict: Dict[int, List[Path]] = {}
        for i in range(n):
            root = find(i)
            if root not in clusters_dict:
                clusters_dict[root] = []
            clusters_dict[root].append(paths[i])
        
        return list(clusters_dict.values())
    
    def _should_merge(self, norm1: NormalizedData, norm2: NormalizedData) -> bool:
        """
        Détermine si deux répertoires doivent être fusionnés
        Applique les règles métier de similarité
        """
        # RÈGLE 04 : Gestion des inversions et sous-ensembles de mots
        # Vérifie si l'un est une sous-chaîne de l'autre
        name1_words = set(norm1.root_name.split())
        name2_words = set(norm2.root_name.split())
        
        # Si les mots clés sont identiques (ordre différent)
        if name1_words == name2_words:
            return True
        
        # Si l'un contient tous les mots de l'autre (subset matching)
        # Ex: "kiss miss marvel" contient "miss marvel"
        if name1_words.issubset(name2_words) or name2_words.issubset(name1_words):
            # Pour les subsets, on est plus permissif (70% au lieu de 92%)
            similarity = fuzz.ratio(norm1.root_name, norm2.root_name)
            if similarity >= 70:
                return True
        
        # Calcul de similarité fuzzy standard ET token-based
        # token_sort_ratio gère mieux les mots réordonnés ou fusionnés
        # Ex: "juu shiro" vs "juushiro"
        similarity_standard = fuzz.ratio(norm1.root_name, norm2.root_name)
        similarity_token = fuzz.token_sort_ratio(norm1.root_name, norm2.root_name)
        
        # Utilise le meilleur score
        similarity = max(similarity_standard, similarity_token)
        
        if similarity < self.FUZZY_MATCH_THRESHOLD:
            return False
        
        # RÈGLE 03 : Protection - Années différentes = séparation
        if norm1.year and norm2.year and norm1.year != norm2.year:
            # Exception : si différence < 2 ans, c'est probablement la même série
            if abs(norm1.year - norm2.year) > 2:
                return False
        
        return similarity >= self.FUZZY_MATCH_THRESHOLD
    
    def _create_merge_action(
        self, 
        cluster: List[Path], 
        normalized_data: Dict[Path, NormalizedData]
    ) -> MergeAction:
        """
        Crée une action de fusion pour un cluster
        Applique les règles métier (01, 02, 03, 04)
        """
        # Récupère les données normalisées
        norms = [normalized_data[path] for path in cluster]
        
        # Détermine le nom de base (le plus propre)
        base_name = self._select_best_name(norms)
        
        # Vérifie les saisons
        seasons = [n.season for n in norms if n.season is not None]
        has_multiple_seasons = len(set(seasons)) > 1
        
        # Vérifie les années
        years = [n.year for n in norms if n.year is not None]
        has_conflicting_years = len(set(years)) > 1 and any(
            abs(y1 - y2) > 2 for y1 in years for y2 in years if y1 != y2
        )
        
        # RÈGLE 03 : Protection - Années conflictuelles
        if has_conflicting_years:
            return None  # Ne pas fusionner
        
        # RÈGLE 02 : Hiérarchie - Saisons multiples
        if has_multiple_seasons:
            dest_path = cluster[0].parent / base_name
            return MergeAction(
                source_paths=cluster,
                destination_path=dest_path,
                action_type='hierarchy',
                reason=f"Création hiérarchie pour {len(seasons)} saisons"
            )
        
        # RÈGLE 01 : Fusion directe
        dest_path = cluster[0].parent / base_name
        return MergeAction(
            source_paths=cluster,
            destination_path=dest_path,
            action_type='merge',
            reason=f"Fusion de {len(cluster)} répertoires similaires"
        )
    
    def _select_best_name(self, norms: List[NormalizedData]) -> str:
        """
        Sélectionne le meilleur nom parmi les candidats
        Critères : le plus court, le plus propre, le plus fréquent
        """
        # Compte les occurrences
        name_counts: Dict[str, int] = {}
        for norm in norms:
            name_counts[norm.root_name] = name_counts.get(norm.root_name, 0) + 1
        
        # Sélectionne le plus fréquent, puis le plus court
        best_name = max(
            name_counts.keys(),
            key=lambda x: (name_counts[x], -len(x))
        )
        
        # Capitalise proprement (Title Case)
        return best_name.title()
    
    def get_merge_preview(self) -> List[Dict[str, any]]:
        """
        Génère un aperçu des fusions pour l'UI
        
        Returns:
            Liste de dictionnaires avec source -> destination
        """
        preview = []
        for action in self.merge_actions:
            preview.append({
                'sources': [str(p.name) for p in action.source_paths],
                'destination': str(action.destination_path.name),
                'type': action.action_type,
                'reason': action.reason,
                'conflicts': action.conflicts
            })
        return preview
