# 🚀 GUIDE DE DÉMARRAGE RAPIDE - VERSION 2.1

## ⚡ Lancement Rapide

### Windows PowerShell

```powershell
# Lancer l'application moderne
python file_organizer_modern.py

# Créer un exécutable
python build_exe.py

# Créer des fichiers de test
python create_test_files.py
```

### Windows CMD

```cmd
python file_organizer_modern.py
```

### Avec les lanceurs

```powershell
# Double-cliquez sur lancer.bat
# OU
.\lancer.bat
```

---

## 🎯 Test Rapide (2 minutes)

### 1. Créer des fichiers de test

```powershell
python create_test_files.py
```

Cela crée :

- `test_files/` avec 32 fichiers variés
- `test_folders/` avec 10 dossiers

### 2. Lancer l'application

```powershell
python file_organizer_modern.py
```

### 3. Configuration rapide

1. **Dossier source** : Cliquez "Parcourir" → Sélectionnez `test_files`
2. **Type de tri** : Sélectionnez **📦 Les deux** ⭐
3. **Raccourci** : Cliquez sur **"Crochets [...]"**
4. **Prévisualiser** : Cliquez sur **🔍 Prévisualiser**
5. **Organiser** : Cliquez sur **▶️ Organiser les Fichiers**

✅ **Résultat** : Vos fichiers sont organisés !

---

## 🌟 Nouvelles Fonctionnalités v2.1

### 1. Option "Les deux" 📦

**Triez fichiers ET dossiers en même temps !**

Avant :

- ❌ Trier les fichiers → 1ère passe
- ❌ Trier les dossiers → 2ème passe

Maintenant :

- ✅ Sélectionner "Les deux" → **1 seule passe !**

### 2. Dossiers Réutilisés 🔄

**Ne recrée plus les dossiers existants !**

Logs :

```
📁 Film Action (nouveau dossier créé)
📁 Film Comedie (dossier existant réutilisé) ⭐
```

### 3. Noms Propres 🏷️

**Les règles d'ignorance s'appliquent aux noms de dossiers !**

Exemple :

```
Fichiers : [DKB] Film.mp4
Motif : \[.*?\]

AVANT : 📁 [DKB] Film/
MAINTENANT : 📁 Film/ ⭐
```

---

## 📦 Créer un Exécutable

### Méthode Automatique (Recommandée)

```powershell
python build_exe.py
```

Le script :

1. ✅ Installe PyInstaller automatiquement
2. ✅ Vous demande quelle version compiler
3. ✅ Crée l'exe dans `dist/`
4. ✅ Nettoie les fichiers temporaires

### Méthode Manuelle

```powershell
# Installer PyInstaller
pip install pyinstaller

# Créer l'exe (version moderne)
pyinstaller --onefile --windowed --name="Organisateur_Fichiers_Modern" file_organizer_modern.py
```

Votre exe sera dans `dist/Organisateur_Fichiers_Modern.exe`

---

## 🎨 Raccourcis Rapides

### Motifs Prédéfinis

Cliquez directement sur ces boutons :

| Bouton                | Motif          | Exemple                |
| --------------------- | -------------- | ---------------------- |
| **Crochets [...]**    | `\[.*?\]`      | `[DKB] Film` → `Film`  |
| **Parenthèses (...)** | `\(.*?\)`      | `Film (2024)` → `Film` |
| **Numéros \_123**     | `_\d+`         | `Photo_001` → `Photo`  |
| **Années**            | `\d{4}`        | `Film2024` → `Film`    |
| **Versions**          | `_v\d+\.\d+`   | `App_v1.0` → `App`     |
| **Copies**            | `_COPY\|_copy` | `File_COPY` → `File`   |

---

## 💡 Astuces Pro

### Astuce 1 : Combiner les Motifs

Ajoutez plusieurs motifs pour un nettoyage complet :

```
1. Cliquez "Crochets [...]"
2. Cliquez "Numéros _123"
3. Cliquez "Années"

Résultat : [DKB] Film_2024_001.mp4 → Film/
```

### Astuce 2 : Ajuster le Seuil

- **0.9-1.0** : Très strict (noms quasi identiques)
- **0.7-0.8** : Recommandé ⭐
- **0.5-0.6** : Permissif
- **0.0-0.4** : Très permissif

### Astuce 3 : Toujours Prévisualiser

Avant d'organiser, cliquez **🔍 Prévisualiser** pour :

- ✅ Voir les groupes qui seront créés
- ✅ Vérifier les noms de dossiers
- ✅ Ajuster si nécessaire

---

## 🐛 Dépannage Rapide

### Problème : "python n'est pas reconnu"

**Solution** : Installez Python depuis https://www.python.org/downloads/

### Problème : "tkinter not found"

**Solution** :

```powershell
pip install tk
```

### Problème : "Aucun regroupement possible"

**Solution** : Réduisez le seuil de similarité (ex: 0.5)

### Problème : L'exe est trop gros

**Solution** : C'est normal (~10-15 MB), il inclut Python

---

## 📚 Documentation Complète

| Fichier                  | Description                  |
| ------------------------ | ---------------------------- |
| **FINAL_v2.1.md**        | Résumé complet v2.1 ⭐       |
| **IMPROVEMENTS_v2.1.md** | Détails des améliorations ⭐ |
| **START_HERE.md**        | Point de départ              |
| **QUICKSTART.md**        | Guide rapide                 |
| **README.md**            | Documentation complète       |
| **PACKAGING.md**         | Guide de packaging           |

---

## ✅ Checklist

### Première Utilisation

- [ ] Lancer `python file_organizer_modern.py`
- [ ] Tester l'option "Les deux" 📦
- [ ] Essayer les raccourcis rapides
- [ ] Vérifier la prévisualisation
- [ ] Organiser les fichiers de test

### Avant Production

- [ ] Tester avec une copie de vos fichiers
- [ ] Ajuster le seuil de similarité
- [ ] Vérifier les noms de dossiers créés
- [ ] Confirmer la réutilisation des dossiers

### Pour Distribution

- [ ] Exécuter `python build_exe.py`
- [ ] Tester l'exe sur une autre machine
- [ ] Partager avec vos collègues

---

## 🎉 Vous êtes Prêt !

L'application est **100% fonctionnelle** avec :

- ✅ Interface moderne
- ✅ Tri simultané fichiers + dossiers
- ✅ Noms de dossiers propres
- ✅ Réutilisation intelligente
- ✅ Raccourcis rapides
- ✅ Documentation complète

**Bon tri ! 🚀**

---

**Version** : 2.1.0  
**Date** : 2026-01-01  
**Statut** : Production Ready ✅
