"""
SmartSort - Test Suite Complet
Validation de tous les cas métier et règles de fusion
"""

import unittest
from pathlib import Path
from normalizer import Normalizer, NormalizedData
from merger import DirectoryMerger
from executor import MergeExecutor
import tempfile
import shutil


class TestNormalizer(unittest.TestCase):
    """Tests du moteur de normalisation"""
    
    def setUp(self):
        self.normalizer = Normalizer()
    
    def test_extraction_season(self):
        """Test extraction numéro de saison"""
        result = self.normalizer.preprocess("One Piece S01")
        self.assertEqual(result.season, 1)
        
        result = self.normalizer.preprocess("Naruto s12")
        self.assertEqual(result.season, 12)
    
    def test_extraction_episode(self):
        """Test extraction numéro d'épisode"""
        result = self.normalizer.preprocess("Naruto ep 01")
        self.assertEqual(result.episode, 1)
        
        result = self.normalizer.preprocess("One Piece E123")
        self.assertEqual(result.episode, 123)
    
    def test_extraction_year(self):
        """Test extraction année"""
        result = self.normalizer.preprocess("Naruto 2002")
        self.assertEqual(result.year, 2002)
        
        result = self.normalizer.preprocess("Naruto 2022")
        self.assertEqual(result.year, 2022)
    
    def test_extraction_resolution(self):
        """Test extraction résolution"""
        result = self.normalizer.preprocess("Movie 4k BluRay")
        self.assertEqual(result.resolution, "4k")
        
        result = self.normalizer.preprocess("Series 1080p WEB-DL")
        self.assertEqual(result.resolution, "1080p")
    
    def test_noise_removal(self):
        """Test suppression des termes de bruit"""
        result = self.normalizer.preprocess("Movie.2020.1080p.BluRay.x264.DTS")
        self.assertNotIn("1080p", result.root_name)
        self.assertNotIn("bluray", result.root_name)
        self.assertNotIn("x264", result.root_name)
    
    def test_canonicalization(self):
        """Test canonicalisation (lowercase, espaces)"""
        result = self.normalizer.preprocess("One.Piece.S01E01")
        self.assertEqual(result.root_name, "one piece")
        
        result = self.normalizer.preprocess("Miss_Marvel-2022")
        self.assertEqual(result.root_name, "miss marvel")
    
    def test_dkb_prefix_removal(self):
        """BAN TEST 1 : [DKB] juu-shiro + juushiro"""
        result1 = self.normalizer.preprocess("[DKB] juu-shiro")
        result2 = self.normalizer.preprocess("juushiro")
        
        # Les deux doivent être similaires après normalisation
        self.assertIn("juu", result1.root_name)
        self.assertIn("juu", result2.root_name)


