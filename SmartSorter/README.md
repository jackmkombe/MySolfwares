# 🗂️ Organisateur de Fichiers et Dossiers

Application desktop Python complète pour le tri automatique de fichiers et dossiers par similarité de noms.

## 📋 Fonctionnalités

### ✨ Principales

- **Tri de fichiers ou dossiers** : Choisissez ce que vous souhaitez organiser
- **Filtrage par type** : Images, vidéos, documents, audio ou tous types
- **Règles d'ignorance personnalisées** : Utilisez des regex pour ignorer des motifs dans les noms
- **Seuil de similarité ajustable** : Contrôlez la précision du regroupement (0.0 à 1.0)
- **Destination flexible** : Dossier source ou destination personnalisée
- **Prévisualisation** : Visualisez les groupes avant de déplacer les fichiers
- **Logs détaillés** : Suivez toutes les opérations en temps réel

### 🎯 Cas d'usage

**Exemple 1 : Films avec tags**

```
Avant :
  [DKB] Film Action.mp4
  [DKB] Film Action - Part2.mp4
  [XYZ] Film Action HD.mp4

Règle d'ignorance : \[.*?\]

Après :
  📁 Film Action/
     ├─ [DKB] Film Action.mp4
     ├─ [DKB] Film Action - Part2.mp4
     └─ [XYZ] Film Action HD.mp4
```

**Exemple 2 : Photos de vacances**

```
Avant :
  Vacances_2024_001.jpg
  Vacances_2024_002.jpg
  Vacances_2024_003.jpg
  Travail_rapport_01.jpg

Règle d'ignorance : _\d+

Après :
  📁 Vacances/
     ├─ Vacances_2024_001.jpg
     ├─ Vacances_2024_002.jpg
     └─ Vacances_2024_003.jpg
  📁 Travail rapport/
     └─ Travail_rapport_01.jpg
```

## 🚀 Installation et Lancement

### Prérequis

- Python 3.7 ou supérieur
- Tkinter (inclus par défaut avec Python)

### Lancement

```bash
python file_organizer.py
```

**C'est tout !** Aucune dépendance externe n'est requise.

## 📖 Guide d'utilisation

### 1️⃣ Sélection du dossier source

Cliquez sur **"Parcourir..."** et sélectionnez le dossier contenant les fichiers/dossiers à trier.

### 2️⃣ Choix du type de tri

- **Trier des fichiers** : Pour organiser les fichiers
- **Trier des dossiers** : Pour organiser les sous-dossiers

### 3️⃣ Filtrage (pour les fichiers uniquement)

Sélectionnez le type de fichiers à inclure :

- **all** : Tous les fichiers
- **images** : .jpg, .png, .gif, .bmp, .svg, .webp, etc.
- **videos** : .mp4, .avi, .mkv, .mov, .wmv, etc.
- **documents** : .pdf, .doc, .docx, .txt, .xls, .ppt, etc.
- **audio** : .mp3, .wav, .flac, .aac, .ogg, etc.

### 4️⃣ Règles d'ignorance (optionnel)

Définissez des motifs regex à ignorer dans les noms :

| Motif      | Description                   | Exemple                              |
| ---------- | ----------------------------- | ------------------------------------ |
| `\[.*?\]`  | Ignore tout entre crochets    | `[DKB] Film.mp4` → `Film`            |
| `\(.*?\)`  | Ignore tout entre parenthèses | `Film (2024).mp4` → `Film`           |
| `_COPY`    | Ignore le texte "\_COPY"      | `Document_COPY.pdf` → `Document.pdf` |
| `\d{4}`    | Ignore 4 chiffres consécutifs | `Photo2024.jpg` → `Photo.jpg`        |
| `^prefix_` | Ignore "prefix\_" en début    | `prefix_file.txt` → `file.txt`       |

**Ajout d'un motif :**

1. Entrez le motif dans le champ
2. Cliquez sur **"Ajouter"**
3. Le motif apparaît dans la liste

### 5️⃣ Seuil de similarité

Ajustez le curseur entre 0.0 et 1.0 :

