from Qt.gui import Ui_MainWindow
from Qt.layouts import ModernLayoutBuilder
from PyQt5.QtWidgets import (
    QMainWindow, QHeaderView, QShortcut, QListWidget, QTableView,
    QStyledItemDelegate, QComboBox, QAbstractItemView, QFrame, QLineEdit, QStyle,
    QToolButton, QStyleOptionViewItem, QFileDialog,
)
from PyQt5.QtCore import Qt, QModelIndex, QVariant, QThread, pyqtSignal, QAbstractTableModel, QSize, QEvent, QTimer, QUrl
from PyQt5.QtGui import QKeySequence, QIcon, QPalette, QColor, QPainter, QDesktopServices
from shutil import copyfile
import os
import logging
import core
from Qt.theme import Colors
import subprocess
import psutil
import fileinput

profile_manager = core.ProfileManager()
games = []

OVERLAY_WIDGETS = (
    "profile_create_window",
    "set_steam_path_window",
    "set_greenluma_path_window",
    "greenluma_install_window",
    "steam_downgrade_window",
    "generic_popup",
    "closing_steam",
    "settings_window",
)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.main_window = Ui_MainWindow()
        self.main_window.setupUi(self)
        self.setStyleSheet("")
        self.main_window.centralwidget.setStyleSheet("")
        self._layout_builder = ModernLayoutBuilder(self.main_window)
        self._layout_builder.build(self)
        self._overlay_widgets = [getattr(self.main_window, name) for name in OVERLAY_WIDGETS]
        self.setup()
        self.connect_components()
        self.import_steam_thread = None
        self.extract_greenluma_thread = None
        self.steam_downgrade_thread = None
        self.steam_restore_thread = None
        self._greenluma_retry_callback = None
        self._settings_was_open = False

    def setup(self):
        self.setWindowIcon(QIcon("icon.ico"))
        self.setMinimumSize(960, 640)
        self.resize(1180, 760)
        self._apply_french_labels()

        # Hide Other Windows
        self.main_window.profile_create_window.setHidden(True)
        self.main_window.set_steam_path_window.setHidden(True)
        self.main_window.set_greenluma_path_window.setHidden(True)
        self.main_window.greenluma_install_window.setHidden(True)
        self.main_window.steam_downgrade_window.setHidden(True)
        self.main_window.closing_steam.setHidden(True)
        self.main_window.generic_popup.setHidden(True)
        self.main_window.settings_window.setHidden(True)
        #-------

        self.setWindowTitle("BlueLuma Manager")
        self.main_window.version_label.setText("v{0}".format(core.CURRENT_VERSION))
        self.main_window.no_hook_checkbox.hide()
        self.populate_list(self.main_window.games_list, games)
        self.main_window.games_list.dropEvent = self.drop_event_handler
        self.editor_model = EditorTableModel()
        table = self.main_window.search_result
        table.setStyleSheet("")
        table.setModel(self.editor_model)
        self.cell_delegate = CellEditorDelegate(table)
        self.type_delegate = TypeDelegate(table)
        self.delete_delegate = DeleteRowDelegate(table)
        table.setItemDelegateForColumn(0, self.cell_delegate)
        table.setItemDelegateForColumn(1, self.cell_delegate)
        table.setItemDelegateForColumn(2, self.type_delegate)
        table.setItemDelegateForColumn(3, self.delete_delegate)
        self.delete_delegate.delete_clicked.connect(self.remove_editor_row)
        self.setup_editor_table()
        self.setup_steam_path()
        self.sync_steam_profiles()
        current_profile = self.main_window.profile_selector.currentText()
        if current_profile and current_profile in profile_manager.profiles:
            profile = profile_manager.profiles[current_profile]
            self.show_profile_games(profile)
            self.sync_applist_for_profile(profile)
        self.setup_greenluma_path()
        self.sync_installed_steam_library()
        if not core.config.manager_msg:
            self.show_popup("Merci d'utiliser le gestionnaire non officiel pour BlueLuma\n\nCeci est uniquement un gestionnaire de jeux ; vous devez télécharger BlueLuma séparément.", self.acknowledge_manager, lambda: core.sys.exit())

        # Settings Window Setup
        self.main_window.update_checkbox.setChecked(core.config.check_update)

        # Shortcuts
        del_game = QShortcut(QKeySequence(Qt.Key_Delete), self.main_window.games_list)
        del_game.activated.connect(self.remove_selected)

        del_editor = QShortcut(QKeySequence(Qt.Key_Delete), self.main_window.search_result)
        del_editor.activated.connect(self.remove_editor_rows)

        self._sync_overlay_stack()

    def _apply_french_labels(self):
        ui = self.main_window
        ui.label_profile.setText("Compte Steam")
        ui.label_games_list.setText("Jeux/DLC Actif")
        ui.create_profile.hide()
        ui.delete_profile.hide()
        ui.remove_game.setText("Retirer")
        ui.add_to_profile.setText("Activer")
        self._layout_builder.editor_label.setText("Éditeur — jeux / DLC non détectés")
        ui.generate_btn.hide()
        ui.create_profile_btn.setText("Créer")
        ui.cancel_profile_btn.setText("Annuler")
        ui.label_profile_name.setText("Nom du profil")
        ui.profile_name.setPlaceholderText("Nom du profil")
        ui.save_steam_path.setText("Enregistrer")
        ui.cancel_steam_path_btn.setText("Annuler")
        ui.label_steam_path.setText("Chemin Steam")
        ui.save_greenluma_path.setText("Enregistrer")
        ui.cancel_greenluma_path_btn.setText("Annuler")
        ui.label_greenluma_path.setText("Chemin BlueLuma")
        ui.popup_btn1.setText("OK")
        ui.popup_btn2.setText("Annuler")
        ui.label_close_steam.setText("Fermeture de Steam…")
        ui.run_GreenLuma_btn.setText("Lancer")
        ui.settings_label_main.setText("Paramètres")
        ui.settings_label_steam.setText("Chemin Steam")
        ui.settings_label_greenluma.setText("Chemin BlueLuma")
        ui.update_checkbox.setText("Vérifier les mises à jour au démarrage")
        ui.steam_path.setPlaceholderText("Dossier Steam")
        ui.greenluma_path.setPlaceholderText("Dossier GLinject")
        ui.settings_steam_path.setPlaceholderText("Dossier Steam")
        ui.settings_greenluma_path.setPlaceholderText("Dossier GLinject (automatique)")
        ui.settings_cancel_btn.setText("Annuler")
        ui.settings_steam_downgrade_btn.setText("Downgrade…")
        ui.settings_steam_restore_btn.setText("Restaurer")
        ui.greenluma_install_download_btn.setText("Télécharger sur cs.rin.ru")
        ui.greenluma_install_select_zip_btn.setText("Sélectionner le ZIP téléchargé")
        ui.greenluma_install_cancel_btn.setText("Annuler")
        ui.steam_downgrade_wayback_btn.setText("Ouvrir Wayback Machine")
        ui.steam_downgrade_launch_btn.setText("Lancer le downgrade")
        ui.steam_downgrade_cancel_btn.setText("Annuler")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cw = self.centralWidget()
        for overlay in self._overlay_widgets:
            if not overlay.isHidden():
                self._layout_builder.position_overlay(overlay, cw)
        self._sync_overlay_stack()

    def _sync_overlay_stack(self):
        modal_open = any(not w.isHidden() for w in self._overlay_widgets)
        self.main_window.main_panel.setEnabled(not modal_open)
        self._layout_builder.sync_overlay_stack(self._overlay_widgets)

    def connect_components(self):
        # Profile (comptes Steam synchronisés automatiquement)
        self.main_window.profile_selector.currentTextChanged.connect(self.select_profile)
        self.main_window.remove_game.clicked.connect(self.remove_selected)

        # Steam Path
        self.main_window.save_steam_path.clicked.connect(self.set_steam_path)
        self.main_window.cancel_steam_path_btn.clicked.connect(lambda: self.toggle_widget(self.main_window.set_steam_path_window))

        # GreenLuma Path
        self.main_window.save_greenluma_path.clicked.connect(self.set_greenluma_path)
        self.main_window.cancel_greenluma_path_btn.clicked.connect(lambda: self.toggle_widget(self.main_window.set_greenluma_path_window))

        self.main_window.greenluma_install_download_btn.clicked.connect(self.open_greenluma_download_page)
        self.main_window.greenluma_install_select_zip_btn.clicked.connect(self.select_greenluma_zip)
        self.main_window.greenluma_install_cancel_btn.clicked.connect(self.hide_greenluma_install_dialog)

        self.main_window.settings_steam_downgrade_btn.clicked.connect(self.show_steam_downgrade_dialog)
        self.main_window.settings_steam_restore_btn.clicked.connect(self.confirm_steam_restore)
        self.main_window.steam_downgrade_wayback_btn.clicked.connect(self.open_steam_wayback_calendar)
        self.main_window.steam_downgrade_url_input.textChanged.connect(self._on_steam_downgrade_url_changed)
        self.main_window.steam_downgrade_launch_btn.clicked.connect(self.confirm_steam_downgrade)
        self.main_window.steam_downgrade_cancel_btn.clicked.connect(self.hide_steam_downgrade_dialog)

        # Éditeur central
        self.main_window.add_to_profile.clicked.connect(self.add_editor_to_profile)
        self.main_window.search_result.clicked.connect(self._edit_table_on_click)

        # Main Buttons
        self.main_window.run_GreenLuma_btn.clicked.connect(lambda: self.show_popup("Steam va être redémarré s'il est ouvert. Continuer ?", self.run_GreenLuma))

        # Settings Window
        self.main_window.settings_btn.clicked.connect(self.open_settings)
        self.main_window.settings_cancel_btn.clicked.connect(self.cancel_settings)
        self.main_window.settings_steam_path.editingFinished.connect(self.persist_settings)
        self.main_window.update_checkbox.stateChanged.connect(lambda *_: self.persist_settings())

    # Profile Functions
    def sync_steam_profiles(self):
        if not core.is_valid_steam_path(core.config.steam_path):
            self.refresh_profile_selector()
            return False

        last_profile = core.config.last_profile
        synced, renamed = core.sync_profiles_from_steam(
            profile_manager,
            core.config.steam_path,
            last_profile=last_profile,
        )
        if synced:
            with core.get_config() as config:
                if config.last_profile in renamed:
                    config.last_profile = renamed[config.last_profile]
                elif config.last_profile not in profile_manager.profiles:
                    if profile_manager.profiles:
                        config.last_profile = sorted(profile_manager.profiles.keys(), key=str.lower)[0]
                    else:
                        config.last_profile = ""

        self.refresh_profile_selector()
        return synced

    def select_profile(self, name):
        if not name or name not in profile_manager.profiles:
            return

        with core.get_config() as config:
            config.last_profile = name

        self.show_profile_games(profile_manager.profiles[name])
        self.sync_applist_for_profile(profile_manager.profiles[name])

    def show_profile_games(self, profile):
        list_ = self.main_window.games_list

        self.populate_list(list_, profile.games)

    def sync_installed_steam_library(self):
        if not core.is_valid_steam_path(core.config.steam_path):
            return

        self.main_window.label_games_list.setText("Jeux/DLC Actif (import Steam…)")
        self.import_steam_thread = ImportSteamLibraryThread(core.config.steam_path)
        self.import_steam_thread.signal.connect(self.on_steam_library_imported)
        self.import_steam_thread.start()

    def on_steam_library_imported(self, games):
        self.main_window.label_games_list.setText("Jeux/DLC Actif")

        if not games or isinstance(games, Exception):
            return

        profile_name = self.main_window.profile_selector.currentText()
        if profile_name not in profile_manager.profiles:
            return

        profile = profile_manager.profiles[profile_name]
        added = 0
        for game in games:
            if game not in profile.games:
                profile.add_game(game)
                added += 1

        if added:
            profile.export_profile()
            self.show_profile_games(profile)
            self.sync_applist_for_profile(profile)
            logging.info("%d jeu(x) Steam ajouté(s) au profil %s", added, profile_name)

    def refresh_profile_selector(self):
        selector = self.main_window.profile_selector
        selector.blockSignals(True)
        selector.clear()

        profiles = sorted(profile_manager.profiles.values(), key=lambda item: item.name.lower())
        if not profiles:
            selector.blockSignals(False)
            self.populate_list(self.main_window.games_list, [])
            return

        last_profile = core.config.last_profile
        if last_profile in profile_manager.profiles:
            selector.addItem(last_profile)
            for profile in profiles:
                if profile.name != last_profile:
                    selector.addItem(profile.name)
        else:
            for profile in profiles:
                selector.addItem(profile.name)

        selector.blockSignals(False)

    # Éditeur manuel (panneau central)
    def setup_editor_table(self):
        table = self.main_window.search_result
        table.setFrameShape(QFrame.NoFrame)
        table.setSelectionBehavior(QTableView.SelectItems)
        table.setSelectionMode(QTableView.ExtendedSelection)
        table.setAlternatingRowColors(False)
        table.setWordWrap(False)
        table.setTextElideMode(Qt.ElideRight)
        table.setShowGrid(True)
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setCornerButtonEnabled(False)
        table.setEditTriggers(QAbstractItemView.EditKeyPressed)

        v_header = table.verticalHeader()
        v_header.setVisible(False)
        v_header.setDefaultSectionSize(36)
        v_header.setMinimumSectionSize(36)

        h_header = EditorTableHeader(Qt.Horizontal, table)
        h_header.setObjectName("editor_table_header")
        table.setHorizontalHeader(h_header)
        h_header.add_row_clicked.connect(self.add_editor_row)
        h_header.setStretchLastSection(False)
        h_header.setMinimumHeight(32)
        h_header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        h_header.setSectionResizeMode(0, QHeaderView.Fixed)
        h_header.setSectionResizeMode(1, QHeaderView.Stretch)
        h_header.setSectionResizeMode(2, QHeaderView.Fixed)
        h_header.setSectionResizeMode(3, QHeaderView.Fixed)
        table.setColumnWidth(0, 96)
        table.setColumnWidth(2, 76)
        table.setColumnWidth(3, 40)

        palette = table.palette()
        palette.setColor(QPalette.Base, QColor(Colors.INPUT_BG))
        palette.setColor(QPalette.AlternateBase, QColor(Colors.INPUT_BG))
        palette.setColor(QPalette.Text, QColor(Colors.TEXT))
        palette.setColor(QPalette.Highlight, QColor(Colors.INPUT_BG))
        palette.setColor(QPalette.HighlightedText, QColor(Colors.TEXT))
        table.setPalette(palette)

    def _edit_table_on_click(self, index):
        if index.isValid() and index.column() != EditorTableModel.ACTION_COLUMN:
            self.main_window.search_result.edit(index)

    def remove_editor_row(self, row):
        self.editor_model.remove_rows([row])

    def add_editor_row(self):
        self.editor_model.add_row()
        table = self.main_window.search_result
        table.selectRow(self.editor_model.rowCount() - 1)
        table.edit(table.model().index(self.editor_model.rowCount() - 1, 0))

    def remove_editor_rows(self):
        selection = self.main_window.search_result.selectionModel().selectedRows()
        if not selection:
            return
        rows = sorted({index.row() for index in selection}, reverse=True)
        self.editor_model.remove_rows(rows)

    def add_editor_to_profile(self):
        profile = profile_manager.profiles[self.main_window.profile_selector.currentText()]
        added = 0
        skipped = 0

        for row in self.editor_model.rows:
            app_id, name, app_type = row[0].strip(), row[1].strip(), row[2].strip()
            if not app_id or not name:
                skipped += 1
                continue
            if app_type not in ("Game", "DLC"):
                skipped += 1
                continue
            game = core.Game(app_id, name, app_type)
            if game not in profile.games:
                profile.add_game(game)
                added += 1

        if added:
            profile.export_profile()
            self.show_profile_games(profile)
            self.sync_applist_for_profile(profile)

        if skipped and not added:
            self.show_popup("Renseignez au minimum un ID et un nom pour chaque ligne.")
        elif added:
            self.show_popup("{0} entrée(s) ajoutée(s) au profil.".format(added))

    def populate_list(self, list_, data):
        list_.clear()
        for item in data:
            label = item.name
            if item.type == "DLC":
                label = "{0} [DLC]".format(item.name)
            list_.addItem(label)

    def remove_selected(self):
        items = self.main_window.games_list.selectedItems()
        if len(items) == 0:
            return

        profile = profile_manager.profiles[self.main_window.profile_selector.currentText()]

        for item in items:
            game_name = item.text().replace(" [DLC]", "")
            profile.remove_game(game_name)

        self.show_profile_games(profile)
        profile.export_profile()
        self.sync_applist_for_profile(profile)

    # Settings Functions
    def open_settings(self):
        widget = self.main_window.settings_window
        if widget.isHidden():
            self._load_settings_fields()
            self.refresh_steam_settings_status()
            self.toggle_widget(widget)
            return

        self.persist_settings()
        self.toggle_widget(widget, True)

    def cancel_settings(self):
        self._load_settings_fields()
        self.toggle_widget(self.main_window.settings_window, True)

    def _load_settings_fields(self):
        ui = self.main_window
        ui.settings_steam_path.setText(core.config.steam_path)
        ui.settings_greenluma_path.setText(core.get_glinject_path())
        ui.update_checkbox.setChecked(core.config.check_update)

    def refresh_steam_settings_status(self):
        label = self.main_window.settings_steam_cfg_status
        try:
            if core.has_steam_cfg():
                label.setText("steam.cfg détecté — les mises à jour automatiques de Steam sont bloquées.")
            else:
                label.setText("Aucun steam.cfg — Steam peut se mettre à jour normalement.")
        except RuntimeError as err:
            label.setText(str(err))

    def persist_settings(self):
        previous_steam_path = core.config.steam_path
        with core.get_config() as config:
            config.steam_path = self.main_window.settings_steam_path.text()
            core.ensure_greenluma_path(config)
            config.check_update = self.main_window.update_checkbox.isChecked()

        self.main_window.settings_greenluma_path.setText(core.get_glinject_path())

        if os.path.normcase(previous_steam_path or "") != os.path.normcase(core.config.steam_path or ""):
            self.sync_steam_profiles()
            self.sync_installed_steam_library()

    def _refresh_greenluma_runtime_path(self):
        with core.get_config() as config:
            config.no_hook = False
            core.ensure_greenluma_path(config)

    def _greenluma_runtime_ready(self):
        self._refresh_greenluma_runtime_path()
        return core.is_valid_greenluma_path(core.config.greenluma_path)

    def open_greenluma_download_page(self):
        QDesktopServices.openUrl(QUrl(core.GREENLUMA_DOWNLOAD_URL))

    def show_greenluma_install_dialog(self, retry_callback=None):
        self._greenluma_retry_callback = retry_callback
        ui = self.main_window
        ui.greenluma_install_status.setText("")
        ui.greenluma_install_download_btn.setEnabled(True)
        ui.greenluma_install_select_zip_btn.setEnabled(True)
        self.toggle_widget(ui.greenluma_install_window)

    def hide_greenluma_install_dialog(self):
        self._greenluma_retry_callback = None
        self.toggle_widget(self.main_window.greenluma_install_window, True)

    def select_greenluma_zip(self):
        zip_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner l'archive BlueLuma",
            "",
            "Archives ZIP (*.zip)",
        )
        if not zip_path:
            return

        ui = self.main_window
        ui.greenluma_install_status.setText("Extraction en cours…")
        ui.greenluma_install_download_btn.setEnabled(False)
        ui.greenluma_install_select_zip_btn.setEnabled(False)

        self.extract_greenluma_thread = ExtractGreenLumaThread(zip_path)
        self.extract_greenluma_thread.signal.connect(self.on_greenluma_extracted)
        self.extract_greenluma_thread.start()

    def on_greenluma_extracted(self, result):
        ui = self.main_window
        ui.greenluma_install_download_btn.setEnabled(True)
        ui.greenluma_install_select_zip_btn.setEnabled(True)

        if isinstance(result, Exception):
            core.logging.exception(result)
            ui.greenluma_install_status.setText(str(result))
            return

        self._refresh_greenluma_runtime_path()
        ui.greenluma_install_status.setText(
            "BlueLuma installé dans GLinject.\n"
            "Dossier actif : {0}".format(core.config.greenluma_path)
        )

        retry = self._greenluma_retry_callback
        self._greenluma_retry_callback = None
        QTimer.singleShot(800, self.hide_greenluma_install_dialog)
        if retry and self._greenluma_runtime_ready():
            QTimer.singleShot(900, retry)

    def _set_downgrade_preview(self, text=""):
        preview = self.main_window.steam_downgrade_url_preview
        if text:
            preview.setText(text)
            preview.setProperty("empty", False)
        else:
            preview.setText("Collez une URL ci-dessus pour voir l'aperçu transformé…")
            preview.setProperty("empty", True)
        preview.style().unpolish(preview)
        preview.style().polish(preview)

    def show_steam_downgrade_dialog(self):
        self._settings_was_open = not self.main_window.settings_window.isHidden()
        if self._settings_was_open:
            self.toggle_widget(self.main_window.settings_window, True)

        ui = self.main_window
        ui.steam_downgrade_status.setText("")
        ui.steam_downgrade_url_input.clear()
        self._set_downgrade_preview("")
        ui.steam_downgrade_launch_btn.setEnabled(True)
        self.toggle_widget(ui.steam_downgrade_window)

    def hide_steam_downgrade_dialog(self):
        self.toggle_widget(self.main_window.steam_downgrade_window, True)
        if getattr(self, "_settings_was_open", False):
            self._settings_was_open = False
            self.refresh_steam_settings_status()
            self.toggle_widget(self.main_window.settings_window)

    def open_steam_wayback_calendar(self):
        QDesktopServices.openUrl(QUrl(core.STEAM_WAYBACK_CALENDAR_URL))

    def _on_steam_downgrade_url_changed(self, _text):
        raw = self.main_window.steam_downgrade_url_input.text().strip()
        if not raw:
            self._set_downgrade_preview("")
            return
        try:
            self._set_downgrade_preview(core.normalize_steam_downgrade_url(raw))
        except ValueError:
            self._set_downgrade_preview("")

    def confirm_steam_downgrade(self):
        raw = self.main_window.steam_downgrade_url_input.text().strip()
        try:
            core.normalize_steam_downgrade_url(raw)
        except ValueError as err:
            self.main_window.steam_downgrade_status.setText(str(err))
            return

        self.show_popup(
            "Steam va être fermé. Une version antérieure sera téléchargée via Wayback Machine, "
            "et steam.cfg sera créé pour bloquer les mises à jour.\n\n"
            "Attendez que la fenêtre de mise à jour Steam se ferme toute seule avant de relancer Steam.\n\n"
            "Continuer ?",
            self.start_steam_downgrade,
        )

    def start_steam_downgrade(self):
        self.hide_popup()
        raw = self.main_window.steam_downgrade_url_input.text().strip()
        ui = self.main_window
        ui.steam_downgrade_status.setText("Fermeture de Steam et préparation du downgrade…")
        ui.steam_downgrade_launch_btn.setEnabled(False)

        self.steam_downgrade_thread = SteamDowngradeThread(raw)
        self.steam_downgrade_thread.signal.connect(self.on_steam_downgrade_finished)
        self.steam_downgrade_thread.start()

    def on_steam_downgrade_finished(self, result):
        ui = self.main_window
        ui.steam_downgrade_launch_btn.setEnabled(True)

        if isinstance(result, Exception):
            core.logging.exception(result)
            ui.steam_downgrade_status.setText(str(result))
            return

        ui.steam_downgrade_url_preview.setProperty("empty", False)
        ui.steam_downgrade_url_preview.setText(result)
        ui.steam_downgrade_url_preview.style().unpolish(ui.steam_downgrade_url_preview)
        ui.steam_downgrade_url_preview.style().polish(ui.steam_downgrade_url_preview)
        ui.steam_downgrade_status.setText(
            "Downgrade lancé.\n"
            "URL utilisée : {0}\n\n"
            "• Attendez que la fenêtre de mise à jour Steam se ferme toute seule.\n"
            "• steam.cfg a été créé dans votre dossier Steam.\n"
            "• Relancez ensuite Steam normalement.".format(result)
        )
        self.refresh_steam_settings_status()

    def confirm_steam_restore(self):
        self.show_popup(
            "Steam va être fermé. steam.cfg sera supprimé et la dernière version officielle "
            "sera téléchargée.\n\n"
            "Attendez que la fenêtre de mise à jour Steam se ferme toute seule avant de relancer Steam.\n\n"
            "Continuer ?",
            self.start_steam_restore,
        )

    def start_steam_restore(self):
        self.hide_popup()
        ui = self.main_window
        ui.settings_steam_restore_btn.setEnabled(False)
        ui.settings_steam_cfg_status.setText("Restauration de Steam en cours…")

        self.steam_restore_thread = SteamRestoreThread()
        self.steam_restore_thread.signal.connect(self.on_steam_restore_finished)
        self.steam_restore_thread.start()

    def on_steam_restore_finished(self, result):
        ui = self.main_window
        ui.settings_steam_restore_btn.setEnabled(True)

        if isinstance(result, Exception):
            core.logging.exception(result)
            ui.settings_steam_cfg_status.setText(str(result))
            return

        ui.settings_steam_cfg_status.setText(
            "Restauration lancée.\n"
            "• steam.cfg a été supprimé.\n"
            "• Attendez que la fenêtre de mise à jour Steam se ferme toute seule.\n"
            "• Relancez ensuite Steam normalement."
        )
        self.refresh_steam_settings_status()

    # Generation Functions
    def run_GreenLuma(self):
        self.hide_popup()

        if not self._greenluma_runtime_ready():
            self.show_greenluma_install_dialog(retry_callback=self.run_GreenLuma)
            return

        profile_name = self.main_window.profile_selector.currentText()
        if profile_name not in profile_manager.profiles:
            self.show_popup("Aucun jeu dans le profil.")
            return

        profile = profile_manager.profiles[profile_name]
        if len(profile.games) == 0:
            self.show_popup("Aucun jeu dans le profil.")
            return

        if not self.sync_applist_for_profile(profile):
            return

        self._refresh_greenluma_runtime_path()

        # Verify required components of GreenLuma are present
        core.logging.info("Validation des fichiers BlueLuma")
        gl_path = core.config.greenluma_path
        for fname in ["DLLInjector.exe", "DLLInjector.ini"]:
            test_path = os.path.join(gl_path, fname)
            if not os.path.exists(test_path):
                core.logging.error(f"{fname} not found at {test_path}")
                self.show_greenluma_install_dialog(retry_callback=self.run_GreenLuma)
                return

        # Read Dll out of DLLInjector.ini
        gl_dll = None
        with open(os.path.join(gl_path, "DLLInjector.ini")) as f:
            for line in f:
                if "#" in line:
                    line = line.split("#", 1)[0]
                if "=" in line:
                    tokens = line.split("=", 1)
                    if tokens[0].strip() == "Dll":
                        gl_dll = tokens[1].strip()
                        break
        if gl_dll is None:
            core.logging.warning(f"Failed to detect Dll from DLLInjector.ini, attempting to locate Dll")
        elif gl_dll == "":
            core.logging.warning(f"No Dll listed in DLLInjector.ini, attempting to locate Dll")
            gl_dll = None
        elif os.path.isabs(gl_dll) and os.path.exists(gl_dll) and not os.path.isfile(gl_dll):
            core.logging.warning(f"Dll listed in DLLInjector.ini is not a file, attempting to locate Dll")
            gl_dll = None
        else:
            gl_base_dll = os.path.basename(gl_dll)
            if not os.path.isabs(gl_dll) or not os.path.isfile(gl_dll):
                test_path = os.path.join(gl_path, gl_base_dll)
                if os.path.exists(test_path):
                    gl_dll = gl_base_dll
                else:
                    core.logging.error(f"{gl_base_dll} not found at {test_path}, attempting to locate proper Dll")
                    gl_dll = None
            elif os.path.normcase(gl_dll) == os.path.normcase(os.path.join(gl_path, gl_base_dll)):
                gl_dll = gl_base_dll
        if gl_dll is None:
            # Attempt to locate the Dll
            for file in os.listdir(gl_path):
                lfile = file.lower()
                if lfile.startswith("greenluma_") and lfile.endswith("_x86.dll"):
                    core.logging.info(f"Found GreenLuma as {file}")
                    gl_dll = file
                    break
            if gl_dll is None:
                core.logging.error("Impossible de localiser la DLL x86 de BlueLuma")
                self.show_greenluma_install_dialog(retry_callback=self.run_GreenLuma)
                return

        # Update DLLInjector.ini
        core.logging.info("Updating DLLInjector.ini")
        try:
            self.replaceConfig("FileToCreate_1", " NoQuestion.bin", True)
            self.replaceConfig("CommandLine", " -inhibitbootstrap")
            self.replaceConfig("WaitForProcessTermination", " 1")
            self.replaceConfig("EnableFakeParentProcess", " 0")
            self.replaceConfig("CreateFiles", " 1")
            self.replaceConfig("FileToCreate_2", "")

            if core.config.steam_path != core.config.greenluma_path or os.path.isabs(gl_dll):
                self.replaceConfig("UseFullPathsFromIni", " 1")
                self.replaceConfig("Exe", " " + os.path.join(core.config.steam_path, "Steam.exe"))
                if os.path.isabs(gl_dll):
                    self.replaceConfig("Dll", " " + gl_dll)
                else:
                    self.replaceConfig("Dll", " " + os.path.join(core.config.greenluma_path, gl_dll))
            else:
                self.replaceConfig("UseFullPathsFromIni", " 0")
                self.replaceConfig("Exe", " Steam.exe")
                self.replaceConfig("Dll", " " + gl_dll)
        except OSError as e:
            core.logging.error("Error while modifying DLLInjector.ini")
            core.logging.exception(e)
            self.show_popup("Failed to update DLLInjector.ini, check errors.log")
            return

        if self.is_steam_running():
            core.logging.info("Closing Steam")
            self.toggle_widget(self.main_window.closing_steam)
            os.chdir(core.config.steam_path)
            try:
                subprocess.run(["Steam.exe", "-shutdown"])  # Shutdown Steam
            except OSError as e:
                core.logging.error("Error while closing Steam")
                core.logging.exception(e)
                self.toggle_widget(self.main_window.closing_steam, True)
                self.show_popup("Failed to close Steam, check errors.log")
                return
            start_time = core.time.monotonic()
            while self.is_steam_running():
                core.time.sleep(1)
                if core.time.monotonic() - start_time > 30:
                    self.toggle_widget(self.main_window.closing_steam, True)
                    self.show_popup("Timed out waiting for steam to close")
                    return
            self.toggle_widget(self.main_window.closing_steam, True)
            core.time.sleep(1)

        os.chdir(core.config.greenluma_path)
        try:
            subprocess.Popen(["DLLInjector.exe"])
            core.logging.info("Launched DLLInjector.exe, exiting")
            self.close()
        except OSError as e:
            core.logging.error("Error while launching DLLInjector.exe")
            core.logging.exception(e)
            self.show_popup("Failed to run DLLInjector.exe, check errors.log")

    def sync_applist_for_profile(self, profile, popup=False):
        self._refresh_greenluma_runtime_path()

        if not profile:
            return False

        if len(profile.games) > 168:
            logging.warning(
                "AppList : %d entrées (limite BlueLuma : 168)",
                len(profile.games),
            )

        try:
            core.createFiles(profile.games)
        except OSError as err:
            logging.exception(err)
            if popup:
                self.show_popup("Impossible de générer l'AppList. Consultez errors.log.")
            return False

        logging.info("AppList synchronisée (%d entrée(s))", len(profile.games))
        if popup:
            self.show_popup("AppList générée")
        return True

    # Util Functions
    def toggle_hidden(self, widget):
        widget.setHidden(not widget.isHidden())
        self.repaint()

    def toggle_widget(self, widget, force_close=False):
        if force_close:
            widget.setHidden(True)
            widget.setEnabled(False)
            self._sync_overlay_stack()
            return

        if widget.isHidden():
            self._layout_builder.position_overlay(widget, self.centralWidget())
            widget.setEnabled(True)
            widget.setHidden(False)
        else:
            widget.setHidden(True)
            widget.setEnabled(False)

        self._sync_overlay_stack()

    def acknowledge_manager(self):
        with core.get_config() as config:
            config.manager_msg = True
        self.hide_popup()

    def set_steam_path(self):
        path = self.main_window.steam_path.text().strip()
        if path == "":
            self.main_window.label_steam_error.setText("Veuillez saisir un chemin")
            return

        if not os.path.isdir(path):
            self.main_window.label_steam_error.setText("Chemin invalide")
            return

        if not core.is_valid_steam_path(path):
            self.main_window.label_steam_error.setText("Steam.exe introuvable dans ce dossier")
            return

        path = os.path.abspath(path)
        with core.get_config() as config:
            config.steam_path = path
            core.ensure_greenluma_path(config)

        self.main_window.settings_steam_path.setText(path)
        self.main_window.settings_greenluma_path.setText(core.get_glinject_path())
        self.sync_steam_profiles()
        self.sync_installed_steam_library()
        self.toggle_widget(self.main_window.set_steam_path_window)

    def setup_steam_path(self):
        with core.get_config() as config:
            found = core.ensure_steam_path(config)

        self.main_window.settings_steam_path.setText(core.config.steam_path)
        if found:
            return

        guess = core.detect_steam_path()
        self.main_window.steam_path.setText(guess)
        self.main_window.label_steam_error.setText(
            "Steam introuvable automatiquement. Indiquez le dossier d'installation."
            if not guess
            else ""
        )
        self.toggle_widget(self.main_window.set_steam_path_window)
        self.main_window.steam_path.setFocus()

    def set_greenluma_path(self):
        path = self.main_window.greenluma_path.text().strip()
        if path == "":
            self.main_window.label_greenluma_error.setText("Veuillez saisir un chemin")
            return

        if not os.path.isdir(path):
            self.main_window.label_greenluma_error.setText("Chemin invalide")
            return

        path = os.path.abspath(path)
        runtime = core.find_greenluma_runtime_path(path, stealth=False)
        if not core.is_valid_greenluma_path(runtime):
            self.main_window.label_greenluma_error.setText("DLLInjector.exe introuvable dans ce dossier")
            return

        with core.get_config() as config:
            config.greenluma_path = runtime

        self.main_window.settings_greenluma_path.setText(core.get_glinject_path())
        self.toggle_widget(self.main_window.set_greenluma_path_window)

    def setup_greenluma_path(self):
        with core.get_config() as config:
            core.ensure_greenluma_path(config)

        self.main_window.settings_greenluma_path.setText(core.get_glinject_path())

    def drop_event_handler(self, event):
        self.add_selected()

    def hide_popup(self, event=None):
        self.toggle_widget(self.main_window.generic_popup, True)

    def show_popup(self, message, ok_callback=None, cx_callback=None):
        self.main_window.popup_text.setText(message)
        if ok_callback is None:
            ok_callback = self.hide_popup
        if cx_callback is None:
            cx_callback = self.hide_popup
        # Remove old callbacks
        try:
            self.main_window.popup_btn1.clicked.disconnect()
        except TypeError:
            pass
        try:
            self.main_window.popup_btn2.clicked.disconnect()
        except TypeError:
            pass
        self.main_window.popup_btn1.clicked.connect(ok_callback)
        self.main_window.popup_btn2.clicked.connect(cx_callback)

        self.toggle_widget(self.main_window.generic_popup)
        self.main_window.popup_btn1.setFocus()

    def is_steam_running(self):
        for process in psutil.process_iter():
            if process.name() == "Steam.exe" or process.name() == "SteamService.exe" or process.name() == "steamwebhelper.exe" or process.name() == "DLLInjector.exe":
                return True

        return False

    def replaceConfig(self, name, new_value, append=False):
        found = False
        ini_path = os.path.join(core.config.greenluma_path, "DLLInjector.ini")
        with fileinput.input(ini_path, inplace=True) as fp:
            for line in fp:
                data = line
                if "#" in data:
                    data = data.split("#", 1)[0]
                if "=" in data:
                    tokens = data.split("=", 1)
                    if tokens[0].strip() == name:
                        found = True
                        tokens[1] = new_value
                        line = "=".join(tokens) + "\n"
                print(line, end="")

        if append and not found:
            with open(ini_path, "at") as f:
                f.write("\n{0} = {1}".format(name, new_value))


