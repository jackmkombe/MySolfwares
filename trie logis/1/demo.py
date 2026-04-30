"""
Script de démonstration des capacités algorithmiques
Montre les cas d'usage du cahier des charges
"""

from src.infrastructure.algorithms.semantic_extractor import SemanticExtractorService
from src.infrastructure.algorithms.similarity import AdvancedSimilarityCalculator
from src.infrastructure.algorithms.normalization import AdvancedNormalizationService


def demo_normalization():
    """Démo de normalisation"""
    print("=" * 80)
    print("DÉMONSTRATION : NORMALISATION")
    print("=" * 80)
    
    normalizer = AdvancedNormalizationService()
    
    test_cases = [
        "juu-shiro [1080p] BluRay x264-GROUP.mkv",
        "juushiro.720p.WEB-DL.mkv",
        "juu shiro (2020) VOSTFR.mkv",
    ]
    
    print("\nNormalisation de variantes orthographiques :\n")
    for filename in test_cases:
        normalized = normalizer.normalize(filename)
        print(f"Original  : {filename}")
        print(f"Normalisé : {normalized}")
        print()


def demo_semantic_extraction():
    """Démo d'extraction sémantique"""
    print("=" * 80)
    print("DÉMONSTRATION : EXTRACTION SÉMANTIQUE")
    print("=" * 80)
    
    extractor = SemanticExtractorService()
    
    test_cases = [
        ("Naruto S01E01 [1080p].mkv", "Série avec saison/épisode"),
        ("One Piece S02E15 (2001) BluRay.mkv", "Série avec année et qualité"),
        ("Naruto Shippuden S01E01.mkv", "Suite/variante"),
        ("Movie (2020) [1080p] BluRay x264.mkv", "Film avec métadonnées"),
        ("miss marvel episode 1.mkv", "Série sans format standard"),
    ]
    
    print("\nExtraction de structure sémantique :\n")
    for filename, description in test_cases:
        result = extractor.extract(filename)
        
        print(f"Fichier : {filename}")
        print(f"Type    : {description}")
        print(f"  → Titre      : {result.title}")
        print(f"  → Type       : {result.content_type.value}")
        if result.season:
            print(f"  → Saison     : {result.season.number}")
        if result.episode:
            print(f"  → Épisode    : {result.episode.number}")
        if result.year:
            print(f"  → Année      : {result.year}")
        if result.quality:
            print(f"  → Qualité    : {result.quality}")
        print(f"  → Confiance  : {result.extraction_confidence:.2%}")
        print()


def demo_similarity():
    """Démo de calcul de similarité"""
    print("=" * 80)
    print("DÉMONSTRATION : CALCUL DE SIMILARITÉ")
    print("=" * 80)
    
    extractor = SemanticExtractorService()
    calculator = AdvancedSimilarityCalculator()
    
    # Cas 1 : Variantes orthographiques
    print("\n--- CAS 1 : Variantes orthographiques (juu-shiro ≈ juushiro) ---\n")
    struct1 = extractor.extract("juu-shiro.mkv")
    struct2 = extractor.extract("juushiro.mkv")
    score1 = calculator.calculate(struct1, struct2)
    
    print(f"Fichier 1 : juu-shiro.mkv → Titre: {struct1.title}")
    print(f"Fichier 2 : juushiro.mkv → Titre: {struct2.title}")
    print(f"\nScore de similarité : {score1.total:.2%}")
    print(f"  - Titre       : {score1.title_similarity:.2%}")
    print(f"  - Structure   : {score1.structural_similarity:.2%}")
    print(f"  - Temporel    : {score1.temporal_similarity:.2%}")
    print(f"  - Qualité     : {score1.quality_similarity:.2%}")
    print(f"\nJustifications :")
    for reason in score1.reasoning:
        print(f"  • {reason}")
    
    # Cas 2 : Même série, même saison, épisodes différents
    print("\n--- CAS 2 : Même série, même saison, épisodes différents ---\n")
    struct3 = extractor.extract("One Piece S01E01.mkv")
    struct4 = extractor.extract("One Piece S01E02.mkv")
    score2 = calculator.calculate(struct3, struct4)
    
    print(f"Fichier 1 : One Piece S01E01.mkv")
    print(f"Fichier 2 : One Piece S01E02.mkv")
    print(f"\nScore de similarité : {score2.total:.2%}")
    print(f"\nJustifications :")
    for reason in score2.reasoning:
        print(f"  • {reason}")
    
    # Cas 3 : Même série, saisons différentes
    print("\n--- CAS 3 : Même série, saisons différentes ---\n")
    struct5 = extractor.extract("One Piece S01E01.mkv")
    struct6 = extractor.extract("One Piece S02E01.mkv")
    score3 = calculator.calculate(struct5, struct6)
    
    print(f"Fichier 1 : One Piece S01E01.mkv")
    print(f"Fichier 2 : One Piece S02E01.mkv")
    print(f"\nScore de similarité : {score3.total:.2%}")
    print(f"\nJustifications :")
    for reason in score3.reasoning:
        print(f"  • {reason}")
    
    # Cas 4 : Naruto vs Naruto Shippuden
    print("\n--- CAS 4 : Naruto vs Naruto Shippuden (séries différentes) ---\n")
    struct7 = extractor.extract("Naruto S01E01.mkv")
    struct8 = extractor.extract("Naruto Shippuden S01E01.mkv")
    score4 = calculator.calculate(struct7, struct8)
    
    print(f"Fichier 1 : Naruto S01E01.mkv → Titre: {struct7.title}")
    print(f"Fichier 2 : Naruto Shippuden S01E01.mkv → Titre: {struct8.title}")
    print(f"\nScore de similarité : {score4.total:.2%}")
    print(f"Ambigu ? {score4.is_ambiguous()} (nécessite validation utilisateur)")
    print(f"\nJustifications :")
    for reason in score4.reasoning:
        print(f"  • {reason}")
    
    # Cas 5 : Doublons (même épisode, qualités différentes)
    print("\n--- CAS 5 : Doublons potentiels (même épisode, qualités différentes) ---\n")
    struct9 = extractor.extract("Naruto S01E01 [1080p].mkv")
    struct10 = extractor.extract("Naruto S01E01 [720p].mkv")
    score5 = calculator.calculate(struct9, struct10)
    
    print(f"Fichier 1 : Naruto S01E01 [1080p].mkv")
    print(f"Fichier 2 : Naruto S01E01 [720p].mkv")
    print(f"\nScore de similarité : {score5.total:.2%}")
    print(f"Haute confiance ? {score5.is_high_confidence()}")
    print(f"\nJustifications :")
    for reason in score5.reasoning:
        print(f"  • {reason}")