- **0.7 - 0.8** : Recommandé pour la plupart des cas
- **0.5 - 0.6** : Regroupement plus permissif
- **0.9 - 1.0** : Regroupement très strict (noms quasi identiques)

### 6️⃣ Destination

**Option 1 : Dossier source (par défaut)**
Les groupes sont créés dans le dossier source.

**Option 2 : Destination personnalisée**

1. Cochez **"Utiliser un dossier de destination personnalisé"**
2. Sélectionnez le dossier de destination
3. Les groupes seront créés dans ce dossier

### 7️⃣ Exécution

**Prévisualisation (recommandé) :**

1. Cliquez sur **"🔍 Prévisualiser"**
2. Consultez les logs pour voir les groupes qui seront créés
3. Ajustez les paramètres si nécessaire

**Organisation :**

1. Cliquez sur **"▶️ Organiser les Fichiers"**
2. Confirmez l'opération
3. Suivez la progression dans les logs

## 🛡️ Sécurité

- **Confirmation requise** : L'application demande confirmation avant tout déplacement
- **Gestion des conflits** : Les fichiers en conflit sont renommés automatiquement (ex: `file_1.txt`)
- **Logs détaillés** : Toutes les opérations sont tracées
- **Pas de suppression** : L'application déplace uniquement, ne supprime jamais

## 🎨 Interface

L'application dispose d'une interface graphique moderne avec :

- ✅ Sections organisées et étiquetées
- ✅ Aide contextuelle pour chaque fonctionnalité
- ✅ Logs colorés (info, succès, avertissement, erreur)
- ✅ Validation des entrées utilisateur
- ✅ Messages d'erreur explicites

## 🔧 Architecture du code

```
file_organizer.py
├─ FileOrganizerApp (classe principale)
│  ├─ __init__() : Initialisation
│  ├─ _setup_ui() : Construction de l'interface
│  ├─ _create_*_section() : Création des sections UI
│  ├─ _get_items_to_process() : Récupération des éléments
│  ├─ _clean_name() : Application des règles d'ignorance
│  ├─ _calculate_similarity() : Calcul de similarité
│  ├─ _group_items() : Algorithme de regroupement
│  ├─ _preview_organization() : Prévisualisation
│  └─ _organize_files() : Exécution du tri
└─ main() : Point d'entrée
```

## 🧪 Exemples de motifs regex avancés

```python
# Ignorer les dates au format YYYY-MM-DD
\d{4}-\d{2}-\d{2}

# Ignorer les numéros de version (v1.0, v2.3, etc.)
v\d+\.\d+

# Ignorer les extensions multiples (.tar.gz)
\.tar\.gz$

# Ignorer les préfixes numériques (001_, 002_, etc.)
^\d+_

# Ignorer tout après un tiret
-.*$

# Ignorer les espaces multiples
\s+
```

## ⚠️ Limitations connues

- Les noms de groupes ne peuvent pas contenir de caractères invalides (`< > : " / \ | ? *`)
- Le tri se base uniquement sur les noms, pas sur le contenu
- Pas de support pour les liens symboliques
- Pas d'annulation automatique (utilisez la prévisualisation)

## 🆘 Dépannage

**Problème : "Le module tkinter n'est pas trouvé"**

```bash
# Windows
python -m pip install tk

# Linux (Ubuntu/Debian)
sudo apt-get install python3-tk

# macOS (avec Homebrew)
brew install python-tk
```

**Problème : "Aucun regroupement possible"**

- Réduisez le seuil de similarité
- Vérifiez que les noms ont des parties communes
- Vérifiez les règles d'ignorance (peut-être trop agressives)

**Problème : "Erreur dans le motif regex"**

- Vérifiez la syntaxe de votre regex
- Échappez les caractères spéciaux avec `\`
- Testez votre regex sur [regex101.com](https://regex101.com)

## 📝 Licence

Ce code est fourni tel quel, libre d'utilisation et de modification.

## 👨‍💻 Auteur

Développé par un ingénieur Python senior expérimenté.

---

**Version** : 1.0.0  
**Date** : 2026  
**Langage** : Python 3.7+  
**Framework UI** : Tkinter
