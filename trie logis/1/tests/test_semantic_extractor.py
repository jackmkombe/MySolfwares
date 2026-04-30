"""
Tests unitaires pour l'extracteur sémantique
Vérifie la capacité à extraire correctement la structure
"""

import pytest
from src.infrastructure.algorithms.semantic_extractor import SemanticExtractorService
from src.domain.entities import ContentType


class TestSemanticExtractor:
    """Tests pour l'extracteur sémantique"""
    
    @pytest.fixture
    def extractor(self):
        """Fixture pour l'extracteur"""
        return SemanticExtractorService()
    
    def test_extract_season_episode_s01e01(self, extractor):
        """Test: Extraction S01E01"""
        filename = "Naruto S01E01 [1080p].mkv"
        
        result = extractor.extract(filename)
        
        assert result.title == "Naruto", f"Titre incorrect: {result.title}"
        assert result.season is not None, "Saison non détectée"
        assert result.season.number == 1, f"Numéro de saison incorrect: {result.season.number}"
        assert result.episode is not None, "Épisode non détecté"
        assert result.episode.number == 1, f"Numéro d'épisode incorrect: {result.episode.number}"
        assert result.content_type == ContentType.SERIES, "Type de contenu incorrect"
    
    def test_extract_season_episode_variants(self, extractor):
        """Test: Variantes de format saison/épisode"""
        test_cases = [
            ("Show Season 1 Episode 5.mkv", 1, 5),
            ("Show s02e10.mkv", 2, 10),
            ("Show S03 E15.mkv", 3, 15),
        ]
        
        for filename, expected_season, expected_episode in test_cases:
            result = extractor.extract(filename)
            
            assert result.season is not None, f"Saison non détectée pour {filename}"
            assert result.season.number == expected_season, \
                f"Saison incorrecte pour {filename}: attendu {expected_season}, obtenu {result.season.number}"
            
            assert result.episode is not None, f"Épisode non détecté pour {filename}"
            assert result.episode.number == expected_episode, \
                f"Épisode incorrect pour {filename}: attendu {expected_episode}, obtenu {result.episode.number}"
    
    def test_extract_year(self, extractor):
        """Test: Extraction d'année"""
        test_cases = [
            ("Movie (2020).mkv", 2020),
            ("Movie 2019.mkv", 2019),
            ("Show 2021 S01E01.mkv", 2021),
        ]
        
        for filename, expected_year in test_cases:
            result = extractor.extract(filename)
            
            assert result.year == expected_year, \
                f"Année incorrecte pour {filename}: attendu {expected_year}, obtenu {result.year}"
    
    def test_extract_quality_info(self, extractor):
        """Test: Extraction d'informations de qualité"""
        filename = "Movie [1080p BluRay x264 AAC].mkv"
        
        result = extractor.extract(filename)
        
        assert result.quality is not None, "Qualité non détectée"
        assert result.quality.resolution == "1080p", f"Résolution incorrecte: {result.quality.resolution}"
        assert result.quality.source.lower() == "bluray", f"Source incorrecte: {result.quality.source}"
        assert result.quality.codec == "x264", f"Codec incorrect: {result.quality.codec}"
        assert result.quality.audio.lower() == "aac", f"Audio incorrect: {result.quality.audio}"
    
    def test_extract_language(self, extractor):
        """Test: Extraction de langue"""
        test_cases = [
            ("Movie VOSTFR.mkv", "VOSTFR"),
            ("Movie VF.mkv", "VF"),
            ("Movie MULTI.mkv", "MULTI"),
        ]
        
        for filename, expected_lang in test_cases:
            result = extractor.extract(filename)
            
            assert result.language == expected_lang, \
                f"Langue incorrecte pour {filename}: attendu {expected_lang}, obtenu {result.language}"
    
    def test_remove_noise_from_title(self, extractor):
        """Test: Suppression du bruit du titre"""
        filename = "Naruto [1080p] (2002) BluRay x264-GROUP.mkv"
        
        result = extractor.extract(filename)
        
        # Le titre devrait être propre
        assert result.title == "Naruto", f"Titre devrait être 'Naruto', obtenu: {result.title}"
        assert "[1080p]" not in result.title, "Tags devraient être supprimés"
        assert "BluRay" not in result.title, "Informations de qualité devraient être supprimées"
        assert "GROUP" not in result.title, "Groupe de release devrait être supprimé"
    
    def test_detect_series_vs_movie(self, extractor):
        """Test: Détection série vs film"""
        # Série
        series_filename = "Show S01E01.mkv"
        series_result = extractor.extract(series_filename)
        assert series_result.content_type == ContentType.SERIES, "Devrait détecter une série"
        
        # Film (pas de saison/épisode)
        movie_filename = "Movie (2020).mkv"
        movie_result = extractor.extract(movie_filename)
        assert movie_result.content_type == ContentType.MOVIE, "Devrait détecter un film"
    
    def test_confidence_score(self, extractor):
        """Test: Score de confiance"""
        # Nom bien structuré → haute confiance
        well_structured = "Naruto S01E01 (2002) [1080p].mkv"
        result1 = extractor.extract(well_structured)
        assert result1.extraction_confidence >= 0.7, \
            f"Confiance devrait être élevée pour nom structuré: {result1.extraction_confidence}"
        
        # Nom simple → confiance plus faible
        simple = "file.mkv"
        result2 = extractor.extract(simple)
        assert result2.extraction_confidence < result1.extraction_confidence, \
            "Confiance devrait être plus faible pour nom simple"
    
    def test_extract_tags(self, extractor):
        """Test: Extraction de tags"""
        filename = "Movie [Tag1] (Tag2) {Tag3}.mkv"
        
        result = extractor.extract(filename)
        
        assert len(result.tags) > 0, "Devrait extraire des tags"
        assert "Tag1" in result.tags, "Tag1 devrait être extrait"
    
    def test_batch_extraction(self, extractor):
        """Test: Extraction en batch"""
        filenames = [
            "Naruto S01E01.mkv",
            "Naruto S01E02.mkv",
            "One Piece S01E01.mkv",
        ]
        
        results = extractor.extract_batch(filenames)
        
        assert len(results) == 3, "Devrait extraire 3 structures"
        assert all(r.title for r in results), "Tous devraient avoir un titre"
    
    def test_is_sequel_or_variant(self, extractor):
        """Test: Détection de suites/variantes"""
        # Naruto vs Naruto Shippuden
        is_variant = extractor.is_sequel_or_variant("Naruto", "Naruto Shippuden")
        assert is_variant, "Naruto Shippuden devrait être détecté comme variante de Naruto"
        
        # Dragon Ball vs Dragon Ball Z
        is_variant2 = extractor.is_sequel_or_variant("Dragon Ball", "Dragon Ball GT")
        assert is_variant2, "Dragon Ball GT devrait être détecté comme variante"
        
        # Titres complètement différents
        is_variant3 = extractor.is_sequel_or_variant("Naruto", "One Piece")
        assert not is_variant3, "Titres différents ne devraient pas être variantes"
    
    def test_real_world_examples(self, extractor):
        """Test: Exemples réels du cahier des charges"""
        
        # Cas 1: juu-shiro, juushiro, juu shiro
        examples1 = [
            "juu-shiro.mkv",
            "juushiro.mkv",
            "juu shiro.mkv",
        ]
        results1 = extractor.extract_batch(examples1)
        # Les titres normalisés devraient être similaires
        titles1 = [r.title.lower().replace(" ", "").replace("-", "") for r in results1]
        assert len(set(titles1)) == 1, "Variantes orthographiques devraient avoir le même titre normalisé"
        
        # Cas 2: miss marvel, kiss-missmarvel, stream-miss-marvel
        examples2 = [
            "miss marvel.mkv",
            "kiss-missmarvel.mkv",
            "stream-miss-marvel.mkv",
        ]
        results2 = extractor.extract_batch(examples2)
        # Tous devraient contenir "miss" et "marvel"
        for result in results2:
            title_lower = result.title.lower()
            assert "miss" in title_lower or "marvel" in title_lower, \
                f"Titre devrait contenir 'miss' ou 'marvel': {result.title}"
        
        # Cas 3: naruto, naruto ep1, naruto 2001
        examples3 = [
            "naruto.mkv",
            "naruto ep1.mkv",
            "naruto 2001.mkv",
        ]
        results3 = extractor.extract_batch(examples3)
        # Tous devraient avoir "Naruto" comme titre
        for result in results3:
            assert "naruto" in result.title.lower(), f"Titre devrait contenir 'naruto': {result.title}"
        
        # Cas 4: one piece s01 vs one piece s02
        example4a = "one piece s01e01.mkv"
        example4b = "one piece s02e01.mkv"
        result4a = extractor.extract(example4a)
        result4b = extractor.extract(example4b)
        
        # Même titre
        assert result4a.title.lower() == result4b.title.lower(), "Devraient avoir le même titre"
        # Saisons différentes
        assert result4a.season.number != result4b.season.number, "Devraient avoir des saisons différentes"
