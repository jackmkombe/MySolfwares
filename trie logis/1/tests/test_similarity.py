"""
Tests unitaires pour l'algorithme de similarité
Démontre la testabilité et la traçabilité
"""

import pytest
from src.domain.entities import (
    SemanticStructure,
    ContentType,
    SeasonInfo,
    EpisodeInfo,
    QualityInfo,
)
from src.infrastructure.algorithms.similarity import AdvancedSimilarityCalculator


class TestAdvancedSimilarityCalculator:
    """Tests pour le calculateur de similarité"""
    
    @pytest.fixture
    def calculator(self):
        """Fixture pour le calculateur"""
        return AdvancedSimilarityCalculator(
            title_weight=0.5,
            structural_weight=0.3,
            temporal_weight=0.1,
            quality_weight=0.1,
        )
    
    def test_identical_titles_high_similarity(self, calculator):
        """Test: Titres identiques → haute similarité"""
        struct1 = SemanticStructure(
            title="Naruto",
            original_title="Naruto",
            content_type=ContentType.SERIES,
            extraction_confidence=0.9,
        )
        
        struct2 = SemanticStructure(
            title="Naruto",
            original_title="Naruto",
            content_type=ContentType.SERIES,
            extraction_confidence=0.9,
        )
        
        score = calculator.calculate(struct1, struct2)
        
        assert score.total >= 0.8, "Titres identiques devraient avoir haute similarité"
        assert score.title_similarity == 1.0, "Similarité de titre devrait être 1.0"
    
    def test_variant_spellings_recognized(self, calculator):
        """Test: Variantes orthographiques reconnues (juu-shiro ≈ juushiro)"""
        struct1 = SemanticStructure(
            title="juu-shiro",
            original_title="juu-shiro",
            content_type=ContentType.SERIES,
            extraction_confidence=0.9,
        )
        
        struct2 = SemanticStructure(
            title="juushiro",
            original_title="juushiro",
            content_type=ContentType.SERIES,
            extraction_confidence=0.9,
        )
        
        score = calculator.calculate(struct1, struct2)
        
        assert score.title_similarity >= 0.7, "Variantes orthographiques devraient être reconnues"
        assert len(score.reasoning) > 0, "Devrait avoir des justifications"
    
    def test_same_season_same_episode_duplicate(self, calculator):
        """Test: Même saison, même épisode → doublon probable"""
        struct1 = SemanticStructure(
            title="One Piece",
            original_title="One Piece",
            content_type=ContentType.SERIES,
            season=SeasonInfo(number=1),
            episode=EpisodeInfo(number=1),
            extraction_confidence=0.9,
        )
        
        struct2 = SemanticStructure(
            title="One Piece",
            original_title="One Piece",
            content_type=ContentType.SERIES,
            season=SeasonInfo(number=1),
            episode=EpisodeInfo(number=1),
            extraction_confidence=0.9,
        )
        
        score = calculator.calculate(struct1, struct2)
        
        assert score.structural_similarity == 1.0, "Même saison/épisode → similarité structurelle maximale"
        assert score.total >= 0.85, "Doublons devraient avoir très haute similarité"
    
    def test_same_season_different_episodes(self, calculator):
        """Test: Même saison, épisodes différents → même série"""
        struct1 = SemanticStructure(
            title="One Piece",
            original_title="One Piece",
            content_type=ContentType.SERIES,
            season=SeasonInfo(number=1),
            episode=EpisodeInfo(number=1),
            extraction_confidence=0.9,
        )
        
        struct2 = SemanticStructure(
            title="One Piece",
            original_title="One Piece",
            content_type=ContentType.SERIES,
            season=SeasonInfo(number=1),
            episode=EpisodeInfo(number=2),
            extraction_confidence=0.9,
        )
        
        score = calculator.calculate(struct1, struct2)
        
        assert score.structural_similarity >= 0.6, "Même saison → similarité structurelle élevée"
        assert "Même saison" in " ".join(score.reasoning), "Devrait mentionner la même saison"
    
    def test_different_seasons_same_series(self, calculator):
        """Test: Saisons différentes → même série mais groupes différents"""
        struct1 = SemanticStructure(
            title="One Piece",
            original_title="One Piece",
            content_type=ContentType.SERIES,
            season=SeasonInfo(number=1),
            extraction_confidence=0.9,
        )
        
        struct2 = SemanticStructure(
            title="One Piece",
            original_title="One Piece",
            content_type=ContentType.SERIES,
            season=SeasonInfo(number=2),
            extraction_confidence=0.9,
        )
        
        score = calculator.calculate(struct1, struct2)
        
        assert score.structural_similarity >= 0.4, "Saisons différentes mais même série"
        assert "Saisons différentes" in " ".join(score.reasoning), "Devrait mentionner saisons différentes"
    
    def test_naruto_vs_naruto_shippuden(self, calculator):
        """Test: Naruto ≠ Naruto Shippuden (séries différentes)"""
        struct1 = SemanticStructure(
            title="Naruto",
            original_title="Naruto",
            content_type=ContentType.SERIES,
            extraction_confidence=0.9,
        )
        
        struct2 = SemanticStructure(
            title="Naruto Shippuden",
            original_title="Naruto Shippuden",
            content_type=ContentType.SERIES,
            extraction_confidence=0.9,
        )
        
        score = calculator.calculate(struct1, struct2)
        
        # Devrait avoir une similarité modérée (titres similaires mais pas identiques)
        assert 0.4 <= score.title_similarity <= 0.8, "Titres similaires mais différents"
        assert score.is_ambiguous(), "Devrait être ambigu et nécessiter validation"
    
    def test_year_similarity(self, calculator):
        """Test: Années proches → bonus de similarité"""
        struct1 = SemanticStructure(
            title="Movie",
            original_title="Movie",
            content_type=ContentType.MOVIE,
            year=2020,
            extraction_confidence=0.9,
        )
        
        struct2 = SemanticStructure(
            title="Movie",
            original_title="Movie",
            content_type=ContentType.MOVIE,
            year=2020,
            extraction_confidence=0.9,
        )
        
        score = calculator.calculate(struct1, struct2)
        
        assert score.temporal_similarity == 1.0, "Même année → similarité temporelle maximale"
    
    def test_quality_similarity(self, calculator):
        """Test: Même qualité → bonus"""
        quality1 = QualityInfo(resolution="1080p", codec="x264", source="BluRay")
        quality2 = QualityInfo(resolution="1080p", codec="x264", source="BluRay")
        
        struct1 = SemanticStructure(
            title="Movie",
            original_title="Movie",
            content_type=ContentType.MOVIE,
            quality=quality1,
            extraction_confidence=0.9,
        )
        
        struct2 = SemanticStructure(
            title="Movie",
            original_title="Movie",
            content_type=ContentType.MOVIE,
            quality=quality2,
            extraction_confidence=0.9,
        )
        
        score = calculator.calculate(struct1, struct2)
        
        assert score.quality_similarity == 1.0, "Même qualité → similarité maximale"
    
    def test_reasoning_is_traceable(self, calculator):
        """Test: Toutes les décisions sont justifiées"""
        struct1 = SemanticStructure(
            title="Test",
            original_title="Test",
            content_type=ContentType.SERIES,
            season=SeasonInfo(number=1),
            extraction_confidence=0.9,
        )
        
        struct2 = SemanticStructure(
            title="Test",
            original_title="Test",
            content_type=ContentType.SERIES,
            season=SeasonInfo(number=2),
            extraction_confidence=0.9,
        )
        
        score = calculator.calculate(struct1, struct2)
        
        assert len(score.reasoning) > 0, "Devrait avoir des justifications"
        assert score.weights is not None, "Devrait avoir les poids utilisés"
        
        # Vérifier que les justifications sont informatives
        reasoning_text = " ".join(score.reasoning)
        assert len(reasoning_text) > 20, "Justifications devraient être détaillées"
    
    def test_ambiguous_scores_flagged(self, calculator):
        """Test: Scores ambigus sont flaggés pour validation"""
        struct1 = SemanticStructure(
            title="Similar Title",
            original_title="Similar Title",
            content_type=ContentType.SERIES,
            extraction_confidence=0.9,
        )
        
        struct2 = SemanticStructure(
            title="Similar Ttle",  # Faute de frappe
            original_title="Similar Ttle",
            content_type=ContentType.SERIES,
            extraction_confidence=0.9,
        )
        
        score = calculator.calculate(struct1, struct2)
        
        # Devrait être ambigu
        if score.is_ambiguous():
            assert "validation" in " ".join(score.reasoning).lower(), \
                "Devrait recommander validation utilisateur"


