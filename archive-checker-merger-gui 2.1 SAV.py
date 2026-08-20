import sys
import os
import re
import zipfile
import patoolib

# --- GESTION DES CHEMINS TEMPORAIRES SI COMPILÉ EN .EXE ---
if getattr(sys, 'frozen', False):
    BUNDLE_DIR = sys._MEIPASS
    os.environ["PATH"] += os.pathsep + BUNDLE_DIR
else:
    BUNDLE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- IMPORTATION SÉCURISÉE DE SEND2TRASH ---
try:
    from send2trash import send2trash
    HAS_SEND2TRASH = True
except ImportError:
    HAS_SEND2TRASH = False

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QLabel, QProgressBar, QTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter, QMessageBox, QLineEdit, QDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor

APP_VERSION = "2.1"

# --- Dictionnaire de traductions FR / EN ---
TRANSLATIONS = {
    "FR": {
        "title": f"Vérificateur, Renommeur & Fusionneur d'Archives v{APP_VERSION}",
        "btn_select": "📁 Sélectionner",
        "btn_refresh": "🔄 Actualiser",
        "btn_stop": "⏹️ Arrêter",
        "btn_toggle_all_check": "☑️ Tout cocher",
        "btn_toggle_all_uncheck": "🔳 Tout décocher",
        "btn_rename": "🏷️ Formater en 0001",
        "btn_merge": "⚡ Fusionner",
        "btn_delete": "🗑️ Corbeille",
        "lbl_dest": "📂 Destination (Fusion) :",
        "txt_dest_placeholder": "Par défaut : même dossier que l'importation...",
        "btn_browse_dest": "Parcourir...",
        "lbl_status_ready": "Prêt",
        "lbl_filter": "🔍 Filtrer :",
        "txt_filter_placeholder": "Filtrer la liste...",
        "col_select": "Sélection",
        "col_parent": "Dossier parent",
        "col_archive": "Nom de l'Archive",
        "col_format": "Format 0000",
        "col_status": "Statut",
        "col_files": "Fichiers",
        "col_range": "Séquence",
        "col_bin": "Fichiers .BIN",
        "lbl_details_title": "Détails & Informations :",
        "lbl_source_folder": "📂 Dossier source : ",
        "lbl_no_folder": "Aucun dossier sélectionné (Glissez-déposez un dossier ici)",
        "yes": "OUI ✅",
        "no": "NON ❌",
        "msg_no_selection": "Veuillez cocher au moins une archive.",
        "msg_merge_min": "Veuillez cocher au moins deux archives à fusionner.",
        "msg_no_folder_to_refresh": "Veuillez d'abord sélectionner un dossier à analyser.",
        "msg_invalid_folder": "Veuillez glisser-déposer un **dossier**.",
        "confirm_rename_title": "Confirmer le renommage",
        "confirm_rename_body": "Voulez-vous réécrire la numérotation en 4 chiffres pour les {count} archive(s) sélectionnée(s) ?",
        "confirm_delete_title": "⚠️ Déplacer vers la corbeille",
        "confirm_delete_body": "Voulez-vous envoyer {count} fichier(s) sélectionné(s) vers la corbeille ?",
        "guardrail_title": "Garde-fou : Format non respecté",
        "guardrail_body": "Impossible de fusionner !\n\n{count} archive(s) sélectionnée(s) ne respectent pas le format à 4 chiffres (Format 0000) :\n{list}\n\nVeuillez d'abord utiliser le bouton '🏷️ Formater en 0001' sur votre sélection.",
        "status_processing": "Traitement [{current}/{total}] : {file}",
        "status_done": "Analyse terminée !",
        "status_rename_done": "Renommage terminé !",
        "status_merge_done": "Fusion terminée !",
        "status_delete_done": "Envoi à la corbeille effectué !",
        "status_stopped": "Arrêt en cours...",
        "about_title": f"À propos & Guide - v{APP_VERSION}",
        "about_btn": f"ℹ️ v{APP_VERSION}",
        "about_content": (
            "📖 GUIDE D'UTILISATION (TUTORIEL PERMANENT)\n"
            "==================================================\n\n"
            "1. SÉLECTION ET ANALYSE :\n"
            "   • Cliquez sur '📁 Sélectionner' ou faites un Glisser-Déposer d'un dossier d'archives.\n"
            "   • L'application analyse récursivement les sous-dossiers (.cbz, .zip, .rar, .7z).\n"
            "   • Le scanner vérifie l'absence de fichiers indésirables (.bin) et affiche leur nombre exact.\n\n"
            "2. FORMATAGE EN 0001 (SÉLECTION) :\n"
            "   • Cochez les archives à corriger, puis cliquez sur '🏷️ Formater en 0001'.\n"
            "   • L'application renomme les fichiers internes et le nom d'archive sur 4 chiffres (ex: 1 -> 0001, 3.5 -> 0003.5).\n\n"
            "3. FUSION SÉCURISÉE EN CBZ :\n"
            "   • Cochez au moins 2 archives formatées en 'Format 0000' et cliquez sur '⚡ Fusionner'.\n"
            "   • Les images sont extraites, réordonnées séquentiellement et regroupées dans une archive CBZ unique.\n"
            "   • Le nom du CBZ est généré automatiquement : 'DOSSIER - XXXX to XXXX.cbz'.\n\n"
            "4. OUTILS D'INTERFACE ET GESTION :\n"
            "   • 🔄 Actualiser : Rescanne instantanément le dossier source pour prendre en compte les ajouts/modifications.\n"
            "   • 🗑️ Corbeille : Envoie les archives cochées directement dans la Corbeille de votre OS.\n"
            "   • Tri Dynamique : Cliquez sur les en-têtes de colonnes du tableau pour trier les données.\n\n"
            "--------------------------------------------------\n"
            "📌 NOTE DE VERSION v2.1 :\n"
            " - Affichage explicite du nombre de fichiers .BIN trouvés dans la colonne du tableau.\n"
            " - Maintien du layout compact, de la corbeille OS et du tutoriel permanent.\n"
        )
    },
    "EN": {
        "title": f"Archive Checker, Renamer & Merger v{APP_VERSION}",
        "btn_select": "📁 Select",
        "btn_refresh": "🔄 Refresh",
        "btn_stop": "⏹️ Stop",
        "btn_toggle_all_check": "☑️ Check All",
        "btn_toggle_all_uncheck": "🔳 Uncheck All",
        "btn_rename": "🏷️ Format 0001",
        "btn_merge": "⚡ Merge",
        "btn_delete": "🗑️ Trash",
        "lbl_dest": "📂 Destination (Merge):",
        "txt_dest_placeholder": "Default: same folder as imported...",
        "btn_browse_dest": "Browse...",
        "lbl_status_ready": "Ready",
        "lbl_filter": "🔍 Filter:",
        "txt_filter_placeholder": "Filter list...",
        "col_select": "Selection",
        "col_parent": "Parent Folder",
        "col_archive": "Archive Name",
        "col_format": "0000 Format",
        "col_status": "Status",
        "col_files": "Files",
        "col_range": "Sequence",
        "col_bin": ".BIN Files",
        "lbl_details_title": "Details & Information:",
        "lbl_source_folder": "📂 Source Folder: ",
        "lbl_no_folder": "No folder selected (Drag and drop a folder here)",
        "yes": "YES ✅",
        "no": "NO ❌",
        "msg_no_selection": "Please check at least one archive.",
        "msg_merge_min": "Please check at least two archives to merge.",
        "msg_no_folder_to_refresh": "Please select a folder to analyze first.",
        "msg_invalid_folder": "Please drag and drop a **folder**.",
        "confirm_rename_title": "Confirm Renaming",
        "confirm_rename_body": "Do you want to rewrite 4-digit numbering for the {count} selected archive(s)?",
        "confirm_delete_title": "⚠️ Move to Trash",
        "confirm_delete_body": "Do you want to send {count} selected file(s) to the Recycle Bin?",
        "guardrail_title": "Guardrail: Format not respected",
        "guardrail_body": "Cannot merge!\n\n{count} selected archive(s) do not follow the 4-digit format (0000 Format):\n{list}\n\nPlease use the '🏷️ Format to 0001' button on your selection first.",
        "status_processing": "Processing [{current}/{total}]: {file}",
        "status_done": "Analysis finished!",
        "status_rename_done": "Renaming finished!",
        "status_merge_done": "Merging finished!",
        "status_delete_done": "Moved to Recycle Bin successfully!",
        "status_stopped": "Stopping in progress...",
        "about_title": f"About & User Guide - v{APP_VERSION}",
        "about_btn": f"ℹ️ v{APP_VERSION}",
        "about_content": (
            "📖 USER GUIDE (PERMANENT TUTORIAL)\n"
            "==================================================\n\n"
            "1. SELECTION & ANALYSIS:\n"
            "   • Click '📁 Select' or Drag and Drop an archive folder.\n"
            "   • The application recursively scans subfolders (.cbz, .zip, .rar, .7z).\n"
            "   • The analyzer checks for corrupt/unwanted files (.bin) and displays their exact count.\n\n"
            "2. FORMAT TO 0001 (SELECTION):\n"
            "   • Check archives to fix, then click '🏷️ Format 0001'.\n"
            "   • Renames internal files and archive names to 4 digits (e.g. 1 -> 0001, 3.5 -> 0003.5).\n\n"
            "3. SAFE CBZ MERGING:\n"
            "   • Check at least 2 archives matching '0000 Format' and click '⚡ Merge'.\n"
            "   • Images are extracted, sequentially reordered, and packaged into a single CBZ archive.\n"
            "   • Automatic CBZ naming: 'FOLDER - XXXX to XXXX.cbz'.\n\n"
            "4. INTERFACE TOOLS & MANAGEMENT:\n"
            "   • 🔄 Refresh: Instantly rescans active folder for added or modified archives.\n"
            "   • 🗑️ Trash: Sends checked archives directly to system Recycle Bin.\n"
            "   • Dynamic Sorting: Click table headers to sort rows interactively.\n\n"
            "--------------------------------------------------\n"
            "📌 RELEASE NOTES v2.1:\n"
            " - Displays exact count of found .BIN files in the table column.\n"
            " - Retains compact layout, OS Recycle Bin support, and permanent user guide.\n"
        )
    }
}


