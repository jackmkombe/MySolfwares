# 🧪 Script de Test - Générateur de Fichiers d'Exemple

"""
Ce script crée un ensemble de fichiers de test pour démontrer
les capacités de l'organisateur de fichiers.
"""

import os
from pathlib import Path


def create_test_files():
    """Crée une structure de fichiers de test."""
    
    # Créer le dossier de test
    test_folder = Path("test_files")
    test_folder.mkdir(exist_ok=True)
    
    print(f"📁 Création du dossier de test: {test_folder.absolute()}")
    
    # Scénario 1: Films avec tags entre crochets
    films = [
        "[DKB] Film Action.mp4",
        "[DKB] Film Action - Part2.mp4",
        "[XYZ] Film Action HD.mp4",
        "[ABC] Film Comedie.mp4",
        "[ABC] Film Comedie 2.mp4",
        "[DKB] Film Horreur.mkv",
        "[XYZ] Film Horreur Directors Cut.mkv",
    ]
    
    # Scénario 2: Photos avec numéros
    photos = [
        "Vacances_2024_001.jpg",
        "Vacances_2024_002.jpg",
        "Vacances_2024_003.jpg",
        "Travail_rapport_01.jpg",
        "Travail_rapport_02.jpg",
        "Famille_noel_001.png",
        "Famille_noel_002.png",
    ]
    
    # Scénario 3: Documents avec versions
    documents = [
        "Rapport_v1.0.pdf",
        "Rapport_v1.1.pdf",
        "Rapport_v2.0.pdf",
        "Contrat_v1.docx",
        "Contrat_v2.docx",
        "Presentation_final.pptx",
        "Presentation_final_v2.pptx",
    ]
    
    # Scénario 4: Musique avec artiste
    music = [
        "Artist1 - Song Title.mp3",
        "Artist1 - Song Title (Remix).mp3",
        "Artist1 - Song Title Live.mp3",
        "Artist2 - Another Song.mp3",
        "Artist2 - Another Song Acoustic.mp3",
    ]
    
    # Scénario 5: Fichiers divers
    misc = [
        "backup_2024-01-01.zip",
        "backup_2024-01-02.zip",
        "backup_2024-01-03.zip",
        "project_code.py",
        "project_code_v2.py",
        "notes.txt",
        "notes_important.txt",
    ]
    
    all_files = films + photos + documents + music + misc
    
    # Créer tous les fichiers
    for filename in all_files:
        filepath = test_folder / filename
        filepath.touch()
        print(f"✓ Créé: {filename}")
    
    print(f"\n✅ {len(all_files)} fichiers de test créés avec succès!")
    print(f"\n📍 Chemin: {test_folder.absolute()}")
    print("\n" + "="*60)
    print("SUGGESTIONS DE TEST:")
    print("="*60)
    
    print("\n🎬 Test 1: Films avec tags")
    print("   Motif à ignorer: \\[.*?\\]")
    print("   Seuil: 0.7")
    print("   Type: videos")
    
    print("\n📸 Test 2: Photos numérotées")
    print("   Motif à ignorer: _\\d+")
    print("   Seuil: 0.8")
    print("   Type: images")
    
    print("\n📄 Test 3: Documents versionnés")
    print("   Motif à ignorer: _v\\d+\\.\\d+")
    print("   Seuil: 0.7")
    print("   Type: documents")
    
    print("\n🎵 Test 4: Musique")
    print("   Motif à ignorer: \\(.*?\\)")
    print("   Seuil: 0.6")
    print("   Type: audio")
    
    print("\n📦 Test 5: Tous les fichiers")
    print("   Motif à ignorer: _\\d{4}-\\d{2}-\\d{2}")
    print("   Seuil: 0.7")
    print("   Type: all")
    
    print("\n" + "="*60)
    print("Lancez file_organizer.py et sélectionnez le dossier 'test_files'")
    print("="*60)


def create_test_folders():
    """Crée une structure de dossiers de test."""
    
    test_folder = Path("test_folders")
    test_folder.mkdir(exist_ok=True)
    
    print(f"\n📁 Création du dossier de test pour dossiers: {test_folder.absolute()}")
    
    folders = [
        "Projet_Client_A_2024",
        "Projet_Client_A_2025",
        "Projet_Client_B_v1",
        "Projet_Client_B_v2",
        "Backup_Database_01",
        "Backup_Database_02",
        "Photos_Vacances_Ete",
        "Photos_Vacances_Hiver",
        "[Archive] Documents_Anciens",
        "[Archive] Documents_Anciens_2",
    ]
    
    for folder_name in folders:
        folder_path = test_folder / folder_name
        folder_path.mkdir(exist_ok=True)
        # Créer un fichier vide dedans pour que le dossier ne soit pas vide
        (folder_path / "readme.txt").touch()
        print(f"✓ Créé: {folder_name}/")
    
    print(f"\n✅ {len(folders)} dossiers de test créés avec succès!")
    print(f"\n📍 Chemin: {test_folder.absolute()}")
    print("\n" + "="*60)
    print("SUGGESTIONS DE TEST POUR DOSSIERS:")
    print("="*60)
    
    print("\n📂 Test 1: Projets clients")
    print("   Motif à ignorer: _\\d{4}")
    print("   Seuil: 0.7")
    
    print("\n📂 Test 2: Versions")
    print("   Motif à ignorer: _v\\d+")
    print("   Seuil: 0.8")
    
    print("\n📂 Test 3: Archives")
    print("   Motif à ignorer: \\[.*?\\]")
    print("   Seuil: 0.7")


if __name__ == "__main__":
    print("🚀 Générateur de Fichiers de Test")
    print("="*60)
    
    create_test_files()
    print("\n")
    create_test_folders()
    
    print("\n\n🎉 Tous les fichiers de test sont prêts!")
    print("Vous pouvez maintenant tester l'application file_organizer.py")