class TestMerger(unittest.TestCase):
    """Tests du moteur de clustering et fusion"""
    
    def setUp(self):
        self.normalizer = Normalizer()
        self.merger = DirectoryMerger(self.normalizer)
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_ban_01_dkb_juushiro_fusion(self):
        """BAN TEST 1 : [DKB] juu-shiro + juushiro -> Fusion"""
        # Crée les répertoires de test
        (self.temp_dir / "[DKB] juu-shiro").mkdir()
        (self.temp_dir / "juushiro").mkdir()
        
        actions = self.merger.analyze_directories(self.temp_dir)
        
        # Doit proposer une fusion
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0].action_type, 'merge')
        self.assertEqual(len(actions[0].source_paths), 2)
    
    def test_ban_02_one_piece_seasons_hierarchy(self):
        """BAN TEST 2 : One Piece S01 + S02 -> Hiérarchie"""
        (self.temp_dir / "One Piece S01").mkdir()
        (self.temp_dir / "One Piece S02").mkdir()
        
        actions = self.merger.analyze_directories(self.temp_dir)
        
        # Doit proposer une hiérarchie
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0].action_type, 'hierarchy')
        self.assertIn("one piece", actions[0].destination_path.name.lower())
    
    def test_ban_03_naruto_years_separation(self):
        """BAN TEST 3 : Naruto 2002 + Naruto 2022 -> Séparés"""
        (self.temp_dir / "Naruto 2002").mkdir()
        (self.temp_dir / "Naruto 2022").mkdir()
        
        actions = self.merger.analyze_directories(self.temp_dir)
        
        # Ne doit PAS proposer de fusion (années trop éloignées)
        # Ou si fusion, doit être séparée
        if actions:
            # Vérifie qu'il n'y a pas de fusion des deux
            for action in actions:
                years = set()
                for path in action.source_paths:
                    norm = self.normalizer.preprocess(path.name)
                    if norm.year:
                        years.add(norm.year)
                
                # Si plusieurs années, elles doivent être proches
                if len(years) > 1:
                    year_list = sorted(years)
                    for i in range(len(year_list) - 1):
                        self.assertLessEqual(
                            abs(year_list[i+1] - year_list[i]), 
                            2,
                            "Années trop éloignées fusionnées"
                        )
    
    def test_ban_04_miss_marvel_inversion(self):
        """BAN TEST 4 : Kiss-Miss-Marvel + Miss Marvel -> Fusion"""
        (self.temp_dir / "Kiss-Miss-Marvel").mkdir()
        (self.temp_dir / "Miss Marvel").mkdir()
        
        actions = self.merger.analyze_directories(self.temp_dir)
        
        # Doit proposer une fusion (mots clés identiques)
        self.assertGreaterEqual(len(actions), 1)
        # Vérifie que les deux sont dans la même action
        if actions:
            sources = [p.name for p in actions[0].source_paths]
            self.assertEqual(len(sources), 2)
    
    def test_ban_05_naruto_episode_to_season(self):
        """BAN TEST 5 : Naruto S01 + Naruto ep 01 -> Fusion"""
        (self.temp_dir / "Naruto S01").mkdir()
        (self.temp_dir / "Naruto ep 01").mkdir()
        
        actions = self.merger.analyze_directories(self.temp_dir)
        
        # Doit proposer une fusion ou hiérarchie
        self.assertGreaterEqual(len(actions), 1)
    
    def test_fuzzy_matching_threshold(self):
        """Test seuil de similarité fuzzy (92%)"""
        (self.temp_dir / "One Piece").mkdir()
        (self.temp_dir / "One Pice").mkdir()  # Typo (>92% similarity)
        
        actions = self.merger.analyze_directories(self.temp_dir)
        
        # Doit proposer une fusion (similarité > 92%)
        self.assertEqual(len(actions), 1)
    
    def test_no_merge_different_series(self):
        """Test non-fusion de séries différentes"""
        (self.temp_dir / "Naruto").mkdir()
        (self.temp_dir / "One Piece").mkdir()
        
        actions = self.merger.analyze_directories(self.temp_dir)
        
        # Ne doit PAS proposer de fusion
        self.assertEqual(len(actions), 0)