def safe_move_to_trash(file_path):
    """ Nettoie le chemin Windows et envoie à la corbeille de façon sécurisée. """
    clean_path = os.path.abspath(os.path.normpath(file_path))
    if clean_path.startswith("\\\\?\\"):
        clean_path = clean_path[4:]

    if HAS_SEND2TRASH:
        try:
            send2trash(clean_path)
            return
        except Exception:
            pass

    os.remove(clean_path)


class NumericTableWidgetItem(QTableWidgetItem):
    """ Item personnalisé pour un tri numérique réel. """
    def __lt__(self, other):
        if isinstance(other, QTableWidgetItem):
            try:
                return float(self.text()) < float(other.text())
            except ValueError:
                pass
        return super().__lt__(other)


def format_number_with_decimals(name):
    pattern = r'(\d+)(([._\,]\d+)?)(?=[^\d]*$)'
    match = re.search(pattern, name)
    if not match:
        return name

    start, end = match.span()
    int_part = match.group(1)
    dec_part = match.group(2) if match.group(2) else ""
    return name[:start] + f"{int(int_part):04d}{dec_part}" + name[end:]


def format_chapter_number(filename):
    base_name = os.path.splitext(filename)[0]
    pattern = r'(\d+)(([._\,]\d+)?)(?=[^\d]*$)'
    match = re.search(pattern, base_name)
    if match:
        return f"{int(match.group(1)):04d}" + (match.group(2) if match.group(2) else "")
    return "0000"


