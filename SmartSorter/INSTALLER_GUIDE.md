# 📦 Créer l'Installateur Smart Sorter v4.2

## 🎯 Objectif

Créer un installateur Windows professionnel (`.exe`) qui :

- ✅ Installe Smart Sorter dans Program Files
- ✅ Crée un raccourci sur le bureau
- ✅ Crée un raccourci dans le menu démarrer
- ✅ Inclut toute la documentation
- ✅ Permet la désinstallation propre

---

## 📥 Télécharger Inno Setup

### Étape 1 : Téléchargement

1. Allez sur : https://jrsoftware.org/isdl.php
2. Téléchargez **Inno Setup 6.x** (version la plus récente)
3. Installez Inno Setup sur votre PC

### Étape 2 : Vérification

- Inno Setup Compiler est installé
- Vous pouvez lancer "Inno Setup Compiler" depuis le menu démarrer

---

## 🔧 Créer l'Installateur

### Méthode 1 : Interface Graphique (Recommandé)

1. **Ouvrir Inno Setup Compiler**

   - Menu Démarrer → Inno Setup Compiler

2. **Ouvrir le script**

   - File → Open
   - Sélectionnez `SmartSorter_Setup.iss`

3. **Compiler**

   - Build → Compile (ou F9)
   - Attendez la fin de la compilation

4. **Résultat**
   - L'installateur est créé dans `installer/SmartSorter_v4.2_Setup.exe`

### Méthode 2 : Ligne de Commande

```powershell
# Depuis le dossier du projet
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" SmartSorter_Setup.iss
```

---

## 📁 Fichiers Requis

Avant de compiler, assurez-vous d'avoir :

```
Nouveau dossier/
├── SmartSorter_Setup.iss        ← Script Inno Setup
├── dist/
│   └── SmartSorter_v4.2.exe     ← Exécutable
├── README_EXE.txt               ← Guide utilisateur
├── FINAL_v4.2.md                ← Documentation complète
├── EXE_GUIDE.md                 ← Guide exe
└── LICENSE                      ← Licence
```

**Important** : Tous ces fichiers doivent exister !

---

## ✅ Vérifier l'Installateur

### Test 1 : Installation

1. Double-cliquez sur `installer/SmartSorter_v4.2_Setup.exe`
2. Suivez l'assistant d'installation
3. Vérifiez que :
   - ✅ L'installation se termine sans erreur
   - ✅ Un raccourci apparaît sur le bureau
   - ✅ Smart Sorter est dans le menu démarrer

### Test 2 : Lancement

1. Double-cliquez sur le raccourci bureau
2. Vérifiez que l'application se lance correctement
3. Testez les fonctionnalités principales

### Test 3 : Désinstallation

1. Panneau de configuration → Programmes et fonctionnalités
2. Désinstallez "Smart Sorter"
3. Vérifiez que :
   - ✅ Le raccourci bureau est supprimé
   - ✅ Le dossier Program Files est supprimé
   - ✅ Le menu démarrer est nettoyé

---

## 🎨 Personnalisation

### Changer l'Icône

1. Créez ou trouvez une icône `.ico`
2. Dans `SmartSorter_Setup.iss`, modifiez :
   ```iss
   SetupIconFile=chemin\vers\votre\icone.ico
   ```

### Changer les Informations

Modifiez les lignes suivantes dans `SmartSorter_Setup.iss` :

```iss
#define MyAppPublisher "Votre Nom"
#define MyAppURL "https://votre-site.com"
```

### Ajouter des Fichiers

Dans la section `[Files]`, ajoutez :

```iss
Source: "votre_fichier.txt"; DestDir: "{app}"; Flags: ignoreversion
```

---

## 📤 Distribution

### Option 1 : Partage Direct

Partagez `installer/SmartSorter_v4.2_Setup.exe` (environ 15 MB)

### Option 2 : Hébergement Web

1. Uploadez sur votre site web
2. Partagez le lien de téléchargement

### Option 3 : GitHub Releases

1. Créez une release sur GitHub
2. Attachez `SmartSorter_v4.2_Setup.exe`
3. Partagez le lien de la release

---

## 🔒 Signature Numérique (Optionnel)

Pour éviter les avertissements Windows :

1. Obtenez un certificat de signature de code
2. Signez l'exe avec `signtool.exe`
3. Les utilisateurs ne verront plus "Éditeur inconnu"

**Note** : Les certificats coûtent environ 100-300€/an

---

## 🐛 Dépannage

### Erreur : "File not found"

**Solution** : Vérifiez que tous les fichiers existent aux chemins spécifiés

### Erreur : "Unable to execute file"

**Solution** : Vérifiez que le chemin vers ISCC.exe est correct

### L'installateur ne crée pas le raccourci

**Solution** : Vérifiez la section `[Icons]` du script

### "Windows a protégé votre PC"

**Solution** : Normal sans signature numérique. Cliquez "Informations complémentaires" → "Exécuter quand même"

---

## 📊 Résultat Final

Après compilation, vous obtenez :

**Fichier** : `installer/SmartSorter_v4.2_Setup.exe`  
**Taille** : ~15 MB  
**Fonctionnalités** :

- ✅ Installation dans Program Files
- ✅ Raccourci bureau
- ✅ Menu démarrer
- ✅ Documentation incluse
- ✅ Désinstallation propre
- ✅ Support français/anglais

---

## 🎉 Checklist Finale

- [ ] Télécharger et installer Inno Setup
- [ ] Vérifier que tous les fichiers requis existent
- [ ] Ouvrir `SmartSorter_Setup.iss` dans Inno Setup Compiler
- [ ] Compiler (F9)
- [ ] Tester l'installateur
- [ ] Vérifier l'installation
- [ ] Vérifier le lancement
- [ ] Vérifier la désinstallation
- [ ] Distribuer `SmartSorter_v4.2_Setup.exe`

---

**L'installateur professionnel est prêt ! 🚀**

---

**Version** : 4.2.0 FINAL  
**Date** : 2026-01-01  
**Fichier** : `installer/SmartSorter_v4.2_Setup.exe`  
**Statut** : Production Ready ✅
