"""
Infrastructure Layer - Calcul de similarité sémantique
Algorithmes avancés, pas de comparaisons naïves
"""

from typing import Optional
from rapidfuzz import fuzz
import jellyfish

from src.domain.entities import (
    SemanticStructure,
    SimilarityScore,
    SeasonInfo,
    EpisodeInfo,
)
from src.domain.interfaces import ISimilarityCalculator


class AdvancedSimilarityCalculator(ISimilarityCalculator):
    """
    Calculateur de similarité sémantique avancé
    
    Utilise plusieurs algorithmes:
    - Jaro-Winkler pour similarité phonétique
    - Levenshtein pour distance d'édition
    - Token Set Ratio pour ordre des mots
    - Logique métier pour structure (saison/épisode)
    """
    
    def __init__(
        self,
        title_weight: float = 0.5,
        structural_weight: float = 0.3,
        temporal_weight: float = 0.1,
        quality_weight: float = 0.1,
    ):
        """
        Initialise le calculateur
        
        Args:
            title_weight: Poids du titre (0.0 à 1.0)
            structural_weight: Poids de la structure (saison/épisode)
            temporal_weight: Poids temporel (année)
            quality_weight: Poids de la qualité
        """
        # Validation des poids
        total = title_weight + structural_weight + temporal_weight + quality_weight
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"La somme des poids doit être 1.0, obtenu: {total}")
        
        self.weights = {
            'title': title_weight,
            'structural': structural_weight,
            'temporal': temporal_weight,
            'quality': quality_weight,
        }
    
    def calculate(
        self,
        item1: SemanticStructure,
        item2: SemanticStructure
    ) -> SimilarityScore:
        """
        Calcule le score de similarité entre deux structures
        
        Combine plusieurs métriques:
        1. Similarité du titre (phonétique + édition + tokens)
        2. Similarité structurelle (saison/épisode)
        3. Similarité temporelle (année)
        4. Similarité de qualité
        """
        # Calcul des composants
        title_sim = self._calculate_title_similarity(item1.title, item2.title)
        structural_sim = self._calculate_structural_similarity(item1, item2)
        temporal_sim = self._calculate_temporal_similarity(item1.year, item2.year)
        quality_sim = self._calculate_quality_similarity(item1.quality, item2.quality)
        
        # Score pondéré
        total_score = (
            title_sim * self.weights['title'] +
            structural_sim * self.weights['structural'] +
            temporal_sim * self.weights['temporal'] +
            quality_sim * self.weights['quality']
        )
        
        # Création du score avec justification
        score = SimilarityScore(
            total=total_score,
            title_similarity=title_sim,
            structural_similarity=structural_sim,
            temporal_similarity=temporal_sim,
            quality_similarity=quality_sim,
            weights=self.weights.copy(),
        )
        
        # Ajout des justifications
        self._add_reasoning(score, item1, item2)
        
        return score
    
    def calculate_matrix(
        self,
        items: list[SemanticStructure]
    ) -> dict[tuple[int, int], SimilarityScore]:
        """
        Calcule la matrice de similarité
        
        Returns:
            Dictionnaire (i, j) -> score pour i < j
        """
        matrix = {}
        
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                score = self.calculate(items[i], items[j])
                matrix[(i, j)] = score
        
        return matrix
    
    def _calculate_title_similarity(self, title1: str, title2: str) -> float:
        """
        Calcule la similarité des titres
        
        Combine plusieurs métriques:
        - Jaro-Winkler (similarité phonétique)
        - Token Set Ratio (ordre des mots)
        - Levenshtein normalisé
        
        Gère les cas:
        - juu-shiro ≈ juushiro ≈ juu shiro
        - miss marvel ≈ kiss-missmarvel
        """
        if not title1 or not title2:
            return 0.0
        
        # Normalisation
        t1 = title1.lower().strip()
        t2 = title2.lower().strip()
        
        # Égalité exacte
        if t1 == t2:
            return 1.0
        
        # Jaro-Winkler (bon pour variantes phonétiques)
        jaro_score = jellyfish.jaro_winkler_similarity(t1, t2)
        
        # Token Set Ratio (ignore l'ordre des mots)
        token_score = fuzz.token_set_ratio(t1, t2) / 100.0
        
        # Ratio partiel (sous-chaînes)
        partial_score = fuzz.partial_ratio(t1, t2) / 100.0
        
        # Combinaison pondérée
        combined = (
            jaro_score * 0.4 +
            token_score * 0.4 +
            partial_score * 0.2
        )
        
        return combined
    
    def _calculate_structural_similarity(
        self,
        item1: SemanticStructure,
        item2: SemanticStructure
    ) -> float:
        """
        Calcule la similarité structurelle (saison/épisode)
        
        Logique:
        - Même saison, même épisode → 1.0 (doublons)
        - Même saison, épisodes différents → 0.7 (même série)
        - Saisons différentes → 0.5 (même série, saisons différentes)
        - Pas de structure → 0.0
        """
        s1, s2 = item1.season, item2.season
        e1, e2 = item1.episode, item2.episode
        
        # Aucune structure
        if not (s1 or e1 or s2 or e2):
            return 0.0
        
        # Un seul a une structure → faible similarité
        if bool(s1 or e1) != bool(s2 or e2):
            return 0.2
        
        # Comparaison des saisons
        if s1 and s2:
            if s1.number == s2.number:
                # Même saison
                if e1 and e2:
                    # Comparaison des épisodes
                    if e1.number == e2.number:
                        return 1.0  # Même épisode (doublon probable)
                    else:
                        return 0.7  # Même saison, épisodes différents
                else:
                    return 0.8  # Même saison, épisodes non spécifiés
            else:
                # Saisons différentes (même série)
                return 0.5
        
        # Comparaison des épisodes seuls
        if e1 and e2:
            if e1.number == e2.number:
                return 0.9
            else:
                return 0.6
        
        return 0.3
    
    def _calculate_temporal_similarity(
        self,
        year1: Optional[int],
        year2: Optional[int]
    ) -> float:
        """
        Calcule la similarité temporelle (année)
        
        Logique:
        - Même année → 1.0
        - Années proches (±1) → 0.8
        - Années proches (±2-3) → 0.5
        - Années éloignées → 0.0
        - Pas d'année → 0.5 (neutre)
        """
        if year1 is None or year2 is None:
            return 0.5  # Neutre si pas d'info
        
        diff = abs(year1 - year2)
        
        if diff == 0:
            return 1.0
        elif diff == 1:
            return 0.8
        elif diff <= 3:
            return 0.5
        else:
            return 0.0
    
    def _calculate_quality_similarity(
        self,
        quality1: Optional,
        quality2: Optional
    ) -> float:
        """
        Calcule la similarité de qualité
        
        Logique:
        - Même résolution → bonus
        - Même source → bonus
        - Pas d'info → neutre
        """
        if quality1 is None or quality2 is None:
            return 0.5  # Neutre
        
        score = 0.0
        count = 0
        
        # Résolution
        if quality1.resolution and quality2.resolution:
            count += 1
            if quality1.resolution.lower() == quality2.resolution.lower():
                score += 1.0
        
        # Source
        if quality1.source and quality2.source:
            count += 1
            if quality1.source.lower() == quality2.source.lower():
                score += 1.0
        
        # Codec
        if quality1.codec and quality2.codec:
            count += 1
            if quality1.codec.lower() == quality2.codec.lower():
                score += 1.0
        
        if count == 0:
            return 0.5
        
        return score / count
    
    def _add_reasoning(
        self,
        score: SimilarityScore,
        item1: SemanticStructure,
        item2: SemanticStructure
    ) -> None:
        """Ajoute des justifications au score"""
        
        # Titre
        if score.title_similarity >= 0.9:
            score.add_reasoning(f"Titres très similaires: '{item1.title}' ≈ '{item2.title}'")
        elif score.title_similarity >= 0.7:
            score.add_reasoning(f"Titres similaires: '{item1.title}' ~ '{item2.title}'")
        elif score.title_similarity < 0.5:
            score.add_reasoning(f"Titres différents: '{item1.title}' ≠ '{item2.title}'")
        
        # Structure
        if item1.season and item2.season:
            if item1.season.number == item2.season.number:
                score.add_reasoning(f"Même saison: {item1.season}")
                if item1.episode and item2.episode:
                    if item1.episode.number == item2.episode.number:
                        score.add_reasoning(f"Même épisode: {item1.episode} (doublon probable)")
                    else:
                        score.add_reasoning(f"Épisodes différents: {item1.episode} vs {item2.episode}")
            else:
                score.add_reasoning(f"Saisons différentes: {item1.season} vs {item2.season}")
        
        # Année
        if item1.year and item2.year:
            if item1.year == item2.year:
                score.add_reasoning(f"Même année: {item1.year}")
            else:
                score.add_reasoning(f"Années différentes: {item1.year} vs {item2.year}")
        
        # Score global
        if score.is_high_confidence():
            score.add_reasoning("✓ Haute confiance de regroupement")
        elif score.is_ambiguous():
            score.add_reasoning("⚠ Score ambigu - validation utilisateur recommandée")
        else:
            score.add_reasoning("✗ Faible similarité - regroupement non recommandé")