def is_formatted_4_digits(filename):
    base_name = os.path.splitext(filename)[0]
    matches = list(re.finditer(r'(\d+)(([._\,]\d+)?)', base_name))
    if not matches:
        return True
    return len(matches[-1].group(1)) >= 4


class AboutDialog(QDialog):
    def __init__(self, parent=None, lang="FR"):
        super().__init__(parent)
        self.lang = lang
        t = TRANSLATIONS[self.lang]
        self.setWindowTitle(t["about_title"])
        self.resize(620, 500)

        layout = QVBoxLayout(self)
        lbl_title = QLabel(f"{t['title']}")
        lbl_title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(lbl_title)

        txt_info = QTextEdit()
        txt_info.setReadOnly(True)
        txt_info.setText(t["about_content"])
        layout.addWidget(txt_info)

        btn_close = QPushButton("OK")
        btn_close.setFixedHeight(35)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)


class ArchiveWorker(QThread):
    progress_updated = pyqtSignal(int, int, str)
    result_found = pyqtSignal(dict)
    finished_processing = pyqtSignal()

    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path
        self.is_running = True

    def run(self):
        supported_exts = ('.zip', '.cbz', '.rar', '.cbr', '.7z', '.tar', '.gz')
        archive_files = []

        for root, _, files in os.walk(self.folder_path):
            for file in files:
                if file.lower().endswith(supported_exts):
                    archive_files.append(os.path.join(root, file))

        archive_files.sort()
        total_files = len(archive_files)

        for index, archive_path in enumerate(archive_files):
            if not self.is_running:
                break
            self.progress_updated.emit(index + 1, total_files, os.path.basename(archive_path))
            res = self.analyze_archive(archive_path)
            self.result_found.emit(res)

        self.finished_processing.emit()

    def stop(self):
        self.is_running = False

    def analyze_archive(self, archive_path):
        filename = os.path.basename(archive_path)
        parent_dir_full = os.path.dirname(archive_path)
        try:
            rel_parent_dir = os.path.relpath(parent_dir_full, self.folder_path)
            parent_folder_display = "." if rel_parent_dir == "." else rel_parent_dir
        except ValueError:
            parent_folder_display = parent_dir_full

        status = "OK"
        details = []
        has_bin = False
        bin_count = 0
        missing_numbers = []
        file_count = 0
        min_num, max_num = None, None
        is_4_digits = is_formatted_4_digits(filename)

        try:
            files = []
            if archive_path.lower().endswith(('.zip', '.cbz')):
                with zipfile.ZipFile(archive_path, 'r') as z:
                    files = z.namelist()
            else:
                files = [item[0] for item in patoolib.list_archive(archive_path, verbosity=-1)]

            files = [f for f in files if not f.endswith('/') and not f.endswith('\\')]
            file_count = len(files)

            bin_files = [f for f in files if f.lower().endswith('.bin')]
            bin_count = len(bin_files)
            if bin_count > 0:
                has_bin = True
                details.append(f"❌ {bin_count} .BIN file(s) found : {', '.join(bin_files)}")

            numbers = []
            for f in files:
                base_f = os.path.basename(f)
                if base_f.startswith('.'):
                    continue
                match = re.findall(r'\d+', base_f)
                if match:
                    numbers.append((int(match[-1]), base_f))

            if numbers:
                numbers.sort(key=lambda x: x[0])
                extracted_nums = [n[0] for n in numbers]
                min_num, max_num = extracted_nums[0], extracted_nums[-1]
                expected_set = set(range(min_num, max_num + 1))
                missing_numbers = sorted(list(expected_set - set(extracted_nums)))

                if missing_numbers:
                    details.append(f"❌ Incomplete sequence ({min_num} ➔ {max_num}). Missing: {missing_numbers}")
                else:
                    details.append(f"✅ Complete sequence ({min_num} ➔ {max_num})")
            else:
                details.append("⚠️ No numbered files found.")

            if has_bin and missing_numbers:
                status = "CRITICAL (BIN + Seq)"
            elif has_bin:
                status = "ERROR (.BIN inside)"
            elif missing_numbers:
                status = f"INCOMPLETE (-{len(missing_numbers)} num)"
            elif not numbers:
                status = "WARNING (Unnumbered)"

        except Exception as e:
            status = "READ ERROR"
            details.append(f"❌ Read error: {str(e)}")

        return {
            "path": archive_path,
            "parent_folder": parent_folder_display,
            "filename": filename,
            "status": status,
            "file_count": file_count,
            "has_bin": has_bin,
            "bin_count": bin_count,
            "is_4_digits": is_4_digits,
            "missing_numbers": missing_numbers,
            "range": f"{min_num} - {max_num}" if min_num is not None else "N/A",
            "details": "\n".join(details)
        }


