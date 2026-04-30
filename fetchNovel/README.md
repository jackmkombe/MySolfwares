# 📖 FetchNovel - Scraper de Romans Moderne

**FetchNovel** est une application Windows élégante conçue pour récupérer automatiquement les chapitres de vos romans préférés depuis des sites de lecture en ligne et les sauvegarder proprement aux formats **DOCX** et **PDF** avec une mise en page de type "Livre professionnel".

## ✨ Fonctionnalités

- **GUI Moderne** : Une interface inspirée de Windows 11 avec modes clair et sombre.
- **Mise en page Premium** :
  - Justification du texte et retraits de première ligne (indents).
  - Polices avec empattement (Times New Roman) pour un confort de lecture optimal.
- **Traitement par paquets** : Créez automatiquement de nouveaux fichiers tous les X chapitres (ex: 50 chapitres par fichier).
- **Nommage Intelligent** : Les fichiers sont nommés selon le roman et la plage de chapitres (ex: `My Novel c1 - c50.docx`).

## 🚀 Installation & Utilisation

### 1. Utilisation de l'exécutable (Recommandé)

Lancez simplement `FetchNovel.exe` et remplissez les paramètres.

### 2. Configuration des paramètres

| Paramètre             | Description                                                                                                            |
| :-------------------- | :--------------------------------------------------------------------------------------------------------------------- |
| **Start URL**         | Le lien du **chapitre 1** (ex: `https://site.com/roman/chapitre-1`). L'app incrémentera seule le numéro pour la suite. |
| **Content Selector**  | C'est l'identifiant technique qui indique à l'app _où_ se trouve le texte sur la page.                                 |
| **Chapters per File** | Le nombre de chapitres à mettre dans chaque document créé.                                                             |
| **Save Location**     | Le dossier où seront créés les fichiers.                                                                               |

---

## 🔍 Comment trouver le "Content Selector" ?

Si vous utilisez un site autre que ceux configurés par défaut, vous devez indiquer à l'application où se cache le texte du roman.

1. Allez sur une page de chapitre du site avec votre navigateur (Chrome, Edge, Firefox).
2. Faites un **clic droit** sur le texte du roman et choisissez **Inspecter**.
3. Dans la fenêtre qui s'ouvre, cherchez la balise `<div>` qui englobe _tout_ le texte du chapitre.
   - Si elle a un `id`, utilisez `#` : exemple `id="chapter-content"` devient `#chapter-content`.
   - Si elle a une `class`, utilisez `.` : exemple `class="entry-content"` devient `.entry-content`.
4. Copiez cette valeur dans le champ **Content Selector** de l'application.

---

## 🛠 Compilation (Pour développeurs)

Si vous souhaitez générer l'exécutable vous-même :

1. Installez les dépendances : `pip install customtkinter requests beautifulsoup4 python-docx reportlab pyinstaller`
2. Lancez la commande :
   ```bash
   pyinstaller --noconsole --onefile --name "FetchNovel" --add-data "scraper.py;." --add-data "app.py;." run.py
   ```
   _L'exécutable se trouvera dans le dossier `dist/`._

---

_Développé pour une expérience de lecture ultime._