class TestSimilarityMatrix:
    """Tests pour le calcul de matrice"""
    
    def test_matrix_calculation(self):
        """Test: Calcul de matrice pour plusieurs items"""
        calculator = AdvancedSimilarityCalculator()
        
        items = [
            SemanticStructure(
                title="Naruto",
                original_title="Naruto",
                content_type=ContentType.SERIES,
                season=SeasonInfo(number=1),
                extraction_confidence=0.9,
            ),
            SemanticStructure(
                title="Naruto",
                original_title="Naruto",
                content_type=ContentType.SERIES,
                season=SeasonInfo(number=2),
                extraction_confidence=0.9,
            ),
            SemanticStructure(
                title="One Piece",
                original_title="One Piece",
                content_type=ContentType.SERIES,
                season=SeasonInfo(number=1),
                extraction_confidence=0.9,
            ),
        ]
        
        matrix = calculator.calculate_matrix(items)
        
        # Vérifier que la matrice contient les bonnes paires
        assert (0, 1) in matrix, "Devrait avoir (0, 1)"
        assert (0, 2) in matrix, "Devrait avoir (0, 2)"
        assert (1, 2) in matrix, "Devrait avoir (1, 2)"
        
        # Vérifier que (1, 0) n'existe pas (matrice triangulaire supérieure)
        assert (1, 0) not in matrix, "Ne devrait pas avoir (1, 0)"
        
        # Vérifier les scores
        assert matrix[(0, 1)].total > matrix[(0, 2)].total, \
            "Naruto S01 devrait être plus similaire à Naruto S02 qu'à One Piece"
