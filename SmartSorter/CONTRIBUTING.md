# 🤝 Guide de Contribution

Merci de votre intérêt pour contribuer à l'Organisateur de Fichiers et Dossiers !

## 📋 Table des Matières

- [Code de Conduite](#code-de-conduite)
- [Comment Contribuer](#comment-contribuer)
- [Standards de Code](#standards-de-code)
- [Structure du Projet](#structure-du-projet)
- [Tests](#tests)
- [Soumettre une Contribution](#soumettre-une-contribution)

---

## 📜 Code de Conduite

Ce projet suit un code de conduite simple :

- Soyez respectueux et professionnel
- Acceptez les critiques constructives
- Concentrez-vous sur ce qui est meilleur pour la communauté
- Montrez de l'empathie envers les autres membres

---

## 🚀 Comment Contribuer

### Signaler un Bug

Si vous trouvez un bug :

1. Vérifiez qu'il n'a pas déjà été signalé
2. Créez une issue avec :
   - Description claire du problème
   - Étapes pour reproduire
   - Comportement attendu vs comportement actuel
   - Version de Python et OS
   - Logs d'erreur si disponibles

### Proposer une Fonctionnalité

Pour proposer une nouvelle fonctionnalité :

1. Créez une issue décrivant :
   - Le problème que cela résout
   - Comment cela fonctionnerait
   - Pourquoi c'est utile
2. Attendez les retours avant de commencer le développement

### Améliorer la Documentation

La documentation est toujours bienvenue :

- Corriger des fautes de frappe
- Clarifier des instructions
- Ajouter des exemples
- Traduire dans d'autres langues

---

## 💻 Standards de Code

### Style Python

Suivez **PEP 8** :

```python
# ✅ BON
def calculate_similarity(name1: str, name2: str) -> float:
    """Calcule la similarité entre deux noms."""
    return SequenceMatcher(None, name1.lower(), name2.lower()).ratio()

# ❌ MAUVAIS
def calc_sim(n1,n2):
    return SequenceMatcher(None,n1.lower(),n2.lower()).ratio()
```

### Conventions de Nommage

- **Classes** : `PascalCase` (ex: `FileOrganizerApp`)
- **Fonctions/Méthodes** : `snake_case` (ex: `calculate_similarity`)
- **Constantes** : `UPPER_SNAKE_CASE` (ex: `FILE_TYPES`)
- **Privé** : Préfixe `_` (ex: `_clean_name`)

### Type Hints

Utilisez les type hints pour la clarté :

```python
def _group_items(self, items: List[Path]) -> Dict[str, List[Path]]:
    """Regroupe les éléments par similarité."""
    pass
```

### Docstrings

Utilisez le format Google :

```python
def _calculate_similarity(self, name1: str, name2: str) -> float:
    """
    Calcule la similarité entre deux noms.

    Args:
        name1: Premier nom à comparer
        name2: Deuxième nom à comparer

    Returns:
        Score de similarité entre 0.0 et 1.0

    Raises:
        ValueError: Si les noms sont vides
    """
    pass
```

### Commentaires

- Commentez le **pourquoi**, pas le **quoi**
- Utilisez des commentaires pour les parties complexes
- Gardez les commentaires à jour

```python
# ✅ BON
# Nettoyer les espaces multiples pour éviter les faux négatifs
cleaned = re.sub(r'\s+', ' ', cleaned).strip()

# ❌ MAUVAIS
# Remplacer les espaces
cleaned = re.sub(r'\s+', ' ', cleaned).strip()
```

---

## 📁 Structure du Projet

```
Nouveau dossier/
├── file_organizer.py       # Application principale
├── create_test_files.py    # Générateur de tests
├── regex_patterns.py       # Bibliothèque de motifs
├── README.md               # Documentation principale
├── QUICKSTART.md           # Guide de démarrage rapide
├── CHANGELOG.md            # Historique des versions
├── CONTRIBUTING.md         # Ce fichier
├── LICENSE                 # Licence MIT
├── requirements.txt        # Dépendances (aucune)
├── .gitignore              # Fichiers à ignorer
├── lancer.bat              # Lanceur Windows
└── lancer.sh               # Lanceur Linux/macOS
```

### Fichier Principal : `file_organizer.py`

**Classe principale** : `FileOrganizerApp`

**Sections** :

1. **Initialisation** : `__init__`, `_setup_ui`
2. **UI Creation** : `_create_*_section`
3. **Callbacks** : `_browse_*`, `_on_*_change`, `_toggle_*`
4. **Utilitaires** : `_log`, `_clean_name`, `_calculate_similarity`
5. **Core Logic** : `_get_items_to_process`, `_group_items`
6. **Actions** : `_preview_organization`, `_organize_files`

---

## 🧪 Tests

### Tests Manuels

Avant de soumettre :

1. Exécutez `python create_test_files.py`
2. Testez avec différentes configurations :
   - Fichiers et dossiers
   - Différents types de fichiers
   - Différents seuils de similarité
   - Différents motifs regex
3. Vérifiez les logs pour les erreurs
4. Testez la prévisualisation
5. Testez l'organisation réelle

### Scénarios de Test

**Test 1 : Films avec tags**

```
Fichiers : [DKB] Film.mp4, [XYZ] Film.mkv
Motif : \[.*?\]
Résultat attendu : 1 groupe "Film"
```

**Test 2 : Photos numérotées**

```
Fichiers : Photo_001.jpg, Photo_002.jpg
Motif : _\d+
Résultat attendu : 1 groupe "Photo"
```

**Test 3 : Gestion des erreurs**

```
- Dossier source inexistant
- Dossier destination inexistant
- Motif regex invalide
- Aucun fichier à traiter
```

---

## 📤 Soumettre une Contribution

### Workflow Git

1. **Fork** le projet
2. **Clone** votre fork

   ```bash
   git clone https://github.com/votre-username/file-organizer.git
   ```

3. **Créez une branche**

   ```bash
   git checkout -b feature/ma-fonctionnalite
   ```

4. **Faites vos modifications**

   - Suivez les standards de code
   - Ajoutez des commentaires
   - Testez vos changements

5. **Committez**

   ```bash
   git add .
   git commit -m "feat: ajoute la fonctionnalité X"
   ```

6. **Poussez**

   ```bash
   git push origin feature/ma-fonctionnalite
   ```

7. **Créez une Pull Request**
   - Description claire des changements
   - Référence aux issues liées
   - Screenshots si pertinent

### Format des Commits

Utilisez le format **Conventional Commits** :

```
<type>(<scope>): <description>

[corps optionnel]

[footer optionnel]
```

**Types** :

- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Documentation
- `style`: Formatage (pas de changement de code)
- `refactor`: Refactoring
- `test`: Ajout de tests
- `chore`: Maintenance

**Exemples** :

```
feat(ui): ajoute un bouton pour exporter la configuration
fix(regex): corrige la gestion des caractères spéciaux
docs(readme): ajoute des exemples de motifs regex
```

---

## 🎯 Domaines de Contribution

### Priorité Haute

- 🐛 Correction de bugs
- 📝 Amélioration de la documentation
- 🧪 Ajout de tests

### Priorité Moyenne

- ✨ Nouvelles fonctionnalités (après discussion)
- 🎨 Améliorations UI/UX
- ⚡ Optimisations de performance

### Priorité Basse

- 🌍 Traductions
- 🎨 Thèmes d'interface
- 📦 Packaging (exe, app, etc.)

---

## ❓ Questions ?

Si vous avez des questions :

1. Consultez la documentation (README.md, QUICKSTART.md)
2. Cherchez dans les issues existantes
3. Créez une nouvelle issue avec le tag `question`

---

## 🙏 Remerciements

Merci à tous les contributeurs qui aident à améliorer ce projet !

**Contributeurs** :

- Ingénieur Python Senior (Auteur original)
- [Votre nom pourrait être ici !]

---

**Bonne contribution ! 🚀**
