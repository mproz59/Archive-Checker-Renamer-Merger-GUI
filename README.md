
# Archive Checker, Renamer & Merger GUI (v2.1)

**Archive Checker, Renamer & Merger GUI** est une application desktop Python (PyQt6) dédiée à la gestion, l'analyse, la normalisation et la consolidation d'archives d'images (`.cbz`, `.zip`, `.rar`, `.7z`). 

Développée spécifiquement pour les collecteurs et archivistes de scans/mangas, elle permet d'automatiser le contrôle de séquences, la détection de fichiers parasites (`.bin`), le renommage normalisé sur 4 chiffres (`0000`) et la fusion sécurisée en archives CBZ uniques.

---

📸 Aperçu & Fonctionnalités Clés

- **🔍 Scan Récursif & Diagnostic Asynchrone (`QThread`) :**
  - Inspection automatique des sous-dossiers sans figer l'interface.
  - Détection explicite des fichiers corrompus/parasites (`.bin`) avec compteur dédié.
  - Analyse des séquences numériques internes (détection des chapitres/pages manquants).
  - Code couleur par statut : `OK`, `INCOMPLETE`, `ERROR (.BIN inside)`, `CRITICAL`, `WARNING`.

- **🏷️ Formatage Standardisé sur 4 Chiffres (`Format 0000`) :**
  - Normalisation automatique des noms de fichiers internes et des archives (ex: `1` ➔ `0001`, `3.5` ➔ `0003.5`).
  - Prise en charge des numérotations décimales pour les demi-chapitres.

- **⚡ Fusion Sécurisée en CBZ Unique :**
  - Regroupement de plusieurs archives en un seul fichier `.cbz`.
  - Réindexation séquentielle continue globale de toutes les pages (`0001.jpg`, `0002.jpg`, ...).
  - Génération automatique de la nomenclature : `NOM_DOSSIER - XXXX to XXXX.cbz`.
  - **Garde-fou strict :** Blocage de la fusion si les archives sélectionnées ne sont pas préalablement au format `0000`.

- **🛡️ Sécurité des Données & Ergonomie :**
  - **Corbeille OS intégrée (`send2trash`) :** Aucune suppression définitive irréversible lors des opérations de remplacement/nettoyage.
  - **Glisser-Déposer (Drag & Drop) :** Importation directe de dossiers par simple dépôt sur la fenêtre.
  - **Interface Bilingue dynamique :** Bascule instantanée Français / Anglais (FR/EN) sans redémarrage.
  - **Tri & Filtrage Dynamiques :** Tri numérique réel sur les colonnes et recherche rapide en temps réel.

---

🛠️ Configuration Requise & Dépendances

- **Python :** 3.10 ou supérieur
- **Dépendances Python :**
  - `PyQt6` (Interface graphique)
  - `send2trash` (Gestion sécurisée de la corbeille OS)
  - `patool` (Support des formats RAR, 7Z, TAR, GZ)
 


📖 Guide d'Utilisation
Sélectionner un dossier : Cliquez sur 📁 Sélectionner ou glissez-déposez directement un dossier dans l'application.

Analyser : L'application affiche la liste des archives avec le nombre de fichiers, les plages de séquences et la présence éventuelle de fichiers .bin.

Formater : Cochez les archives nécessitant un ajustement et cliquez sur 🏷️ Formater en 0001.

Fusionner : Cochez au moins 2 archives au format 0000 valide, choisissez un dossier de destination (optionnel) et cliquez sur ⚡ Fusionner.

Nettoyer : Utilisez le bouton 🗑️ Corbeille pour envoyer les doublons ou fichiers inutiles vers la corbeille de votre système en toute sécurité.



📄 Licence

Ce projet est sous licence **GNU General Public License v3.0 (GPLv3)** - voir le fichier [LICENSE](LICENSE) pour plus de détails. En raison de l'utilisation de **PyQt6** et **patool**, cette application est soumise aux termes du copyleft fort de la GPLv3.




