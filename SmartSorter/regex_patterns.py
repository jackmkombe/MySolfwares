# ⚙️ Exemples de Configuration

"""
Ce fichier contient des exemples de motifs regex couramment utilisés
pour l'application d'organisation de fichiers.

Copiez-collez ces motifs dans l'application selon vos besoins.
"""

# ============================================================================
# MOTIFS POUR IGNORER LES TAGS ET MARQUEURS
# ============================================================================

# Ignorer tout entre crochets [...]
# Exemple: [DKB] Film.mp4 → Film.mp4
PATTERN_BRACKETS = r"\[.*?\]"

# Ignorer tout entre parenthèses (...)
# Exemple: Film (2024).mp4 → Film.mp4
PATTERN_PARENTHESES = r"\(.*?\)"

# Ignorer tout entre accolades {...}
# Exemple: Document {draft}.pdf → Document.pdf
PATTERN_BRACES = r"\{.*?\}"

# Ignorer les tags HTML/XML <...>
# Exemple: <tag>content</tag> → content
PATTERN_HTML_TAGS = r"<.*?>"


# ============================================================================
# MOTIFS POUR IGNORER LES NUMÉROS ET DATES
# ============================================================================

# Ignorer les numéros à la fin du nom
# Exemple: Document_001.pdf → Document.pdf
PATTERN_TRAILING_NUMBERS = r"_\d+$"

# Ignorer les numéros au début du nom
# Exemple: 001_Document.pdf → Document.pdf
PATTERN_LEADING_NUMBERS = r"^\d+_"

# Ignorer les dates au format YYYY-MM-DD
# Exemple: Rapport_2024-01-15.pdf → Rapport.pdf
PATTERN_DATE_ISO = r"\d{4}-\d{2}-\d{2}"

# Ignorer les dates au format DD/MM/YYYY
# Exemple: Rapport_15-01-2024.pdf → Rapport.pdf
PATTERN_DATE_FR = r"\d{2}-\d{2}-\d{4}"

# Ignorer les années (4 chiffres)
# Exemple: Photo_2024.jpg → Photo.jpg
PATTERN_YEAR = r"\d{4}"

# Ignorer les timestamps
# Exemple: backup_20240115_143022.zip → backup.zip
PATTERN_TIMESTAMP = r"\d{8}_\d{6}"


# ============================================================================
# MOTIFS POUR IGNORER LES VERSIONS
# ============================================================================

# Ignorer les versions v1.0, v2.3, etc.
# Exemple: App_v1.0.exe → App.exe
PATTERN_VERSION_V = r"_?v\d+\.\d+"

# Ignorer les versions (v1), (v2), etc.
# Exemple: Document (v2).pdf → Document.pdf
PATTERN_VERSION_PARENTHESES = r"\(v\d+\)"

# Ignorer "version X"
# Exemple: File_version_2.txt → File.txt
PATTERN_VERSION_WORD = r"_?version_?\d+"


# ============================================================================
# MOTIFS POUR IGNORER LES SUFFIXES COURANTS
# ============================================================================

# Ignorer "_COPY", "_copy", etc.
# Exemple: Document_COPY.pdf → Document.pdf
PATTERN_COPY = r"_?[Cc][Oo][Pp][Yy]"

# Ignorer "_backup", "_BACKUP", etc.
# Exemple: File_backup.txt → File.txt
PATTERN_BACKUP = r"_?[Bb][Aa][Cc][Kk][Uu][Pp]"

# Ignorer "_final", "_FINAL", etc.
# Exemple: Presentation_final.pptx → Presentation.pptx
PATTERN_FINAL = r"_?[Ff][Ii][Nn][Aa][Ll]"

# Ignorer "_draft", "_DRAFT", etc.
# Exemple: Report_draft.docx → Report.docx
PATTERN_DRAFT = r"_?[Dd][Rr][Aa][Ff][Tt]"

# Ignorer "_old", "_OLD", etc.
# Exemple: Config_old.ini → Config.ini
PATTERN_OLD = r"_?[Oo][Ll][Dd]"

# Ignorer "_new", "_NEW", etc.
# Exemple: File_new.txt → File.txt
PATTERN_NEW = r"_?[Nn][Ee][Ww]"

# Ignorer "_temp", "_TEMP", "_tmp", etc.
# Exemple: Data_temp.csv → Data.csv
PATTERN_TEMP = r"_?[Tt][Ee][Mm][Pp]|_?[Tt][Mm][Pp]"


# ============================================================================
# MOTIFS POUR IGNORER LES RÉSOLUTIONS ET QUALITÉS
# ============================================================================

# Ignorer les résolutions (1080p, 720p, 4K, etc.)
# Exemple: Film_1080p.mp4 → Film.mp4
PATTERN_RESOLUTION = r"_?\d+p|_?4K|_?8K|_?HD|_?UHD"

# Ignorer les qualités (BluRay, WEB-DL, etc.)
# Exemple: Movie_BluRay.mkv → Movie.mkv
PATTERN_QUALITY = r"_?BluRay|_?WEB-DL|_?HDTV|_?DVDRip"


# ============================================================================
# MOTIFS POUR IGNORER LES LANGUES ET SOUS-TITRES
# ============================================================================