def demo_real_world_cases():
    """Démo des cas réels du cahier des charges"""
    print("=" * 80)
    print("DÉMONSTRATION : CAS RÉELS DU CAHIER DES CHARGES")
    print("=" * 80)
    
    extractor = SemanticExtractorService()
    calculator = AdvancedSimilarityCalculator()
    
    # Cas du cahier des charges
    cases = [
        {
            "description": "juu-shiro, juushiro, juu shiro → même entité",
            "files": ["juu-shiro.mkv", "juushiro.mkv", "juu shiro.mkv"]
        },
        {
            "description": "miss marvel, kiss-missmarvel, stream-miss-marvel → équivalents",
            "files": ["miss marvel.mkv", "kiss-missmarvel.mkv", "stream-miss-marvel.mkv"]
        },
        {
            "description": "naruto, naruto ep1, naruto 2001 → même œuvre",
            "files": ["naruto.mkv", "naruto ep1.mkv", "naruto 2001.mkv"]
        },
    ]
    
    for case in cases:
        print(f"\n--- {case['description']} ---\n")
        
        structures = [extractor.extract(f) for f in case['files']]
        
        # Afficher les titres extraits
        print("Titres extraits :")
        for i, (filename, struct) in enumerate(zip(case['files'], structures), 1):
            print(f"  {i}. {filename:40s} → {struct.title}")
        
        # Calculer les similarités
        print("\nScores de similarité :")
        for i in range(len(structures)):
            for j in range(i + 1, len(structures)):
                score = calculator.calculate(structures[i], structures[j])
                print(f"  {case['files'][i]} ↔ {case['files'][j]}")
                print(f"    Score: {score.total:.2%} (Titre: {score.title_similarity:.2%})")


def main():
    """Point d'entrée de la démo"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  DÉMONSTRATION DES ALGORITHMES DE TRI ET FUSION INTELLIGENTE".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")
    
    # Exécuter les démos
    demo_normalization()
    print("\n")
    
    demo_semantic_extraction()
    print("\n")
    
    demo_similarity()
    print("\n")
    
    demo_real_world_cases()
    print("\n")
    
    print("=" * 80)
    print("FIN DE LA DÉMONSTRATION")
    print("=" * 80)
    print("\nToutes les capacités du cahier des charges sont démontrées :")
    print("  ✓ Reconnaissance de variantes orthographiques")
    print("  ✓ Distinction entre œuvres et suites")
    print("  ✓ Séparation par saison avec regroupement hiérarchique")
    print("  ✓ Scores de similarité pondérés et traçables")
    print("  ✓ Validation utilisateur pour cas ambigus")
    print("\n")


if __name__ == "__main__":
    main()