class RenameWorker(QThread):
    progress_updated = pyqtSignal(int, int, str)
    finished_rename = pyqtSignal(int)
    error_occurred = pyqtSignal(str)

    def __init__(self, selected_archives):
        super().__init__()
        self.selected_archives = selected_archives

    def run(self):
        total = len(self.selected_archives)
        processed = 0

        try:
            for idx, archive_path in enumerate(self.selected_archives):
                self.progress_updated.emit(idx + 1, total, os.path.basename(archive_path))

                dir_name, full_filename = os.path.split(archive_path)
                name_part, ext_part = os.path.splitext(full_filename)

                new_name_part = format_number_with_decimals(name_part)
                target_archive_path = os.path.join(dir_name, new_name_part + ext_part)

                if archive_path.lower().endswith(('.zip', '.cbz')):
                    temp_path = archive_path + ".tmp"
                    with zipfile.ZipFile(archive_path, 'r') as in_zip:
                        with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as out_zip:
                            for item in in_zip.namelist():
                                data = in_zip.read(item)
                                if item.endswith('/') or item.endswith('\\'):
                                    out_zip.writestr(item, data)
                                    continue

                                folder_part, filename = os.path.split(item)
                                if filename.startswith('.'):
                                    out_zip.writestr(item, data)
                                    continue

                                base_name, file_ext = os.path.splitext(filename)
                                formatted_base = format_number_with_decimals(base_name)
                                new_filename = formatted_base + file_ext

                                new_item_path = os.path.join(folder_part, new_filename).replace('\\', '/') if folder_part else new_filename
                                out_zip.writestr(new_item_path, data)

                    safe_move_to_trash(archive_path)
                    os.rename(temp_path, target_archive_path)
                else:
                    if archive_path != target_archive_path:
                        os.rename(archive_path, target_archive_path)

                processed += 1

            self.finished_rename.emit(processed)
        except Exception as e:
            self.error_occurred.emit(str(e))


class MergeWorker(QThread):
    progress_updated = pyqtSignal(int, int, str)
    finished_merge = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, selected_archives, output_path):
        super().__init__()
        self.selected_archives = selected_archives
        self.output_path = output_path

    def run(self):
        current_index = 1
        total_archives = len(self.selected_archives)

        try:
            with zipfile.ZipFile(self.output_path, 'w', zipfile.ZIP_DEFLATED) as out_zip:
                for idx, archive_path in enumerate(self.selected_archives):
                    self.progress_updated.emit(idx + 1, total_archives, os.path.basename(archive_path))

                    if archive_path.lower().endswith(('.zip', '.cbz')):
                        with zipfile.ZipFile(archive_path, 'r') as in_zip:
                            items = [f for f in in_zip.namelist() if not f.endswith('/') and not f.endswith('\\')]

                            def extract_num(fname):
                                m = re.findall(r'\d+', os.path.basename(fname))
                                return int(m[-1]) if m else None

                            items_numbered = [i for i in items if extract_num(i) is not None]
                            items_unnumbered = [i for i in items if extract_num(i) is None]

                            items_numbered.sort(key=extract_num)

                            for item in items_numbered:
                                filename = os.path.basename(item)
                                if filename.startswith('.'):
                                    continue
                                ext = os.path.splitext(filename)[1]
                                out_zip.writestr(f"{current_index:04d}{ext}", in_zip.read(item))
                                current_index += 1

                            for item in items_unnumbered:
                                filename = os.path.basename(item)
                                if not filename.startswith('.'):
                                    out_zip.writestr(filename, in_zip.read(item))

            self.finished_merge.emit(self.output_path)
        except Exception as e:
            self.error_occurred.emit(str(e))


class ArchiveCheckerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_lang = "FR"
        self.resize(880, 750)
        self.worker = None
        self.merge_worker = None
        self.rename_worker = None
        self.results_data = []
        self.all_checked = False
        self.current_folder = ""
        self.custom_destination_locked = False

        self.setAcceptDrops(True)
        self.init_ui()
        self.update_language_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # Top Controls
        top_layout = QHBoxLayout()
        self.btn_select = QPushButton()
        self.btn_select.setFixedHeight(36)
        self.btn_select.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.btn_select.clicked.connect(self.select_folder)

        self.btn_refresh = QPushButton()
        self.btn_refresh.setFixedHeight(36)
        self.btn_refresh.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.btn_refresh.clicked.connect(self.refresh_folder)

        self.btn_stop = QPushButton()
        self.btn_stop.setFixedHeight(36)
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_analysis)

        self.btn_toggle_all = QPushButton()
        self.btn_toggle_all.setFixedHeight(36)
        self.btn_toggle_all.setFont(QFont("Arial", 9))
        self.btn_toggle_all.clicked.connect(self.toggle_all_checkboxes)

        self.btn_rename = QPushButton()
        self.btn_rename.setFixedHeight(36)
        self.btn_rename.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.btn_rename.setStyleSheet("background-color: #1565c0; color: white;")
        self.btn_rename.clicked.connect(self.rename_selected)

        self.btn_merge = QPushButton()
        self.btn_merge.setFixedHeight(36)
        self.btn_merge.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.btn_merge.setStyleSheet("background-color: #2e7d32; color: white;")
        self.btn_merge.clicked.connect(self.merge_selected)

        self.btn_delete = QPushButton()
        self.btn_delete.setFixedHeight(36)
        self.btn_delete.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.btn_delete.setStyleSheet("background-color: #c62828; color: white;")
        self.btn_delete.clicked.connect(self.delete_selected)

        top_layout.addWidget(self.btn_select)
        top_layout.addWidget(self.btn_refresh)
        top_layout.addWidget(self.btn_stop)
        top_layout.addWidget(self.btn_toggle_all)
        top_layout.addWidget(self.btn_rename)
        top_layout.addWidget(self.btn_merge)
        top_layout.addWidget(self.btn_delete)
        main_layout.addLayout(top_layout)

        # Destination
        dest_layout = QHBoxLayout()
        self.lbl_dest = QLabel()
        self.lbl_dest.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.txt_destination = QLineEdit()
        self.btn_browse_dest = QPushButton()
        self.btn_browse_dest.clicked.connect(self.browse_destination)

        dest_layout.addWidget(self.lbl_dest)
        dest_layout.addWidget(self.txt_destination, 1)
        dest_layout.addWidget(self.btn_browse_dest)
        main_layout.addLayout(dest_layout)

        # Progress
        progress_layout = QVBoxLayout()
        self.lbl_status = QLabel()
        self.lbl_status.setStyleSheet("color: #444; font-weight: bold;")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.lbl_status)
        progress_layout.addWidget(self.progress_bar)
        main_layout.addLayout(progress_layout)

        # Filter
        filter_layout = QHBoxLayout()
        self.lbl_filter = QLabel()
        self.lbl_filter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.txt_filter = QLineEdit()
        self.txt_filter.textChanged.connect(self.filter_table)
        filter_layout.addWidget(self.lbl_filter)
        filter_layout.addWidget(self.txt_filter)
        main_layout.addLayout(filter_layout)

        # Splitter
        splitter = QSplitter(Qt.Orientation.Vertical)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setSortingEnabled(True)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setColumnWidth(1, 160)
        self.table.setColumnWidth(2, 200)

        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.itemSelectionChanged.connect(self.show_details)
        splitter.addWidget(self.table)

        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        details_layout.setContentsMargins(0, 5, 0, 0)

        self.lbl_source_folder_info = QLabel()
        self.lbl_source_folder_info.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.lbl_source_folder_info.setStyleSheet("color: #1565c0; margin-bottom: 2px;")
        
        self.lbl_details_title = QLabel()
        self.lbl_details_title.setFont(QFont("Arial", 9, QFont.Weight.Bold))

        self.txt_details = QTextEdit()
        self.txt_details.setReadOnly(True)
        self.txt_details.setFont(QFont("Monospace", 9))

        bottom_bar_layout = QHBoxLayout()
        self.btn_about = QPushButton()
        self.btn_about.setFixedHeight(30)
        self.btn_about.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        self.btn_about.setStyleSheet("background-color: #424242; color: white;")
        self.btn_about.clicked.connect(self.show_about_dialog)

        self.btn_lang = QPushButton("🌐 FR")
        self.btn_lang.setFixedHeight(30)
        self.btn_lang.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        self.btn_lang.setStyleSheet("background-color: #6a1b9a; color: white;")
        self.btn_lang.clicked.connect(self.toggle_language)

        bottom_bar_layout.addWidget(self.lbl_details_title, 1)
        bottom_bar_layout.addWidget(self.btn_about)
        bottom_bar_layout.addWidget(self.btn_lang)

        details_layout.addWidget(self.lbl_source_folder_info)
        details_layout.addLayout(bottom_bar_layout)
        details_layout.addWidget(self.txt_details)
        splitter.addWidget(details_widget)

        splitter.setSizes([450, 180])
        main_layout.addWidget(splitter)

    def toggle_language(self):
        self.current_lang = "EN" if self.current_lang == "FR" else "FR"
        self.btn_lang.setText(f"🌐 {self.current_lang}")
        self.update_language_ui()

    def update_language_ui(self):
        t = TRANSLATIONS[self.current_lang]
        self.setWindowTitle(t["title"])
        self.btn_select.setText(t["btn_select"])
        self.btn_refresh.setText(t["btn_refresh"])
        self.btn_stop.setText(t["btn_stop"])
        self.btn_toggle_all.setText(t["btn_toggle_all_uncheck"] if self.all_checked else t["btn_toggle_all_check"])
        self.btn_rename.setText(t["btn_rename"])
        self.btn_merge.setText(t["btn_merge"])
        self.btn_delete.setText(t["btn_delete"])
        self.btn_about.setText(t["about_btn"])

        self.lbl_dest.setText(t["lbl_dest"])
        self.txt_destination.setPlaceholderText(t["txt_dest_placeholder"])
        self.btn_browse_dest.setText(t["btn_browse_dest"])
        self.lbl_status.setText(t["lbl_status_ready"])
        self.lbl_filter.setText(t["lbl_filter"])
        self.txt_filter.setPlaceholderText(t["txt_filter_placeholder"])

        self.table.setHorizontalHeaderLabels([
            t["col_select"], t["col_parent"], t["col_archive"], t["col_format"],
            t["col_status"], t["col_files"], t["col_range"], t["col_bin"]
        ])
        self.lbl_details_title.setText(t["lbl_details_title"])

        if self.current_folder:
            self.lbl_source_folder_info.setText(f"{t['lbl_source_folder']}{self.current_folder}")
        else:
            self.lbl_source_folder_info.setText(t['lbl_no_folder'])

        for row in range(self.table.rowCount()):
            chk_item = self.table.item(row, 0)
            if chk_item:
                file_path = chk_item.data(Qt.ItemDataRole.UserRole)
                res = next((r for r in self.results_data if r["path"] == file_path), None)
                if res:
                    item_fmt = self.table.item(row, 3)
                    item_bin = self.table.item(row, 7)
                    if item_fmt:
                        item_fmt.setText(t["yes"] if res["is_4_digits"] else t["no"])
                    if item_bin:
                        bin_text = f"{t['yes']} ({res['bin_count']})" if res["has_bin"] else t["no"]
                        item_bin.setText(bin_text)

    def show_about_dialog(self):
        dialog = AboutDialog(self, self.current_lang)
        dialog.exec()

    def browse_destination(self):
        dir_path = QFileDialog.getExistingDirectory(self, TRANSLATIONS[self.current_lang]["lbl_dest"])
        if dir_path:
            self.txt_destination.setText(dir_path)
            self.custom_destination_locked = True

    def set_root_folder(self, folder):
        self.current_folder = folder
        t = TRANSLATIONS[self.current_lang]
        self.lbl_source_folder_info.setText(f"{t['lbl_source_folder']}{folder}")
        if not self.custom_destination_locked:
            self.txt_destination.setText(folder)
        self.start_analysis(folder)

    def refresh_folder(self):
        t = TRANSLATIONS[self.current_lang]
        if self.current_folder and os.path.exists(self.current_folder):
            self.start_analysis(self.current_folder)
        else:
            QMessageBox.information(self, "Info", t["msg_no_folder_to_refresh"])

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if os.path.isdir(path):
                self.set_root_folder(path)
            else:
                QMessageBox.warning(self, "Error", TRANSLATIONS[self.current_lang]["msg_invalid_folder"])

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.set_root_folder(folder)

    def delete_selected(self):
        t = TRANSLATIONS[self.current_lang]
        items_to_delete = []

        for row in range(self.table.rowCount()):
            chk_item = self.table.item(row, 0)
            if chk_item and chk_item.checkState() == Qt.CheckState.Checked:
                file_path = chk_item.data(Qt.ItemDataRole.UserRole)
                if file_path:
                    items_to_delete.append(file_path)

        if not items_to_delete:
            QMessageBox.warning(self, "Warning", t["msg_no_selection"])
            return

        reply = QMessageBox.question(
            self, t["confirm_delete_title"],
            t["confirm_delete_body"].format(count=len(items_to_delete)),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.table.setSortingEnabled(False)
        deleted_count = 0
        errors = []

        for row in range(self.table.rowCount() - 1, -1, -1):
            chk_item = self.table.item(row, 0)
            if chk_item and chk_item.checkState() == Qt.CheckState.Checked:
                file_path = chk_item.data(Qt.ItemDataRole.UserRole)
                try:
                    if file_path and os.path.exists(file_path):
                        safe_move_to_trash(file_path)

                    self.results_data = [r for r in self.results_data if r["path"] != file_path]
                    self.table.removeRow(row)
                    deleted_count += 1
                except Exception as e:
                    errors.append(f"{os.path.basename(file_path)}: {str(e)}")

        self.table.setSortingEnabled(True)

        if errors:
            QMessageBox.critical(self, "Error", "Erreur lors de la suppression :\n" + "\n".join(errors))
        else:
            self.lbl_status.setText(t["status_delete_done"])
            QMessageBox.information(self, "OK", f"{deleted_count} fichier(s) traité(s).")

    def rename_selected(self):
        t = TRANSLATIONS[self.current_lang]
        selected_paths = []

        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.checkState() == Qt.CheckState.Checked:
                file_path = item.data(Qt.ItemDataRole.UserRole)
                if file_path:
                    selected_paths.append(file_path)

        if not selected_paths:
            QMessageBox.warning(self, "Warning", t["msg_no_selection"])
            return

        reply = QMessageBox.question(
            self, t["confirm_rename_title"],
            t["confirm_rename_body"].format(count=len(selected_paths)),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.btn_select.setEnabled(False)
        self.btn_refresh.setEnabled(False)
        self.btn_rename.setEnabled(False)
        self.btn_merge.setEnabled(False)
        self.btn_delete.setEnabled(False)

        self.rename_worker = RenameWorker(selected_paths)
        self.rename_worker.progress_updated.connect(self.update_progress)
        self.rename_worker.finished_rename.connect(self.rename_finished)
        self.rename_worker.error_occurred.connect(self.rename_error)
        self.rename_worker.start()

    def rename_finished(self, count):
        self.btn_select.setEnabled(True)
        self.btn_refresh.setEnabled(True)
        self.btn_rename.setEnabled(True)
        self.btn_merge.setEnabled(True)
        self.btn_delete.setEnabled(True)
        t = TRANSLATIONS[self.current_lang]
        self.lbl_status.setText(t["status_rename_done"])
        QMessageBox.information(self, "OK", f"{count} archive(s) OK.")
        if self.current_folder:
            self.start_analysis(self.current_folder)

    def rename_error(self, err):
        self.btn_select.setEnabled(True)
        self.btn_refresh.setEnabled(True)
        self.btn_rename.setEnabled(True)
        self.btn_merge.setEnabled(True)
        self.btn_delete.setEnabled(True)
        QMessageBox.critical(self, "Error", err)

    def toggle_all_checkboxes(self):
        t = TRANSLATIONS[self.current_lang]
        self.all_checked = not self.all_checked
        target_state = Qt.CheckState.Checked if self.all_checked else Qt.CheckState.Unchecked

        for row in range(self.table.rowCount()):
            if not self.table.isRowHidden(row):
                item = self.table.item(row, 0)
                if item:
                    item.setCheckState(target_state)

        self.btn_toggle_all.setText(t["btn_toggle_all_uncheck"] if self.all_checked else t["btn_toggle_all_check"])

    def start_analysis(self, folder):
        t = TRANSLATIONS[self.current_lang]
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        self.results_data.clear()
        self.txt_details.clear()
        self.txt_filter.clear()
        self.all_checked = False
        self.btn_toggle_all.setText(t["btn_toggle_all_check"])
        self.btn_select.setEnabled(False)
        self.btn_refresh.setEnabled(False)
        self.btn_stop.setEnabled(True)

        self.worker = ArchiveWorker(folder)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.result_found.connect(self.add_result)
        self.worker.finished_processing.connect(self.analysis_finished)
        self.worker.start()

    def stop_analysis(self):
        if self.worker:
            self.worker.stop()
            self.lbl_status.setText(TRANSLATIONS[self.current_lang]["status_stopped"])

    def update_progress(self, current, total, filename):
        t = TRANSLATIONS[self.current_lang]
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.lbl_status.setText(t["status_processing"].format(current=current, total=total, file=filename))

    def add_result(self, res):
        t = TRANSLATIONS[self.current_lang]
        self.results_data.append(res)
        row = self.table.rowCount()
        self.table.insertRow(row)

        chk_item = QTableWidgetItem()
        chk_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        chk_item.setCheckState(Qt.CheckState.Unchecked)
        chk_item.setData(Qt.ItemDataRole.UserRole, res["path"])

        item_folder = QTableWidgetItem(res["parent_folder"])
        item_name = QTableWidgetItem(res["filename"])
        item_fmt = QTableWidgetItem(t["yes"] if res["is_4_digits"] else t["no"])
        item_status = QTableWidgetItem(res["status"])
        item_count = NumericTableWidgetItem(f"{res['file_count']}")
        item_range = QTableWidgetItem(res["range"])

        # Affichage enrichi avec compteur de fichiers .BIN
        bin_text = f"{t['yes']} ({res['bin_count']})" if res["has_bin"] else t["no"]
        item_bin = QTableWidgetItem(bin_text)

        if "CRITICAL" in res["status"] or "CRITIQUE" in res["status"] or "ERROR" in res["status"] or "ERREUR" in res["status"]:
            item_status.setBackground(QColor("#ffcdd2"))
            item_status.setForeground(QColor("#b71c1c"))
        elif "INCOMPLETE" in res["status"] or "INCOMPLET" in res["status"]:
            item_status.setBackground(QColor("#ffe0b2"))
            item_status.setForeground(QColor("#e65100"))
        elif "WARNING" in res["status"] or "AVERTISSEMENT" in res["status"]:
            item_status.setBackground(QColor("#fff9c4"))
            item_status.setForeground(QColor("#f57f17"))
        else:
            item_status.setBackground(QColor("#c8e6c9"))
            item_status.setForeground(QColor("#1b5e20"))

        self.table.setItem(row, 0, chk_item)
        self.table.setItem(row, 1, item_folder)
        self.table.setItem(row, 2, item_name)
        self.table.setItem(row, 3, item_fmt)
        self.table.setItem(row, 4, item_status)
        self.table.setItem(row, 5, item_count)
        self.table.setItem(row, 6, item_range)
        self.table.setItem(row, 7, item_bin)

    def filter_table(self):
        query = self.txt_filter.text().lower()
        for row in range(self.table.rowCount()):
            match = False
            for col in range(1, self.table.columnCount()):
                item = self.table.item(row, col)
                if item and query in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    def show_details(self):
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            return
        row = selected_rows[0].row()
        chk_item = self.table.item(row, 0)
        if not chk_item:
            return

        file_path = chk_item.data(Qt.ItemDataRole.UserRole)
        res = next((r for r in self.results_data if r["path"] == file_path), None)

        if res:
            text = f"Folder : {res['parent_folder']}\n"
            text += f"Path : {res['path']}\n"
            text += f"Format 0000 : {'Yes' if res['is_4_digits'] else 'No'}\n"
            text += f"Files : {res['file_count']}\n"
            text += f"Status : {res['status']}\n"
            text += "=" * 60 + "\n"
            text += res['details']

            self.txt_details.setText(text)

    def merge_selected(self):
        t = TRANSLATIONS[self.current_lang]
        selected_items = []

        for row in range(self.table.rowCount()):
            chk_item = self.table.item(row, 0)
            if chk_item and chk_item.checkState() == Qt.CheckState.Checked:
                file_path = chk_item.data(Qt.ItemDataRole.UserRole)
                res = next((r for r in self.results_data if r["path"] == file_path), None)
                if res:
                    selected_items.append(res)

        if len(selected_items) < 2:
            QMessageBox.warning(self, "Warning", t["msg_merge_min"])
            return

        non_formatted = [item["filename"] for item in selected_items if not item["is_4_digits"]]
        if non_formatted:
            fmt_list = "\n".join([f"- {name}" for name in non_formatted[:5]]) + ("\n..." if len(non_formatted) > 5 else "")
            QMessageBox.critical(self, t["guardrail_title"], t["guardrail_body"].format(count=len(non_formatted), list=fmt_list))
            return

        selected_paths = [item["path"] for item in selected_items]
        first_num = format_chapter_number(selected_items[0]["filename"])
        last_num = format_chapter_number(selected_items[-1]["filename"])

        folder_base_name = os.path.basename(self.current_folder) if self.current_folder else "Archive_fusion"
        output_filename = f"{folder_base_name} - {first_num} to {last_num}.cbz"

        dest_dir = self.txt_destination.text().strip()
        if not dest_dir or not os.path.isdir(dest_dir):
            dest_dir = self.current_folder if self.current_folder else os.getcwd()

        output_path = os.path.join(dest_dir, output_filename)

        self.btn_select.setEnabled(False)
        self.btn_refresh.setEnabled(False)
        self.btn_rename.setEnabled(False)
        self.btn_merge.setEnabled(False)
        self.btn_delete.setEnabled(False)

        self.merge_worker = MergeWorker(selected_paths, output_path)
        self.merge_worker.progress_updated.connect(self.update_progress)
        self.merge_worker.finished_merge.connect(self.merge_finished)
        self.merge_worker.error_occurred.connect(self.merge_error)
        self.merge_worker.start()

    def merge_finished(self, out_path):
        self.btn_select.setEnabled(True)
        self.btn_refresh.setEnabled(True)
        self.btn_rename.setEnabled(True)
        self.btn_merge.setEnabled(True)
        self.btn_delete.setEnabled(True)
        t = TRANSLATIONS[self.current_lang]
        self.lbl_status.setText(t["status_merge_done"])
        QMessageBox.information(self, "OK", f"CBZ OK:\n{out_path}")
        if self.current_folder:
            self.start_analysis(self.current_folder)

    def merge_error(self, err):
        self.btn_select.setEnabled(True)
        self.btn_refresh.setEnabled(True)
        self.btn_rename.setEnabled(True)
        self.btn_merge.setEnabled(True)
        self.btn_delete.setEnabled(True)
        QMessageBox.critical(self, "Error", err)

    def analysis_finished(self):
        self.btn_select.setEnabled(True)
        self.btn_refresh.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.table.setSortingEnabled(True)
        self.lbl_status.setText(TRANSLATIONS[self.current_lang]["status_done"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ArchiveCheckerApp()
    window.show()
    sys.exit(app.exec())