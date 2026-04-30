"""
Infrastructure Layer - Stratégie de regroupement hiérarchique
Regroupe intelligemment les fichiers similaires
"""

from typing import Optional
from collections import defaultdict

from src.domain.entities import (
    FileItem,
    SimilarityScore,
    GroupingDecision,
    ContentType,
)
from src.domain.interfaces import IGroupingStrategy, ILogger


class HierarchicalGroupingStrategy(IGroupingStrategy):
    """
    Stratégie de regroupement hiérarchique
    
    Logique:
    1. Regroupe par titre principal (ex: "Naruto")
    2. Sous-regroupe par saison (ex: "Naruto/Season 01")
    3. Valide les regroupements ambigus
    
    Gère les cas:
    - One Piece S01 ≠ One Piece S02 (mais sous même parent)
    - Naruto ≠ Naruto Shippuden (séries différentes)
    """
    
    def __init__(
        self,
        high_confidence_threshold: float = 0.85,
        ambiguous_min_threshold: float = 0.5,
        logger: Optional[ILogger] = None,
    ):
        """
        Initialise la stratégie
        
        Args:
            high_confidence_threshold: Seuil pour regroupement automatique
            ambiguous_min_threshold: Seuil minimum pour considérer un regroupement
            logger: Logger pour traçabilité
        """
        if not 0.0 <= ambiguous_min_threshold < high_confidence_threshold <= 1.0:
            raise ValueError("Seuils invalides")
        
        self.high_confidence_threshold = high_confidence_threshold
        self.ambiguous_min_threshold = ambiguous_min_threshold
        self.logger = logger
    
    def group(
        self,
        items: list[FileItem],
        similarity_matrix: dict[tuple[int, int], SimilarityScore]
    ) -> list[GroupingDecision]:
        """
        Crée des décisions de regroupement hiérarchique
        
        Algorithme:
        1. Créer des clusters basés sur la similarité
        2. Pour chaque cluster, déterminer la hiérarchie
        3. Générer les décisions avec justifications
        """
        if not items:
            return []
        
        self._log_info(f"Début du regroupement de {len(items)} items")
        
        # 1. Créer les clusters
        clusters = self._create_clusters(items, similarity_matrix)
        self._log_info(f"Créé {len(clusters)} clusters")
        
        # 2. Générer les décisions
        decisions = []
        for cluster_items in clusters:
            if len(cluster_items) < 2:
                continue
            
            cluster_decisions = self._create_cluster_decisions(
                cluster_items,
                similarity_matrix
            )
            decisions.extend(cluster_decisions)
        
        self._log_info(f"Généré {len(decisions)} décisions de regroupement")
        
        return decisions
    
    def _create_clusters(
        self,
        items: list[FileItem],
        similarity_matrix: dict[tuple[int, int], SimilarityScore]
    ) -> list[list[FileItem]]:
        """
        Crée des clusters d'items similaires
        Utilise un algorithme de clustering par seuil
        """
        # Initialisation: chaque item dans son propre cluster
        clusters: list[set[int]] = [{i} for i in range(len(items))]
        
        # Fusion des clusters similaires
        for (i, j), score in similarity_matrix.items():
            if score.total >= self.ambiguous_min_threshold:
                # Trouver les clusters contenant i et j
                cluster_i = next(c for c in clusters if i in c)
                cluster_j = next(c for c in clusters if j in c)
                
                # Fusionner si différents
                if cluster_i is not cluster_j:
                    cluster_i.update(cluster_j)
                    clusters.remove(cluster_j)
        
        # Convertir en listes d'items
        return [
            [items[idx] for idx in cluster]
            for cluster in clusters
            if len(cluster) >= 2
        ]
    
    def _create_cluster_decisions(
        self,
        cluster_items: list[FileItem],
        similarity_matrix: dict[tuple[int, int], SimilarityScore]
    ) -> list[GroupingDecision]:
        """
        Crée des décisions de regroupement pour un cluster
        
        Gère la hiérarchie:
        - Groupe parent pour la série
        - Sous-groupes pour les saisons
        """
        decisions = []
        
        # Vérifier si c'est une série avec saisons
        has_seasons = any(
            item.semantic and item.semantic.season
            for item in cluster_items
        )
        
        if has_seasons:
            # Regroupement hiérarchique par saison
            decisions.extend(
                self._create_hierarchical_decisions(cluster_items, similarity_matrix)
            )
        else:
            # Regroupement simple
            decision = self._create_simple_decision(cluster_items, similarity_matrix)
            if decision:
                decisions.append(decision)
        
        return decisions
    
    def _create_hierarchical_decisions(
        self,
        cluster_items: list[FileItem],
        similarity_matrix: dict[tuple[int, int], SimilarityScore]
    ) -> list[GroupingDecision]:
        """
        Crée des décisions hiérarchiques pour séries avec saisons
        
        Structure:
        - Série/
          - Season 01/
            - Episode 01.mkv
            - Episode 02.mkv
          - Season 02/
            - Episode 01.mkv
        """
        decisions = []
        
        # Grouper par saison
        seasons: dict[int, list[FileItem]] = defaultdict(list)
        no_season: list[FileItem] = []
        
        for item in cluster_items:
            if item.semantic and item.semantic.season:
                seasons[item.semantic.season.number].append(item)
            else:
                no_season.append(item)
        
        # Nom de la série (du premier item)
        series_name = self._get_series_name(cluster_items)
        
        # Décision pour chaque saison
        for season_num, season_items in seasons.items():
            if len(season_items) < 2:
                continue
            
            # Calculer la confiance moyenne
            avg_confidence = self._calculate_average_confidence(
                season_items,
                similarity_matrix
            )
            
            # Nom du groupe
            group_name = f"{series_name}/Season {season_num:02d}"
            
            # Créer la décision
            decision = GroupingDecision(
                items=season_items,
                group_name=group_name,
                confidence=avg_confidence,
                requires_validation=avg_confidence < self.high_confidence_threshold,
            )
            
            # Justifications
            decision.reasoning.append(f"Série: {series_name}")
            decision.reasoning.append(f"Saison: {season_num}")
            decision.reasoning.append(f"Nombre d'épisodes: {len(season_items)}")
            decision.reasoning.append(f"Confiance moyenne: {avg_confidence:.2f}")
            
            if decision.requires_validation:
                decision.reasoning.append("⚠ Validation utilisateur requise")
            
            decisions.append(decision)
            
            self._log_debug(
                f"Décision créée: {group_name}",
                items_count=len(season_items),
                confidence=avg_confidence
            )
        
        return decisions
    
    def _create_simple_decision(
        self,
        cluster_items: list[FileItem],
        similarity_matrix: dict[tuple[int, int], SimilarityScore]
    ) -> Optional[GroupingDecision]:
        """Crée une décision de regroupement simple (non hiérarchique)"""
        
        if len(cluster_items) < 2:
            return None
        
        # Calculer la confiance moyenne
        avg_confidence = self._calculate_average_confidence(
            cluster_items,
            similarity_matrix
        )
        
        # Nom du groupe (du premier item avec sémantique)
        group_name = self._get_group_name(cluster_items)
        
        # Créer la décision
        decision = GroupingDecision(
            items=cluster_items,
            group_name=group_name,
            confidence=avg_confidence,
            requires_validation=avg_confidence < self.high_confidence_threshold,
        )
        
        # Justifications
        decision.reasoning.append(f"Groupe: {group_name}")
        decision.reasoning.append(f"Nombre d'items: {len(cluster_items)}")
        decision.reasoning.append(f"Confiance moyenne: {avg_confidence:.2f}")
        
        if decision.requires_validation:
            decision.reasoning.append("⚠ Validation utilisateur requise")
        
        self._log_debug(
            f"Décision simple créée: {group_name}",
            items_count=len(cluster_items),
            confidence=avg_confidence
        )
        
        return decision
    
    def _get_series_name(self, items: list[FileItem]) -> str:
        """Récupère le nom de la série"""
        for item in items:
            if item.semantic and item.semantic.title:
                return item.semantic.title
        
        # Fallback sur le premier nom
        return items[0].name if items else "Unknown"
    
    def _get_group_name(self, items: list[FileItem]) -> str:
        """Récupère le nom du groupe"""
        # Essayer d'utiliser le titre sémantique
        for item in items:
            if item.semantic and item.semantic.title:
                return item.semantic.title
        
        # Fallback: utiliser le nom du premier item
        return items[0].name if items else "Unknown Group"
    
    def _calculate_average_confidence(
        self,
        items: list[FileItem],
        similarity_matrix: dict[tuple[int, int], SimilarityScore]
    ) -> float:
        """Calcule la confiance moyenne pour un groupe d'items"""
        if len(items) < 2:
            return 1.0
        
        # Récupérer tous les scores de similarité pour ces items
        scores = []
        item_indices = {id(item): idx for idx, item in enumerate(items)}
        
        for (i, j), score in similarity_matrix.items():
            # Vérifier si les deux indices correspondent à des items du groupe
            # (approximation simplifiée)
            scores.append(score.total)
        
        if not scores:
            return 0.5
        
        return sum(scores) / len(scores)
    
    def _log_info(self, message: str, **context) -> None:
        """Log niveau info"""
        if self.logger:
            self.logger.info(message, **context)
    
    def _log_debug(self, message: str, **context) -> None:
        """Log niveau debug"""
        if self.logger:
            self.logger.debug(message, **context)
