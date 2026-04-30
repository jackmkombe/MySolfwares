"""
MediaNexus PRO v3.0 - Module de Matching Intelligent
Algorithme de correspondance composite avec scoring multi-critères.
"""
import re
from pathlib import Path
from difflib import SequenceMatcher
from typing import List, Dict, Tuple, Optional

class MatchingEngine:
    """
    Moteur de correspondance intelligent.
    Utilise un scoring composite basé sur titre, année et type.
    """

    # Patterns de bruit à nettoyer
    NOISE_PATTERNS = [
        r'\[.*?\]',           # [Groupe]
        r'\(.*?\)',           # (Info)
        r'\.(1080p|720p|480p|2160p|4K|UHD)',
        r'\.(BluRay|WEB-DL|WEBRip|HDTV|DVDRip|BRRip|HDRip)',
        r'\.(x264|x265|H264|H265|HEVC|AVC)',
        r'\.(AAC|AC3|DTS|MP3|FLAC)',
        r'[-_](VOSTFR|VOSTA|VF|VO|MULTI|FRENCH|TRUEFRENCH)',
        r'\.S\d{2}E\d{2}',    # S01E01
        r'\.S\d{2}',          # S01
        r'\.E\d{2,3}',        # E01
        r'-\w+$',             # -SPARKS
        r'\.PROPER|\.REPACK|\.INTERNAL',
        r'\.COMPLETE',
        r'\.EXTENDED|\.UNRATED|\.DIRECTORS\.CUT',
    ]

    NOISE_WORDS = {
        'bluray', 'bdrip', 'webrip', 'hdtv', 'dvdrip', 
        'x264', 'x265', 'hevc', 'aac', 'dts',
        'vostfr', 'french', 'multi', 'truefrench',
        'complete', 'extended', 'unrated', 'repack', 'proper'
    }

    @classmethod
    def clean_title(cls, raw_name: str) -> Tuple[str, Optional[int]]:
        """
        Nettoie un nom de fichier et extrait l'année potentielle.
        
        Returns:
            Tuple[str, Optional[int]]: (titre nettoyé, année si trouvée)
        """
        name = Path(raw_name).stem

        # Extraction de l'année avant nettoyage (pattern 19xx ou 20xx)
        year_match = re.search(r'\b(19|20)\d{2}\b', name)
        year = int(year_match.group(0)) if year_match else None

        # Application des patterns de nettoyage
        for pattern in cls.NOISE_PATTERNS:
            name = re.sub(pattern, ' ', name, flags=re.IGNORECASE)

        # Remplacement des séparateurs
        name = re.sub(r'[._-]+', ' ', name)

        # Filtrage des mots de bruit
        words = name.split()
        filtered = [w for w in words if w.lower() not in cls.NOISE_WORDS]

        # Reconstruction du titre
        clean = ' '.join(filtered).strip()

        # Si le nettoyage a tout supprimé, on garde les 3 premiers mots
        if not clean and words:
            clean = ' '.join(words[:3])

        return clean, year

    @classmethod
    def calculate_title_similarity(cls, source: str, target: str) -> float:
        """
        Calcule la similarité entre deux titres.
        Combine ratio de séquence et correspondance de tokens.
        """
        if not source or not target:
            return 0.0

        source_lower = source.lower()
        target_lower = target.lower()

        # Ratio de séquence (difflib)
        seq_ratio = SequenceMatcher(None, source_lower, target_lower).ratio()

        # Correspondance de tokens (Jaccard)
        source_tokens = set(source_lower.split())
        target_tokens = set(target_lower.split())
        
        if source_tokens and target_tokens:
            intersection = len(source_tokens & target_tokens)
            union = len(source_tokens | target_tokens)
            jaccard = intersection / union if union > 0 else 0.0
        else:
            jaccard = 0.0

        # Score combiné (60% séquence, 40% Jaccard)
        return (seq_ratio * 0.6) + (jaccard * 0.4)

    @classmethod
    def calculate_match_score(cls, query_title: str, query_year: Optional[int],
                               result: Dict, media_type: str) -> float:
        """
        Calcule un score de confiance composite pour un résultat API.
        
        Facteurs pondérés:
        - Similarité du titre: 60%
        - Correspondance de l'année: 25%
        - Cohérence du type: 15%
        """
        score = 0.0

        # 1. Similarité du titre (60%)
        result_title = result.get('title') or result.get('name', '')
        title_sim = cls.calculate_title_similarity(query_title, result_title)
        score += title_sim * 0.60

        # 2. Correspondance de l'année (25%)
        if query_year:
            result_date = result.get('release_date') or result.get('first_air_date') or ''
            if result_date:
                try:
                    result_year = int(result_date[:4])
                    year_diff = abs(query_year - result_year)
                    if year_diff == 0:
                        year_score = 1.0
                    elif year_diff == 1:
                        year_score = 0.8
                    elif year_diff <= 3:
                        year_score = 0.5
                    else:
                        year_score = 0.0
                    score += year_score * 0.25
                except ValueError:
                    pass

        # 3. Cohérence du type (15%)
        result_type = result.get('media_type', '')
        type_match = 0.0
        
        if media_type == "Films / Séries":
            if result_type in ('movie', 'tv'):
                type_match = 1.0
        elif media_type == "Animés":
            # Pour Jikan, on assume que c'est toujours un animé
            type_match = 1.0
        elif media_type == "Jeux PC":
            type_match = 1.0  # RAWG = toujours jeux
        
        score += type_match * 0.15

        return round(score, 3)

    @classmethod
    def select_best_match(cls, query_title: str, query_year: Optional[int],
                          candidates: List[Dict], media_type: str,
                          threshold: float = 0.65) -> Tuple[Optional[Dict], float]:
        """
        Sélectionne le meilleur candidat parmi une liste de résultats API.
        
        Returns:
            Tuple[Optional[Dict], float]: (meilleur résultat, score) ou (None, 0.0)
        """
        if not candidates:
            return None, 0.0

        scored_candidates = []
        for candidate in candidates:
            score = cls.calculate_match_score(query_title, query_year, candidate, media_type)
            scored_candidates.append((candidate, score))

        # Tri par score décroissant
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        best, best_score = scored_candidates[0]

        # Vérification du seuil de confiance
        if best_score >= threshold:
            return best, best_score
        else:
            return None, best_score

    @classmethod
    def is_duplicate(cls, title_a: str, title_b: str, threshold: float = 0.85) -> bool:
        """
        Vérifie si deux titres sont des doublons probables.
        """
        similarity = cls.calculate_title_similarity(title_a, title_b)
        return similarity >= threshold