class SteamRestoreThread(QThread):
    signal = pyqtSignal("PyQt_PyObject")

    def run(self):
        try:
            core.perform_steam_restore()
            self.signal.emit(True)
        except Exception as err:
            self.signal.emit(err)


class SteamDowngradeThread(QThread):
    signal = pyqtSignal("PyQt_PyObject")

    def __init__(self, raw_url):
        super().__init__()
        self.raw_url = raw_url

    def run(self):
        try:
            package_url = core.perform_steam_downgrade(self.raw_url)
            self.signal.emit(package_url)
        except Exception as err:
            self.signal.emit(err)


class ExtractGreenLumaThread(QThread):
    signal = pyqtSignal("PyQt_PyObject")

    def __init__(self, zip_path):
        super().__init__()
        self.zip_path = zip_path

    def run(self):
        try:
            core.extract_greenluma_archive(self.zip_path)
            self.signal.emit(True)
        except Exception as err:
            self.signal.emit(err)


class ImportSteamLibraryThread(QThread):
    signal = pyqtSignal("PyQt_PyObject")

    def __init__(self, steam_path):
        super(ImportSteamLibraryThread, self).__init__()
        self.steam_path = steam_path

    def run(self):
        try:
            result = core.get_installed_games_with_extensions(self.steam_path)
            self.signal.emit(result)
        except Exception as err:
            logging.exception(err)
            self.signal.emit(err)


