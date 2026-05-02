# Guide d'installation Inno Setup pour FetchNovel

## 📦 Installation d'Inno Setup

### Étape 1: Télécharger Inno Setup

1. Allez sur le site officiel : https://jrsoftware.org/isdl.php
2. Téléchargez la version **"QuickStart Pack"** (recommandé)
   - Inclut le compilateur `iscc.exe`
   - Contient l'éditeur de scripts
   - Support multilingue inclus

### Étape 2: Installation

1. Exécutez le fichier d'installation
2. Suivez les instructions par défaut
3. Cochez l'option "Add to PATH" si disponible

### Étape 3: Vérification

Ouvrez une invite de commandes et tapez :
```cmd
iscc --version
```

Si vous voyez la version, l'installation est réussie !

## 🚀 Compilation de l'installateur FetchNovel

### Méthode 1: Script batch (recommandé)

1. Double-cliquez sur `compile_installer.bat`
2. Le script vérifie automatiquement tout
3. L'installateur sera créé dans `dist\Setup_FetchNovel_Win11_v1.0.exe`

### Méthode 2: Manuelle

```cmd
cd "c:\Users\etoun\Documents\Logiciel\fetchNovel"
iscc installer_script.iss
```

## 📋 Fichiers générés

Après compilation, vous aurez :

| Fichier | Description | Taille |
|---------|-------------|--------|
| `Setup_FetchNovel_Win11_v1.0.exe` | Installateur complet | ~30MB |
| `FetchNovel-1.0-win64.msi` | Alternative MSI | 16MB |
| `FetchNovel.exe` | Portable standalone | 27MB |

## 🎯 Caractéristiques de l'installateur

### ✅ Fonctionnalités incluses

- **Installation moderne** : Style Windows 11
- **Multilingue** : Français et Anglais
- **Raccourcis automatiques** : Bureau + Menu Démarrer
- **Désinstallation propre** : Via Panneau de configuration
- **Vérifications système** : Windows 10/11 requis
- **Association de fichiers** : Extension .novel (optionnel)
- **Messages personnalisés** : Bienvenue et instructions

### 📁 Répertoires créés

```
C:\Program Files\FetchNovel\
├── FetchNovel.exe          # Application principale
├── LISEZ-MOI.md           # Documentation française
├── docs\                  # Documentation
│   └── utilisation.md
├── examples\              # Exemples
│   └── selecteurs_exemples.txt
├── downloads\             # Downloads par défaut
├── logs\                  # Logs de l'application
├── temp\                  # Fichiers temporaires
└── cache\                 # Cache
```

### 🔧 Entrées de registre

L'installateur crée :
- `HKLM\SOFTWARE\FetchNovel` : Configuration de l'application
- `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\FetchNovel` : Désinstallation
- Association de fichiers `.novel` (si activée)

## 🛠️ Personnalisation avancée

### Modifier le script

1. Ouvrez `installer_script.iss` dans l'éditeur Inno Setup
2. Modifiez les sections souhaitées
3. Recompilez avec `iscc installer_script.iss`

### Sections modifiables courantes

```ini
[Setup]
AppVersion=1.0              # Version
DefaultDirName={autopf}\FetchNovel  # Répertoire d'installation

[Icons]
Name: "{group}\FetchNovel";  # Nom du raccourci
```

### Ajouter des fichiers

```ini
[Files]
Source: "mon_fichier.txt"; DestDir: "{app}"; Flags: ignoreversion
```

## 🔍 Dépannage

### Erreurs courantes

#### "iscc n'est pas reconnu"
**Solution** : Réinstallez Inno Setup avec le QuickStart Pack

#### "Fichier introuvable"
**Solution** : Vérifiez que `dist\FetchNovel.exe` existe

#### "Erreur de compilation"
**Solution** : Vérifiez la syntaxe dans `installer_script.iss`

### Vérifications avant compilation

1. ✅ Inno Setup installé
2. ✅ `dist\FetchNovel.exe` existe
3. ✅ `installer_script.iss` présent
4. ✅ Droits administrateur pour l'installation

## 📊 Comparaison des options

| Option | Avantages | Inconvénients | Usage |
|--------|-----------|---------------|-------|
| **MSI (cx_Freeze)** | Standard Windows | Moins personnalisable | Déploiement entreprise |
| **Inno Setup** | **Recommandé** | Nécessite Inno Setup | **Distribution grand public** |
| **Portable EXE** | Aucune installation | Gros fichier | Usage personnel/clé USB |

## 🎉 Prochaines étapes

1. **Installez Inno Setup** QuickStart Pack
2. **Lancez** `compile_installer.bat`
3. **Testez** l'installateur sur une machine virtuelle
4. **Distribuez** `Setup_FetchNovel_Win11_v1.0.exe`

---

**Note** : L'installateur Inno Setup est la méthode recommandée pour la distribution de FetchNovel aux utilisateurs finaux.
