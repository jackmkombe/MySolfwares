# 🔀 Fusion Automatique des Dossiers - v4.1

## ✨ Nouvelle Fonctionnalité

### Problème Résolu

**Avant (v4.0)** :

```
Dossier existant : "Film/"
Nouveau groupe : "Film 2024/"

→ 2 dossiers séparés ❌
```

**Maintenant (v4.1)** :

```
Dossier existant : "Film/"
Nouveau groupe : "Film 2024/"

→ Fusion automatique dans "Film/" ✅
```

---

## 🧠 Comment ça Marche

### Étape 1 : Détection des Dossiers Existants

L'application scanne le dossier de destination et liste tous les dossiers existants.

### Étape 2 : Comparaison Intelligente

Pour chaque nouveau groupe à créer, l'IA compare le nom avec tous les dossiers existants en utilisant les **4 algorithmes de similarité**.

### Étape 3 : Fusion Automatique

Si la similarité dépasse le seuil du mode sélectionné :

- **Strict** (85%) : Fusion uniquement si très similaire
- **Normal** (65%) : Fusion si similaire ⭐
- **Permissif** (45%) : Fusion large

Les fichiers sont déplacés dans le dossier existant au lieu d'en créer un nouveau.

---

## 📊 Exemples Concrets

### Exemple 1 : Séries TV

**Situation** :

```
Downloads/
├── Breaking Bad/  (dossier existant avec S01E01-E05)
├── Breaking.Bad.S01E06.mkv  (nouveau fichier)
└── Breaking Bad - S01E07.mp4  (nouveau fichier)
```

**Résultat (Mode Normal)** :

```
Downloads/
└── Breaking Bad/  (fusionné)
    ├── S01E01.mkv
    ├── S01E02.mkv
    ├── ...
    ├── Breaking.Bad.S01E06.mkv  ← Ajouté
    └── Breaking Bad - S01E07.mp4  ← Ajouté
```

✅ **1 dossier fusionné automatiquement**

---

### Exemple 2 : Films avec Années

**Situation** :

```
Films/
├── Inception/  (dossier existant)
├── Inception.2010.1080p.mkv  (nouveau)
└── Inception (2010) VOSTFR.mp4  (nouveau)
```

**Analyse** :

- Nom extrait : "Inception"
- Dossier existant : "Inception"
- Similarité : 100%
- Seuil Normal : 65%
- **100% ≥ 65% → FUSION**

**Résultat** :

```
Films/
└── Inception/  (fusionné)
    ├── [fichiers existants]
    ├── Inception.2010.1080p.mkv  ← Ajouté
    └── Inception (2010) VOSTFR.mp4  ← Ajouté
```

---

### Exemple 3 : Variations de Noms

**Situation** :

```
Series/
├── Game of Thrones/  (existant)
├── GoT.S08E01.mkv  (nouveau)
└── Game.of.Thrones.S08E02.mp4  (nouveau)
```

**Analyse** :

- "GoT" → Extrait : "GoT"
- "Game.of.Thrones" → Extrait : "Game of Thrones"
- Comparaison avec "Game of Thrones" :
  - "GoT" vs "Game of Thrones" : ~40% (pas de fusion)
  - "Game of Thrones" vs "Game of Thrones" : 100% (fusion)

**Résultat (Mode Normal)** :

```
Series/
├── Game of Thrones/  (fusionné)
│   ├── [fichiers existants]
│   └── Game.of.Thrones.S08E02.mp4  ← Ajouté
└── GoT/  (nouveau dossier, pas assez similaire)
    └── GoT.S08E01.mkv
```

---

## 🎯 Avantages

### 1. Organisation Cohérente

Plus de dossiers dupliqués avec des noms légèrement différents

### 2. Gain de Temps

Pas besoin de fusionner manuellement les dossiers

### 3. Intelligent

Utilise les mêmes algorithmes que le regroupement initial

### 4. Sécurisé

- Gestion des conflits de noms
- Confirmation avant fusion
- Compteur de fusions dans le résumé

---

## 💡 Cas d'Usage

### Téléchargements Progressifs

**Scénario** : Vous téléchargez une série épisode par épisode

**Jour 1** :

```
python smart_sorter_v4.py
→ Crée "Breaking Bad/" avec E01-E03
```

**Jour 2** : Nouveaux épisodes E04-E06

```
python smart_sorter_v4.py
→ Détecte "Breaking Bad/" existant
→ Fusionne automatiquement E04-E06 dedans
```

**Résultat** : Un seul dossier "Breaking Bad/" avec tous les épisodes

---

### Réorganisation Incrémentale

**Scénario** : Vous organisez vos fichiers par lots

**Lot 1** : Films d'action

```
→ Crée "Inception/", "Matrix/", etc.
```

**Lot 2** : Autres films (dont Inception 2010)

```
→ Détecte "Inception/" existant
→ Fusionne automatiquement
```

---

## 📋 Résumé Amélioré

### Avant (v4.0)

```
✅ Tri intelligent terminé !

Mode utilisé: NORMAL
📦 42 éléments déplacés
🔄 3 dossiers réutilisés
```

### Maintenant (v4.1)

```
✅ Tri intelligent terminé !

Mode utilisé: NORMAL
📦 42 éléments déplacés
🔀 5 dossiers fusionnés automatiquement  ← NOUVEAU
🔄 3 dossiers réutilisés
```

---

## ⚙️ Configuration

### Mode Strict

- Seuil : 85%
- Fusion uniquement si noms très similaires
- Exemple : "Film" et "Film HD" → Pas de fusion

### Mode Normal ⭐ **RECOMMANDÉ**

- Seuil : 65%
- Équilibre entre précision et fusion
- Exemple : "Film" et "Film 2024" → Fusion

### Mode Permissif

- Seuil : 45%
- Fusion large
- Exemple : "Film" et "Film Action" → Fusion (peut-être trop)

---

## 🔒 Sécurité

### Gestion des Conflits

Si un fichier existe déjà dans le dossier cible :

```
Film.mkv existe déjà
→ Renomme en Film_1.mkv
→ Si Film_1.mkv existe → Film_2.mkv
→ Etc.
```

### Confirmation

Message de confirmation explicite :

```
"Voulez-vous lancer le tri intelligent ?

Note: Les dossiers similaires existants
seront fusionnés automatiquement."
```

---

## 🎉 Résumé

**Smart Sorter v4.1** ajoute la fusion automatique :

✅ **Détection** des dossiers existants  
✅ **Comparaison** intelligente avec IA  
✅ **Fusion** automatique si similaire  
✅ **Compteur** de fusions dans le résumé  
✅ **Sécurisé** avec gestion des conflits

**Fini les dossiers dupliqués ! 🎯**

---

**Version** : 4.1.0  
**Date** : 2026-01-01  
**Fichier** : `smart_sorter_v4.py`  
**Statut** : Production Ready ✅