class EditorTableModel(QAbstractTableModel):
    HEADERS = ["ID", "Nom", "Type", ""]
    TYPES = ("Game", "DLC")
    TYPE_PLACEHOLDER = "Choisir"
    FIELD_PLACEHOLDERS = {
        0: "Saisir l'ID Steam",
        1: "Saisir le nom",
    }
    ACTION_COLUMN = 3

    def __init__(self, rows=None, parent=None):
        super().__init__(parent=parent)
        self.rows = rows or []

    def rowCount(self, parent=QModelIndex()):
        return len(self.rows)

    def columnCount(self, parent=QModelIndex()):
        return 4

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        if index.column() == self.ACTION_COLUMN:
            return QVariant()
        if role in (Qt.DisplayRole, Qt.EditRole):
            value = self.rows[index.row()][index.column()]
            if index.column() == 2 and role == Qt.DisplayRole:
                return value if value in self.TYPES else self.TYPE_PLACEHOLDER
            return value
        if index.column() == 2 and role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid() or role != Qt.EditRole:
            return False
        if index.column() == self.ACTION_COLUMN:
            return False
        value = str(value).strip()
        if index.column() == 2:
            if value == self.TYPE_PLACEHOLDER:
                value = ""
            elif value not in self.TYPES:
                value = ""
        self.rows[index.row()][index.column()] = value
        self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
        return True

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.HEADERS[section]
        return QVariant()

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        if index.column() == self.ACTION_COLUMN:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def add_row(self, app_id="", name="", app_type=""):
        row = len(self.rows)
        self.beginInsertRows(QModelIndex(), row, row)
        stored_type = app_type if app_type in self.TYPES else ""
        self.rows.append([app_id, name, stored_type])
        self.endInsertRows()

    def remove_rows(self, row_indices):
        for row in sorted(set(row_indices), reverse=True):
            if row < 0 or row >= len(self.rows):
                continue
            self.beginRemoveRows(QModelIndex(), row, row)
            del self.rows[row]
            self.endRemoveRows()


