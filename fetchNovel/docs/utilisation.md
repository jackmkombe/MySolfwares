# Guide d'utilisation - FetchNovel

## 📋 Table des matières

1. [Premier démarrage](#premier-démarrage)
2. [Configuration des sélecteurs](#configuration-des-sélecteurs)
3. [Options de traduction](#options-de-traduction)
4. [Export des fichiers](#export-des-fichiers)
5. [Dépannage](#dépannage)

## 🚀 Premier démarrage

### Configuration de base

1. **URL de départ** : Entrez l'URL du premier chapitre du novel
   - Exemple : `https://novelhi.com/s/Douluo-Dalu-4-Ultimate-Fighting/1`

2. **Sélecteur de contenu** : Définissez comment trouver le contenu du chapitre
   - Voir section [Configuration des sélecteurs](#configuration-des-sélecteurs)

3. **Paramètres de récupération** :
   - **Chapitres par fichier** : Nombre de chapitres par document DOCX/PDF
   - **Total à récupérer** : Nombre total de chapitres à télécharger
   - **Délai furtif** : Temps d'attente entre chaque requête (secondes)

4. **Dossier de sauvegarde** : Choisissez où enregistrer les fichiers générés

## 🎯 Configuration des sélecteurs

### Syntaxe supportée

Le système accepte plusieurs types de sélecteurs CSS séparés par des virgules :

```css
#readcontent, .tdb-single-content, [aria-label*="content"]
```

### Types de sélecteurs

| Type | Exemple | Description |
|------|---------|-------------|
| **ID** | `#readcontent` | Élément avec ID spécifique |
| **Classe simple** | `.content` | Élément avec classe spécifique |
| **Classes multiples** | `.td_block_wrap.tdb_single_content` | Élément avec plusieurs classes |
| **Attribut** | `[aria-label="content"]` | Élément avec attribut spécifique |
| **Attribut partiel** | `[aria-label*="content"]` | Attribut contenant le texte |

### Sélecteurs courants

```css
#readcontent, .readcontent, #content, .content
.post-content, .entry-content, .article-content
.td-post-content, .tdb-single-content, .single-content
[aria-label*="content"], [role="main"]
.tdb-block-inner, .td-fix-index
```

### Détection automatique

Si aucun sélecteur ne fonctionne, FetchNovel essaie automatiquement :
- Les conteneurs de contenu courants
- Les éléments avec beaucoup de texte
- Les éléments avec des mots-clés liés aux romans

## 🌐 Options de traduction

### Activation

Cochez **"Traduire en français (Google Translate)"** pour activer la traduction automatique.

### Fonctionnement

- **Langue source** : Détectée automatiquement (généralement anglais)
- **Langue cible** : Français
- **Limites** : Respecte les limites de Google Translate (5000 caractères)
- **Chunking** : Les longs textes sont divisés en paragraphes

### Qualité

La traduction fonctionne mieux avec :
- Des textes narratifs
- Des dialogues clairs
- Des paragraphes bien structurés

## 📁 Export des fichiers

### Formats supportés

1. **DOCX (Word)** : Format Microsoft Word
   - Police Times New Roman 12pt
   - Justification complète
   - Alinéa de 0.3 pouces
   - Saut de page entre chapitres

2. **PDF** : Format PDF portable
   - Police Times-Roman 11pt
   - Justification et alinéa
   - Compatible avec tous les lecteurs PDF

### Nom des fichiers

Les fichiers sont nommés automatiquement :
```
{Nom du novel} c{début} - c{fin}.docx
{Nom du novel} c{début} - c{fin}.pdf
```

Exemple : `Douluo Dalu 4 Ultimate Fighting c1 - c10.docx`

## 🛠️ Dépannage

### Problèmes courants

#### "Contenu introuvable"

**Causes possibles :**
- Sélecteur incorrect
- Structure du site modifiée
- Site bloquant l'accès

**Solutions :**
1. Essayez différents sélecteurs CSS
2. Utilisez plusieurs sélecteurs séparés par des virgules
3. Augmentez le délai furtif pour éviter les blocages
4. Vérifiez que le site est accessible dans votre navigateur

#### "Erreur de traduction"

**Causes possibles :**
- Pas de connexion internet
- Service Google Translate indisponible
- Texte trop long

**Solutions :**
1. Vérifiez votre connexion internet
2. Désactivez la traduction si nécessaire
3. Essayez avec des chapitres plus courts

#### "Fichiers vides"

**Causes possibles :**
- Contenu non trouvé
- Problème d'extraction

**Solutions :**
1. Vérifiez les logs dans l'application
2. Essayez un autre sélecteur
3. Testez avec un seul chapitre d'abord

### Messages d'erreur

| Message | Cause | Solution |
|---------|-------|----------|
| `❌ Contenu introuvable` | Sélecteur invalide | Changez le sélecteur CSS |
| `⚠️ Problème sur URL` | Erreur réseau | Vérifiez connexion + délai |
| `Translation error` | Google Translate indisponible | Désactivez traduction |
| `Failed to fetch chapter` | Site inaccessible | Vérifiez URL dans navigateur |

### Conseils avancés

1. **Sélecteurs multiples** : Utilisez plusieurs sélecteurs pour augmenter les chances de succès
2. **Délai adaptatif** : Augmentez le délai pour les sites sensibles
3. **Test progressif** : Commencez avec 1-2 chapitres pour tester
4. **Logs détaillés** : Surveillez les logs pour identifier les problèmes

## 📞 Support

Pour plus d'aide :
1. Consultez les logs de l'application
2. Vérifiez la documentation technique
3. Testez avec différents sites et configurations

---

**FetchNovel v1.0** - Modern Novel Scraper
