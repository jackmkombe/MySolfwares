"""
Application Layer - Cas d'usage principal
Orchestration de la logique métier
"""

from pathlib import Path
from typing import Optional

from src.domain.entities import FileItem, GroupingDecision
from src.domain.interfaces import (
    IFileSystemRepository,
    ISemanticExtractor,
    ISimilarityCalculator,
    IGroupingStrategy,
    IValidationService,
    ILogger,
)


class FileOrganizationUseCase:
    """
    Cas d'usage principal: Organisation intelligente de fichiers
    
    Workflow:
    1. Scanner le répertoire
    2. Extraire la structure sémantique
    3. Calculer les similarités
    4. Générer les décisions de regroupement
    5. Valider avec l'utilisateur si nécessaire
    6. Exécuter les regroupements validés
    """
    
    def __init__(
        self,
        filesystem_repo: IFileSystemRepository,
        semantic_extractor: ISemanticExtractor,
        similarity_calculator: ISimilarityCalculator,
        grouping_strategy: IGroupingStrategy,
        validation_service: IValidationService,
        logger: ILogger,
    ):
        """Injection de dépendances"""
        self.filesystem_repo = filesystem_repo
        self.semantic_extractor = semantic_extractor
        self.similarity_calculator = similarity_calculator
        self.grouping_strategy = grouping_strategy
        self.validation_service = validation_service
        self.logger = logger
    
    def execute(
        self,
        directory_path: Path,
        recursive: bool = True,
        auto_execute: bool = False,
    ) -> list[GroupingDecision]:
        """
        Exécute le cas d'usage complet
        
        Args:
            directory_path: Répertoire à analyser
            recursive: Scanner récursivement
            auto_execute: Exécuter automatiquement les décisions haute confiance
            
        Returns:
            Liste des décisions de regroupement
        """
        self.logger.info(
            "Début de l'organisation de fichiers",
            directory=str(directory_path),
            recursive=recursive,
        )
        
        # 1. Scanner le répertoire
        self.logger.info("Étape 1/6: Scan du répertoire")
        items = self._scan_directory(directory_path, recursive)
        
        if not items:
            self.logger.warning("Aucun fichier trouvé")
            return []
        
        # 2. Extraire la structure sémantique
        self.logger.info("Étape 2/6: Extraction sémantique")
        items_with_semantic = self._extract_semantic_structures(items)
        
        # 3. Calculer les similarités
        self.logger.info("Étape 3/6: Calcul des similarités")
        similarity_matrix = self._calculate_similarities(items_with_semantic)
        
        # 4. Générer les décisions de regroupement
        self.logger.info("Étape 4/6: Génération des décisions")
        decisions = self._generate_grouping_decisions(
            items_with_semantic,
            similarity_matrix
        )
        
        if not decisions:
            self.logger.info("Aucun regroupement proposé")
            return []
        
        # 5. Valider avec l'utilisateur
        self.logger.info("Étape 5/6: Validation utilisateur")
        validated_decisions = self._validate_decisions(decisions)
        
        # 6. Exécuter si demandé
        if auto_execute:
            self.logger.info("Étape 6/6: Exécution des regroupements")
            self._execute_groupings(validated_decisions)
        else:
            self.logger.info("Étape 6/6: Exécution différée (auto_execute=False)")
        
        self.logger.info(
            "Organisation terminée",
            total_decisions=len(decisions),
            validated_decisions=len(validated_decisions),
        )
        
        return validated_decisions
    
    def _scan_directory(
        self,
        directory_path: Path,
        recursive: bool
    ) -> list[FileItem]:
        """Scanne le répertoire"""
        try:
            items = self.filesystem_repo.scan_directory(directory_path, recursive)
            self.logger.info(f"Trouvé {len(items)} items")
            return items
        except Exception as e:
            self.logger.error(f"Erreur lors du scan: {e}")
            raise
    
    def _extract_semantic_structures(
        self,
        items: list[FileItem]
    ) -> list[FileItem]:
        """Extrait les structures sémantiques"""
        items_with_semantic = []
        
        for item in items:
            try:
                # Extraire la structure sémantique
                semantic = self.semantic_extractor.extract(item.name)
                
                # Créer un nouvel item avec la sémantique
                item_with_semantic = FileItem(
                    path=item.path,
                    name=item.name,
                    is_directory=item.is_directory,
                    file_type=item.file_type,
                    size=item.size,
                    semantic=semantic,
                    created_at=item.created_at,
                    modified_at=item.modified_at,
                )
                
                items_with_semantic.append(item_with_semantic)
                
                self.logger.debug(
                    f"Sémantique extraite: {item.name}",
                    title=semantic.title,
                    confidence=semantic.extraction_confidence,
                )
                
            except Exception as e:
                self.logger.warning(
                    f"Impossible d'extraire la sémantique pour {item.name}: {e}"
                )
                # Garder l'item sans sémantique
                items_with_semantic.append(item)
        
        return items_with_semantic
    
    def _calculate_similarities(
        self,
        items: list[FileItem]
    ) -> dict[tuple[int, int], any]:
        """Calcule la matrice de similarité"""
        # Filtrer les items avec sémantique
        items_with_semantic = [
            item for item in items
            if item.has_semantic_structure()
        ]
        
        if len(items_with_semantic) < 2:
            self.logger.warning("Pas assez d'items avec sémantique pour calculer les similarités")
            return {}
        
        # Extraire les structures sémantiques
        semantic_structures = [item.semantic for item in items_with_semantic]
        
        # Calculer la matrice
        similarity_matrix = self.similarity_calculator.calculate_matrix(
            semantic_structures
        )
        
        self.logger.info(
            f"Calculé {len(similarity_matrix)} scores de similarité"
        )
        
        return similarity_matrix
    
    def _generate_grouping_decisions(
        self,
        items: list[FileItem],
        similarity_matrix: dict
    ) -> list[GroupingDecision]:
        """Génère les décisions de regroupement"""
        decisions = self.grouping_strategy.group(items, similarity_matrix)
        
        # Log des décisions
        for i, decision in enumerate(decisions):
            self.logger.info(
                f"Décision {i+1}: {decision.group_name}",
                items_count=len(decision.items),
                confidence=decision.confidence,
                requires_validation=decision.requires_validation,
            )
        
        return decisions
    
    def _validate_decisions(
        self,
        decisions: list[GroupingDecision]
    ) -> list[GroupingDecision]:
        """Valide les décisions avec l'utilisateur"""
        validated = []
        
        # Séparer les décisions haute confiance et ambiguës
        high_confidence = [d for d in decisions if not d.requires_validation]
        ambiguous = [d for d in decisions if d.requires_validation]
        
        # Décisions haute confiance: validation automatique
        for decision in high_confidence:
            decision.validate()
            validated.append(decision)
            self.logger.info(
                f"Décision auto-validée: {decision.group_name}",
                confidence=decision.confidence,
            )
        
        # Décisions ambiguës: demander validation utilisateur
        if ambiguous:
            self.logger.info(
                f"{len(ambiguous)} décisions nécessitent une validation utilisateur"
            )
            
            validations = self.validation_service.request_batch_validation(ambiguous)
            
            for idx, is_validated in validations.items():
                decision = ambiguous[idx]
                if is_validated:
                    decision.validate()
                    validated.append(decision)
                    self.logger.info(f"Décision validée par l'utilisateur: {decision.group_name}")
                else:
                    decision.reject()
                    self.logger.info(f"Décision rejetée par l'utilisateur: {decision.group_name}")
        
        return validated
    
    def _execute_groupings(
        self,
        decisions: list[GroupingDecision]
    ) -> None:
        """Exécute les regroupements validés"""
        for decision in decisions:
            if not decision.validated:
                continue
            
            try:
                self._execute_single_grouping(decision)
                self.logger.info(f"Regroupement exécuté: {decision.group_name}")
            except Exception as e:
                self.logger.error(
                    f"Erreur lors du regroupement {decision.group_name}: {e}"
                )
    
    def _execute_single_grouping(self, decision: GroupingDecision) -> None:
        """Exécute un regroupement unique"""
        # Créer le répertoire de destination
        # Note: Le chemin exact dépend de la configuration
        # Pour l'instant, on log juste l'action
        
        self.logger.info(
            f"Création du groupe: {decision.group_name}",
            items=[item.name for item in decision.items],
        )
        
        # TODO: Implémenter le déplacement réel des fichiers
        # self.filesystem_repo.create_directory(...)
        # for item in decision.items:
        #     self.filesystem_repo.move_file(...)