class EditorTableHeader(QHeaderView):
    """Bouton + dans l'en-tête de la dernière colonne ; les lignes n'ont que la croix."""
    add_row_clicked = pyqtSignal()
    ACTION_COLUMN = 3
    ADD_BTN_SIZE = 22

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setSectionsClickable(False)
        self._add_btn = QToolButton(self)
        self._add_btn.setText("+")
        self._add_btn.setObjectName("editor_header_add_btn")
        self._add_btn.setCursor(Qt.PointingHandCursor)
        self._add_btn.setToolTip("Ajouter une ligne")
        self._add_btn.clicked.connect(self.add_row_clicked.emit)
        self.sectionResized.connect(self._reposition_add_btn)
        self.geometriesChanged.connect(self._reposition_add_btn)

    def showEvent(self, event):
        super().showEvent(event)
        self._reposition_add_btn()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reposition_add_btn()

    def _reposition_add_btn(self, *_args):
        if self.count() <= self.ACTION_COLUMN:
            self._add_btn.hide()
            return
        x = self.sectionViewportPosition(self.ACTION_COLUMN)
        width = self.sectionSize(self.ACTION_COLUMN)
        btn_w = btn_h = self.ADD_BTN_SIZE
        y = max(0, (self.height() - btn_h) // 2)
        self._add_btn.setFixedSize(btn_w, btn_h)
        self._add_btn.move(x + (width - btn_w) // 2, y)
        self._add_btn.raise_()
        self._add_btn.show()


class DeleteRowDelegate(QStyledItemDelegate):
    delete_clicked = pyqtSignal(int)

    def paint(self, painter, option, index):
        painter.save()
        if option.state & QStyle.State_MouseOver:
            painter.fillRect(option.rect, QColor(Colors.SURFACE_ELEVATED))
        painter.setPen(QColor(Colors.DANGER))
        font = painter.font()
        font.setPointSize(font.pointSize() + 2)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(option.rect, Qt.AlignCenter, "×")
        painter.restore()

    def editorEvent(self, event, model, option, index):
        if event.type() not in (QEvent.MouseButtonPress, QEvent.MouseButtonRelease):
            return False
        if event.button() != Qt.LeftButton:
            return False
        hit_rect = option.rect.adjusted(-4, -2, 4, 2)
        if not hit_rect.contains(event.pos()):
            return False
        if event.type() == QEvent.MouseButtonRelease:
            self.delete_clicked.emit(index.row())
            return True
        return True


class CellEditorDelegate(QStyledItemDelegate):
    PLACEHOLDERS = EditorTableModel.FIELD_PLACEHOLDERS
    MARGIN_H = 4
    MARGIN_V = 3

    def _cell_text(self, index):
        value = str(index.data(Qt.EditRole) or "").strip()
        if value:
            return value
        return self.PLACEHOLDERS.get(index.column(), "")

    def _is_placeholder(self, index):
        value = str(index.data(Qt.EditRole) or "").strip()
        return not value and index.column() in self.PLACEHOLDERS

    def paint(self, painter, option, index):
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        options.text = self._cell_text(index)
        if self._is_placeholder(index):
            options.palette.setColor(QPalette.Text, QColor(Colors.TEXT_DIM))
        widget = option.widget
        if widget:
            widget.style().drawControl(QStyle.CE_ItemViewItem, options, painter, widget)

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setFrame(False)
        editor.setObjectName("editor_cell_input")
        placeholder = self.PLACEHOLDERS.get(index.column())
        if placeholder:
            editor.setPlaceholderText(placeholder)
        return editor

    def setEditorData(self, editor, index):
        value = index.data(Qt.EditRole)
        editor.setText(str(value) if value else "")

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(
            option.rect.adjusted(self.MARGIN_H, self.MARGIN_V, -self.MARGIN_H, -self.MARGIN_V)
        )

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        return QSize(size.width(), 36)


class TypeDelegate(QStyledItemDelegate):
    TYPES = EditorTableModel.TYPES
    PLACEHOLDER = EditorTableModel.TYPE_PLACEHOLDER
    MARGIN_H = 4
    MARGIN_V = 3

    def _display_text(self, index):
        value = index.data(Qt.EditRole)
        if value in self.TYPES:
            return value
        return self.PLACEHOLDER

    def paint(self, painter, option, index):
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        options.text = self._display_text(index)
        if options.text == self.PLACEHOLDER:
            options.palette.setColor(QPalette.Text, QColor(Colors.TEXT_DIM))
        options.displayAlignment = Qt.AlignCenter
        widget = option.widget
        if widget:
            widget.style().drawControl(QStyle.CE_ItemViewItem, options, painter, widget)

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.setObjectName("editor_cell_combo")
        editor.addItems(list(self.TYPES))
        current = index.data(Qt.EditRole)
        if current in self.TYPES:
            editor.setCurrentText(current)
        else:
            editor.setCurrentIndex(-1)
        QTimer.singleShot(0, editor.showPopup)
        return editor

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(
            option.rect.adjusted(self.MARGIN_H, self.MARGIN_V, -self.MARGIN_H, -self.MARGIN_V)
        )

    def sizeHint(self, option, index):
        return QSize(option.rect.width(), 36)

    def setEditorData(self, editor, index):
        current = index.data(Qt.EditRole)
        if current in self.TYPES:
            editor.setCurrentText(current)
        else:
            editor.setCurrentIndex(-1)

    def setModelData(self, editor, model, index):
        text = editor.currentText()
        if text in self.TYPES:
            model.setData(index, text, Qt.EditRole)
