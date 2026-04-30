# 🚀 Guide de Démarrage Rapide

## Installation en 30 secondes

### Étape 1 : Vérifier Python

```bash
python --version
```

Vous devez avoir Python 3.7 ou supérieur.

### Étape 2 : Lancer l'application

```bash
python file_organizer.py
```

C'est tout ! L'application s'ouvre immédiatement.

---

## 🎯 Premier Test en 5 Minutes

### 1. Créer des fichiers de test

```bash
python create_test_files.py
```

Cela crée deux dossiers :

- `test_files/` : Fichiers de test variés
- `test_folders/` : Dossiers de test

### 2. Lancer l'application

```bash
python file_organizer.py
```

### 3. Configuration rapide

**Pour trier les films :**

1. Cliquez sur "Parcourir..." → Sélectionnez `test_files`
2. Type de tri : **Trier des fichiers**
3. Type de fichiers : **videos**
4. Motif à ignorer : `\[.*?\]` puis cliquez "Ajouter"
5. Seuil : **0.7**
6. Cliquez sur **"🔍 Prévisualiser"**
7. Vérifiez les groupes dans les logs
8. Cliquez sur **"▶️ Organiser les Fichiers"**

✅ Vos films sont maintenant organisés par titre !

---

## 📚 Cas d'Usage Courants

### 🎬 Organiser des films/séries

**Problème :** Films avec tags et qualités

```
[YIFY] Inception.1080p.mp4
[RARBG] Inception.720p.mp4
```

**Solution :**

- Motifs : `\[.*?\]` et `\.\d+p`
- Seuil : 0.7
- Type : videos

**Résultat :** Dossier "Inception" avec tous les fichiers

---

### 📸 Organiser des photos

**Problème :** Photos avec timestamps

```
IMG_20240115_143022.jpg
IMG_20240115_143045.jpg
```

**Solution :**

- Motif : `_\d{8}_\d{6}`
- Seuil : 0.8
- Type : images

**Résultat :** Dossier "IMG" avec toutes les photos

---

### 📄 Organiser des documents

**Problème :** Documents avec versions

```
Rapport_v1.0.pdf
Rapport_v1.1.pdf
Rapport_v2.0.pdf
```

**Solution :**

- Motif : `_v\d+\.\d+`
- Seuil : 0.7
- Type : documents

**Résultat :** Dossier "Rapport" avec toutes les versions

---

### 🎵 Organiser de la musique

**Problème :** Musique avec variantes

```
Artist - Song.mp3
Artist - Song (Remix).mp3
Artist - Song Live.mp3
```

**Solution :**

- Motif : `\(.*?\)`
- Seuil : 0.6
- Type : audio

**Résultat :** Dossier "Artist - Song" avec toutes les versions

---

## 🔧 Motifs Regex les Plus Utiles

| Motif        | Description       | Exemple                |
| ------------ | ----------------- | ---------------------- |
| `\[.*?\]`    | Ignore `[...]`    | `[TAG] File` → `File`  |
| `\(.*?\)`    | Ignore `(...)`    | `File (2024)` → `File` |
| `_\d+`       | Ignore `_123`     | `File_001` → `File`    |
| `\d{4}`      | Ignore année      | `File2024` → `File`    |
| `_v\d+\.\d+` | Ignore version    | `File_v1.0` → `File`   |
| `\.\d+p`     | Ignore résolution | `Film.1080p` → `Film`  |

💡 **Astuce :** Copiez-collez ces motifs directement dans l'application !

---

## ⚡ Raccourcis et Astuces

### Prévisualiser TOUJOURS avant d'organiser

- Cliquez sur "🔍 Prévisualiser"
- Vérifiez les groupes dans les logs
- Ajustez si nécessaire

### Ajuster le seuil de similarité

- **Trop de groupes ?** → Réduire le seuil (ex: 0.6)
- **Pas assez de groupes ?** → Augmenter le seuil (ex: 0.8)

### Tester les motifs regex

- Utilisez [regex101.com](https://regex101.com)
- Sélectionnez "Python" comme langage
- Testez avec vos vrais noms de fichiers

### Annuler une organisation

- L'application ne supprime jamais de fichiers
- Déplacez manuellement les fichiers si besoin
- Ou utilisez Ctrl+Z dans l'explorateur (Windows)

---

## ❓ FAQ Express

**Q : L'application ne trouve aucun fichier**

- Vérifiez que le dossier source contient bien des fichiers
- Vérifiez le filtre de type (images, videos, etc.)

**Q : Aucun regroupement possible**

- Réduisez le seuil de similarité
- Vérifiez que les noms ont des parties communes
- Supprimez les motifs trop agressifs

**Q : Les groupes ont des noms bizarres**

- Ajoutez des motifs pour ignorer les parties non pertinentes
- Augmentez le seuil pour des groupes plus stricts

**Q : Erreur "module tkinter not found"**

```bash
# Windows
pip install tk

# Linux
sudo apt-get install python3-tk

# macOS
brew install python-tk
```

---

## 📁 Structure des Fichiers

```
Nouveau dossier/
├── file_organizer.py       ← Application principale
├── create_test_files.py    ← Générateur de tests
├── regex_patterns.py       ← Bibliothèque de motifs
├── README.md               ← Documentation complète
└── QUICKSTART.md           ← Ce guide
```

---

## 🎓 Prochaines Étapes

1. ✅ Testez avec les fichiers d'exemple
2. ✅ Essayez avec vos propres fichiers (faites une copie d'abord !)
3. ✅ Consultez `regex_patterns.py` pour plus de motifs
4. ✅ Lisez `README.md` pour la documentation complète

---

## 🆘 Besoin d'Aide ?

1. Consultez `README.md` pour la documentation complète
2. Regardez `regex_patterns.py` pour des exemples de motifs
3. Testez vos regex sur [regex101.com](https://regex101.com)

---

**Bon tri ! 🎉**
