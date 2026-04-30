#!/bin/bash
# ============================================
# Lanceur pour Organisateur de Fichiers
# ============================================

echo ""
echo "========================================"
echo " Organisateur de Fichiers et Dossiers"
echo "========================================"
echo ""

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "[ERREUR] Python 3 n'est pas installé"
    echo ""
    echo "Installation :"
    echo "  - Ubuntu/Debian : sudo apt-get install python3 python3-tk"
    echo "  - macOS : brew install python-tk"
    echo ""
    exit 1
fi

echo "[OK] Python détecté"
python3 --version
echo ""

# Vérifier tkinter
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[AVERTISSEMENT] tkinter n'est pas installé"
    echo ""
    echo "Installation :"
    echo "  - Ubuntu/Debian : sudo apt-get install python3-tk"
    echo "  - macOS : brew install python-tk"
    echo ""
    read -p "Voulez-vous continuer quand même ? (o/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Oo]$ ]]; then
        exit 1
    fi
fi

# Lancer l'application
echo "Lancement de l'application..."
echo ""
python3 file_organizer.py

# Si l'application se ferme avec une erreur
if [ $? -ne 0 ]; then
    echo ""
    echo "[ERREUR] L'application s'est terminée avec une erreur"
    echo ""
    read -p "Appuyez sur Entrée pour continuer..."
fi
