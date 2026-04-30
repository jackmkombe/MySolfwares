# 🚀 Smart Sorter v3.1 - Guide de Démarrage

## ⚡ Lancement Ultra-Rapide

```powershell
python smart_sorter_v3.py
```

---

## 🎯 Utilisation en 5 Étapes

### 1️⃣ Choisir le Dossier Source

Cliquez sur **"Choisir"** et sélectionnez le dossier contenant vos fichiers à trier

### 2️⃣ Sélectionner le Type de Tri

- 📄 **Fichiers** : Trie uniquement les fichiers
- 📁 **Dossiers** : Trie uniquement les sous-dossiers
- 📦 **Les deux** : Trie fichiers ET dossiers ⭐ **Recommandé**

### 3️⃣ Ajouter des Règles (Optionnel)

Cliquez sur les raccourcis pour nettoyer les noms :

- **Crochets** : Ignore `[DKB]`, `[YIFY]`, etc.
- **Parenthèses** : Ignore `(2024)`, `(HD)`, etc.
- **Numéros** : Ignore `_001`, `_123`, etc.
- **Années** : Ignore `2024`, `2023`, etc.

### 4️⃣ Prévisualiser

Cliquez sur **🔍 Prévisualiser** pour voir les groupes qui seront créés

### 5️⃣ Lancer le Tri

Cliquez sur **🚀 Lancer le Tri** et confirmez

✅ **C'est fait !** Vos fichiers sont organisés

---

## 💡 Exemple Concret

### Situation

Vous avez téléchargé des films :

```
Downloads/
├── [YIFY] Inception.1080p.mp4
├── [DKB] Inception.720p.mkv
├── [YIFY] Interstellar.mp4
├── [RARBG] Interstellar.1080p.mp4
```

### Configuration

1. **Dossier source** : `Downloads`
2. **Type** : Fichiers
3. **Raccourci** : Cliquez sur "Crochets"
4. **Seuil** : 0.7 (par défaut)

### Résultat

```
Downloads/
├── Inception/
│   ├── [YIFY] Inception.1080p.mp4
│   └── [DKB] Inception.720p.mkv
└── Interstellar/
    ├── [YIFY] Interstellar.mp4
    └── [RARBG] Interstellar.1080p.mp4
```

---

## 🎨 Nouveautés v3.1

### ✅ Scroll Fluide

Le défilement avec la molette est maintenant très fluide

### ✅ Taille Optimale

Fenêtre de 850x950 - tout est visible sans scroll

### ✅ Boutons Fixes

Les boutons gardent une taille raisonnable même en plein écran

### ✅ Raccourcis Fonctionnels

Les boutons de raccourcis fonctionnent parfaitement avec confirmation

---

## 🔧 Options Avancées

### Ajuster le Seuil de Similarité

- **0.9-1.0** : Très strict (noms quasi identiques)
- **0.7-0.8** : Recommandé ⭐
- **0.5-0.6** : Permissif
- **0.0-0.4** : Très permissif

### Destination Personnalisée

Cochez **"Utiliser un dossier de destination personnalisé"** pour créer les dossiers ailleurs

### Types de Fichiers

Décochez les types que vous ne voulez pas inclure (Images, Vidéos, Documents, Audio)

---

## 📋 Raccourcis Clavier

| Action | Raccourci            |
| ------ | -------------------- |
| Scroll | Molette de la souris |
| Fermer | Alt+F4               |

---

## 🐛 Dépannage

### L'application ne se lance pas

```powershell
# Installer CustomTkinter
pip install customtkinter

# Relancer
python smart_sorter_v3.py
```

### Aucun regroupement trouvé

- Réduisez le seuil de similarité (ex: 0.5)
- Vérifiez que vous avez des fichiers similaires

### Les raccourcis ne fonctionnent pas

- Vérifiez que vous utilisez bien `smart_sorter_v3.py` (version corrigée)

---

## ✅ Checklist Première Utilisation

- [ ] Lancer l'application
- [ ] Choisir un dossier de test
- [ ] Essayer un raccourci (ex: Crochets)
- [ ] Vérifier que le motif apparaît dans "Motifs actifs"
- [ ] Prévisualiser
- [ ] Lancer le tri

---

## 🎉 Vous êtes Prêt !

**Smart Sorter v3.1** est prêt à organiser vos fichiers avec :

- ✨ Interface moderne et fluide
- 🎯 Tri intelligent
- ⚡ Raccourcis rapides
- 🔄 Réutilisation des dossiers
- 🏷️ Noms propres

**Bon tri ! 🚀**