# Ignorer les codes de langue (FR, EN, etc.)
# Exemple: Film_FR.mp4 → Film.mp4
PATTERN_LANGUAGE = r"_?[A-Z]{2}(?:_|$)"

# Ignorer "VOSTFR", "SUBBED", etc.
# Exemple: Anime_VOSTFR.mkv → Anime.mkv
PATTERN_SUBTITLES = r"_?VOSTFR|_?VOST|_?SUBBED|_?SUB"


# ============================================================================
# MOTIFS COMBINÉS COMPLEXES
# ============================================================================

# Ignorer tout après un tiret (y compris le tiret)
# Exemple: Document - Copy.pdf → Document.pdf
PATTERN_AFTER_DASH = r"\s*-.*$"

# Ignorer les extensions multiples (.tar.gz, .backup.zip)
# Exemple: archive.tar.gz → archive
PATTERN_DOUBLE_EXTENSION = r"\.[a-z]+\.[a-z]+$"

# Ignorer les espaces multiples et les remplacer par un seul
# Exemple: "File    Name.txt" → "File Name.txt"
PATTERN_MULTIPLE_SPACES = r"\s+"


# ============================================================================
# EXEMPLES D'UTILISATION DANS L'APPLICATION
# ============================================================================

"""
SCÉNARIO 1: Films téléchargés
------------------------------
Fichiers:
  [YIFY] Inception.1080p.BluRay.x264.mp4
  [YIFY] Inception.720p.WEB-DL.x264.mp4
  
Motifs à ajouter:
  1. \[.*?\]           (ignorer les tags)
  2. \.\d+p            (ignorer la résolution)
  3. \.BluRay|\.WEB-DL (ignorer la qualité)
  4. \.x264            (ignorer le codec)
  
Résultat: Tous regroupés dans "Inception/"


SCÉNARIO 2: Photos de smartphone
---------------------------------
Fichiers:
  IMG_20240115_143022.jpg
  IMG_20240115_143045.jpg
  IMG_20240116_091234.jpg
  
Motifs à ajouter:
  1. _\d{8}_\d{6}  (ignorer le timestamp)
  
Résultat: Tous regroupés dans "IMG/"


SCÉNARIO 3: Documents de travail
---------------------------------
Fichiers:
  Rapport_Client_A_v1.0_final.pdf
  Rapport_Client_A_v1.1_final.pdf
  Rapport_Client_A_v2.0_draft.pdf
  
Motifs à ajouter:
  1. _v\d+\.\d+     (ignorer la version)
  2. _final|_draft  (ignorer le statut)
  
Résultat: Tous regroupés dans "Rapport Client A/"


SCÉNARIO 4: Sauvegardes
-----------------------
Fichiers:
  backup_database_2024-01-15.sql
  backup_database_2024-01-16.sql
  backup_database_2024-01-17.sql
  
Motifs à ajouter:
  1. _\d{4}-\d{2}-\d{2}  (ignorer la date)
  
Résultat: Tous regroupés dans "backup database/"


SCÉNARIO 5: Séries TV
---------------------
Fichiers:
  Breaking.Bad.S01E01.720p.WEB-DL.mp4
  Breaking.Bad.S01E02.720p.WEB-DL.mp4
  Breaking.Bad.S01E03.1080p.BluRay.mp4
  
Motifs à ajouter:
  1. \.S\d{2}E\d{2}     (ignorer S01E01)
  2. \.\d+p             (ignorer résolution)
  3. \.WEB-DL|\.BluRay  (ignorer qualité)
  
Résultat: Tous regroupés dans "Breaking Bad/"
"""


# ============================================================================
# CONSEILS D'UTILISATION
# ============================================================================

"""
1. TESTEZ TOUJOURS EN PRÉVISUALISATION
   - Utilisez le bouton "Prévisualiser" avant d'organiser
   - Vérifiez que les groupes correspondent à vos attentes

2. COMMENCEZ SIMPLE
   - Ajoutez un motif à la fois
   - Vérifiez le résultat en prévisualisation
   - Ajoutez d'autres motifs si nécessaire

3. AJUSTEZ LE SEUIL DE SIMILARITÉ
   - 0.9-1.0 : Très strict (noms quasi identiques)
   - 0.7-0.8 : Recommandé (bon équilibre)
   - 0.5-0.6 : Permissif (regroupe plus largement)
   - 0.0-0.4 : Très permissif (peut regrouper trop)

4. CARACTÈRES SPÉCIAUX REGEX
   - . (point) : N'importe quel caractère → Échapper avec \.
   - * (étoile) : 0 ou plus → Échapper avec \*
   - + (plus) : 1 ou plus → Échapper avec \+
   - ? (interrogation) : 0 ou 1 → Échapper avec \?
   - [ ] (crochets) : Classe de caractères → Échapper avec \[ \]
   - ( ) (parenthèses) : Groupe → Échapper avec \( \)
   - { } (accolades) : Quantificateur → Échapper avec \{ \}
   - ^ (accent circonflexe) : Début de chaîne
   - $ (dollar) : Fin de chaîne
   - | (pipe) : OU logique
   - \ (backslash) : Caractère d'échappement

5. TESTEZ VOS REGEX
   - Utilisez https://regex101.com pour tester vos motifs
   - Sélectionnez "Python" comme langage
   - Testez avec vos noms de fichiers réels
"""