class TestExecutor(unittest.TestCase):
    """Tests du moteur d'exécution"""
    
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.executor = MergeExecutor()
    
    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_conflict_resolution_incremental(self):
        """Test résolution de conflits par renommage incrémental"""
        # Crée un fichier existant
        dest_dir = self.temp_dir / "destination"
        dest_dir.mkdir()
        (dest_dir / "file.txt").write_text("original")
        
        # Teste la résolution de conflit
        target = dest_dir / "file.txt"
        resolved = self.executor._resolve_conflict(target)
        
        self.assertEqual(resolved.name, "file_1.txt")
        
        # Crée file_1.txt et teste à nouveau
        resolved.write_text("conflict")
        resolved2 = self.executor._resolve_conflict(target)
        self.assertEqual(resolved2.name, "file_2.txt")
    
    def test_empty_directory_removal(self):
        """Test suppression des répertoires vides"""
        empty_dir = self.temp_dir / "empty"
        empty_dir.mkdir()
        
        self.executor._remove_empty_dirs(empty_dir)
        
        self.assertFalse(empty_dir.exists())
    
    def test_merge_execution_basic(self):
        """Test exécution basique de fusion"""
        # Crée des répertoires sources avec fichiers
        source1 = self.temp_dir / "source1"
        source2 = self.temp_dir / "source2"
        source1.mkdir()
        source2.mkdir()
        
        (source1 / "file1.txt").write_text("content1")
        (source2 / "file2.txt").write_text("content2")
        
        # Crée une action de fusion
        from merger import MergeAction
        action = MergeAction(
            source_paths=[source1, source2],
            destination_path=self.temp_dir / "merged",
            action_type='merge',
            reason='Test'
        )
        
        # Exécute
        results = self.executor.execute_actions([action])
        
        # Vérifie
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].success)
        self.assertEqual(results[0].files_moved, 2)
        
        # Vérifie que les fichiers sont bien déplacés
        merged_dir = self.temp_dir / "merged"
        self.assertTrue((merged_dir / "file1.txt").exists())
        self.assertTrue((merged_dir / "file2.txt").exists())


class TestIntegration(unittest.TestCase):
    """Tests d'intégration complets"""
    
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.normalizer = Normalizer()
        self.merger = DirectoryMerger(self.normalizer)
        self.executor = MergeExecutor()
    
    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_full_workflow_merge(self):
        """Test workflow complet : Analyse -> Fusion -> Exécution"""
        # Crée des répertoires similaires avec fichiers
        dir1 = self.temp_dir / "One.Piece.S01.1080p"
        dir2 = self.temp_dir / "One_Piece_S01_BluRay"
        dir1.mkdir()
        dir2.mkdir()
        
        (dir1 / "episode1.mkv").write_text("video1")
        (dir2 / "episode2.mkv").write_text("video2")
        
        # Analyse
        actions = self.merger.analyze_directories(self.temp_dir)
        self.assertGreater(len(actions), 0)
        
        # Exécution
        results = self.executor.execute_actions(actions)
        self.assertTrue(all(r.success for r in results))
        
        # Vérifie que les fichiers sont fusionnés
        merged_dirs = [d for d in self.temp_dir.iterdir() if d.is_dir()]
        self.assertEqual(len(merged_dirs), 1)
        
        merged_files = list(merged_dirs[0].rglob("*.mkv"))
        self.assertEqual(len(merged_files), 2)
    
    def test_full_workflow_hierarchy(self):
        """Test workflow complet avec création de hiérarchie"""
        # Crée plusieurs saisons
        (self.temp_dir / "Naruto S01").mkdir()
        (self.temp_dir / "Naruto S02").mkdir()
        (self.temp_dir / "Naruto S03").mkdir()
        
        for season in [1, 2, 3]:
            season_dir = self.temp_dir / f"Naruto S{season:02d}"
            (season_dir / f"ep{season}.mkv").write_text(f"season{season}")
        
        # Analyse
        actions = self.merger.analyze_directories(self.temp_dir)
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0].action_type, 'hierarchy')
        
        # Exécution
        results = self.executor.execute_actions(actions)
        self.assertTrue(results[0].success)
        
        # Vérifie la structure
        naruto_dir = self.temp_dir / "Naruto"
        self.assertTrue(naruto_dir.exists())
        
        season_dirs = [d for d in naruto_dir.iterdir() if d.is_dir()]
        self.assertEqual(len(season_dirs), 3)


def run_tests():
    """Exécute tous les tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Ajoute tous les tests
    suite.addTests(loader.loadTestsFromTestCase(TestNormalizer))
    suite.addTests(loader.loadTestsFromTestCase(TestMerger))
    suite.addTests(loader.loadTestsFromTestCase(TestExecutor))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Exécute avec verbosité
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Résumé
    print("\n" + "="*70)
    print("RÉSUMÉ DES TESTS")
    print("="*70)
    print(f"✅ Tests réussis : {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Tests échoués : {len(result.failures)}")
    print(f"⚠️  Erreurs : {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
