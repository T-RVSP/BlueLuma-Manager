"""Réorganisation de l'interface en layouts Qt responsifs."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


def _card(parent=None) -> QFrame:
    frame = QFrame(parent)
    frame.setObjectName("card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(12)
    return frame, layout


class ModernLayoutBuilder:
  """Replace les positions absolues par des layouts après setupUi."""

  SIDEBAR_WIDTH = 300

  def __init__(self, ui):
    self.ui = ui

  def build(self, window: QWidget) -> QWidget:
    central = window.centralWidget()
    central.setStyleSheet("")

    if central.layout() is None:
      central_layout = QVBoxLayout(central)
      central_layout.setContentsMargins(0, 0, 0, 0)
      central_layout.setSpacing(0)
      central_layout.addWidget(self.ui.main_panel)

    window.setStyleSheet("")
    self._build_main_panel()
    self._style_overlays()
    self._build_overlay_layouts(window.centralWidget())
    self._create_greenluma_install_overlay(window.centralWidget())
    self._create_steam_downgrade_overlay(window.centralWidget())

  def _build_main_panel(self):
    panel = self.ui.main_panel
    panel.setObjectName("main_panel")

    root = QVBoxLayout(panel)
    root.setContentsMargins(20, 16, 20, 16)
    root.setSpacing(14)

    # --- En-tête ---
    header = QHBoxLayout()
    header.setSpacing(12)
    header.addStretch(1)
    header.addWidget(self.ui.label_main, 0, Qt.AlignCenter)
    header.addStretch(1)
    header_meta = QHBoxLayout()
    header_meta.setSpacing(8)
    header_meta.setContentsMargins(0, 0, 0, 0)
    self.author_label = QLabel("Développé par ShyninG")
    self.author_label.setObjectName("author_label")
    header_meta.addWidget(self.author_label)
    header_meta.addWidget(self.ui.version_label)
    meta_widget = QWidget()
    meta_widget.setLayout(header_meta)
    header.addWidget(meta_widget, 0, Qt.AlignVCenter | Qt.AlignRight)
    root.addLayout(header)

    # --- Contenu principal : recherche | profil ---
    content = QHBoxLayout()
    content.setSpacing(16)

    left_card, left_layout = _card()
    left_layout.setContentsMargins(16, 16, 16, 12)

    self.editor_label = QLabel("Éditeur — jeux / DLC non détectés")
    self.editor_label.setObjectName("label_editor")
    left_layout.addWidget(self.editor_label)

    editor_toolbar = QHBoxLayout()
    editor_toolbar.setSpacing(8)
    action_btn_width = (self.SIDEBAR_WIDTH - 32 - 8) // 2
    self.ui.add_to_profile.setStyleSheet("")
    self.ui.add_to_profile.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    self.ui.add_to_profile.setMinimumHeight(36)
    self.ui.add_to_profile.setMaximumHeight(36)
    self.ui.add_to_profile.setMinimumWidth(action_btn_width)
    self.ui.add_to_profile.setMaximumWidth(action_btn_width)
    editor_toolbar.addWidget(self.ui.add_to_profile)
    editor_toolbar.addStretch(1)
    self.ui.settings_btn.setStyleSheet("")
    self.ui.settings_btn.setFixedSize(36, 36)
    editor_toolbar.addWidget(self.ui.settings_btn, 0, Qt.AlignVCenter)
    left_layout.addLayout(editor_toolbar)

    self.ui.search_result.setObjectName("editor_table")
    self.ui.search_result.setDragEnabled(False)
    self.ui.search_result.setSortingEnabled(False)
    left_layout.addWidget(self.ui.search_result, 1)

    self.ui.game_search_text.hide()
    self.ui.search_btn.hide()
    self.ui.searching_frame.hide()

    content.addWidget(left_card, 1)

    right_card, right_layout = _card()
    right_layout.setContentsMargins(16, 16, 16, 12)
    right_card.setFixedWidth(self.SIDEBAR_WIDTH)

    right_layout.addWidget(self.ui.label_profile)
    right_layout.addWidget(self.ui.profile_selector)

    self.ui.create_profile.hide()
    self.ui.delete_profile.hide()

    right_layout.addWidget(self.ui.label_games_list)
    right_layout.addWidget(self.ui.games_list, 1)

    profile_actions = QHBoxLayout()
    profile_actions.setSpacing(8)
    for btn in (self.ui.run_GreenLuma_btn, self.ui.remove_game):
      btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
      btn.setMinimumHeight(36)
      btn.setStyleSheet("")
    profile_actions.addWidget(self.ui.run_GreenLuma_btn, 1)
    profile_actions.addWidget(self.ui.remove_game, 1)
    right_layout.addLayout(profile_actions)

    self.ui.games_list.setStyleSheet("")
    self.ui.games_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    content.addWidget(right_card, 0)
    root.addLayout(content, 1)

    self.ui.label_main.setText("BlueLuma Manager")
    self.ui.no_hook_checkbox.hide()
    self.ui.generate_btn.hide()

  def _strip_legacy_styles(self, root: QWidget):
    """Supprime les styles inline blancs hérités de gui.ui."""
    root.setStyleSheet("")
    for child in root.findChildren(QWidget):
      child.setStyleSheet("")

  def _style_overlays(self):
    overlays = [
      self.ui.profile_create_window,
      self.ui.set_steam_path_window,
      self.ui.set_greenluma_path_window,
      self.ui.generic_popup,
      self.ui.closing_steam,
      self.ui.settings_window,
    ]
    for widget in overlays:
      widget.setObjectName("overlay_panel")
      self._strip_legacy_styles(widget)

    for widget in (
      self.ui.profile_name,
      self.ui.steam_path,
      self.ui.greenluma_path,
      self.ui.settings_steam_path,
      self.ui.settings_greenluma_path,
      self.ui.profile_selector,
      self.ui.popup_text,
    ):
      widget.setStyleSheet("")

  def _create_greenluma_install_overlay(self, central: QWidget):
    panel = QWidget(central)
    panel.setObjectName("overlay_panel")
    panel.hide()

    title = QLabel("BlueLuma introuvable")
    title.setObjectName("label_greenluma_install_title")

    text = QLabel()
    text.setObjectName("greenluma_install_text")
    text.setWordWrap(True)
    text.setAlignment(Qt.AlignLeft | Qt.AlignTop)
    text.setText(
      "DLLInjector.exe est absent du dossier GLinject.\n\n"
      "Téléchargez BlueLuma 2026 sur cs.rin.ru, puis sélectionnez l'archive ZIP "
      "téléchargée pour l'installer automatiquement (mot de passe : cs.rin.ru)."
    )

    download_btn = QPushButton("Télécharger sur cs.rin.ru")
    download_btn.setObjectName("greenluma_install_download_btn")
    download_btn.setCursor(Qt.PointingHandCursor)

    select_zip_btn = QPushButton("Sélectionner le ZIP téléchargé")
    select_zip_btn.setObjectName("greenluma_install_zip_btn")
    select_zip_btn.setCursor(Qt.PointingHandCursor)

    status = QLabel("")
    status.setObjectName("greenluma_install_status")
    status.setWordWrap(True)

    cancel_btn = QPushButton("Annuler")
    cancel_btn.setObjectName("greenluma_install_cancel_btn")
    cancel_btn.setCursor(Qt.PointingHandCursor)

    layout = QVBoxLayout(panel)
    layout.setContentsMargins(24, 24, 24, 24)
    layout.setSpacing(14)
    layout.addWidget(title)
    layout.addWidget(text)
    layout.addWidget(download_btn)
    layout.addWidget(select_zip_btn)
    layout.addWidget(status)
    layout.addStretch(1)
    cancel_row = QHBoxLayout()
    cancel_row.addStretch(1)
    cancel_row.addWidget(cancel_btn)
    layout.addLayout(cancel_row)

    panel.setMinimumWidth(460)
    panel.setMaximumWidth(560)

    self.ui.greenluma_install_window = panel
    self.ui.greenluma_install_title = title
    self.ui.greenluma_install_text = text
    self.ui.greenluma_install_download_btn = download_btn
    self.ui.greenluma_install_select_zip_btn = select_zip_btn
    self.ui.greenluma_install_status = status
    self.ui.greenluma_install_cancel_btn = cancel_btn

  def _create_steam_downgrade_overlay(self, central: QWidget):
    panel = QFrame(central)
    panel.setObjectName("overlay_panel")
    panel.hide()

    title = QLabel("Downgrade Steam")
    title.setObjectName("label_steam_downgrade_title")

    subtitle = QLabel(
      "Installez une version antérieure de Steam via une capture Wayback Machine."
    )
    subtitle.setObjectName("overlay_subtitle")
    subtitle.setWordWrap(True)

    step1, step1_layout = self._settings_section("Étape 1 — Snapshot Wayback")
    step1_help = QLabel(
      "Ouvrez le calendrier, sélectionnez un jour (point bleu), puis clic droit "
      "sur l'heure de capture → Copier l'adresse du lien."
    )
    step1_help.setObjectName("steam_downgrade_help")
    step1_help.setWordWrap(True)

    wayback_btn = QPushButton("Ouvrir Wayback Machine")
    wayback_btn.setObjectName("steam_downgrade_wayback_btn")
    wayback_btn.setCursor(Qt.PointingHandCursor)

    step1_layout.addWidget(step1_help)
    step1_layout.addWidget(wayback_btn)

    step2, step2_layout = self._settings_section("Étape 2 — URL de la version")
    url_input = QLineEdit()
    url_input.setObjectName("steam_downgrade_url_input")
    url_input.setPlaceholderText(
      "https://web.archive.org/web/20251015123000/http://media.steampowered.com/"
    )

    preview_box = QFrame()
    preview_box.setObjectName("downgrade_preview_box")
    preview_layout = QVBoxLayout(preview_box)
    preview_layout.setContentsMargins(12, 10, 12, 10)
    preview_layout.setSpacing(6)

    preview_caption = QLabel("Aperçu transformé")
    preview_caption.setObjectName("steam_downgrade_field_label")

    url_preview = QLabel("Collez une URL ci-dessus pour voir l'aperçu transformé…")
    url_preview.setObjectName("steam_downgrade_url_preview")
    url_preview.setProperty("empty", True)
    url_preview.setWordWrap(True)
    url_preview.setTextInteractionFlags(Qt.TextSelectableByMouse)

    preview_layout.addWidget(preview_caption)
    preview_layout.addWidget(url_preview)

    step2_layout.addWidget(url_input)
    step2_layout.addWidget(preview_box)

    status = QLabel("")
    status.setObjectName("steam_downgrade_status")
    status.setWordWrap(True)

    cancel_btn = QPushButton("Annuler")
    cancel_btn.setObjectName("steam_downgrade_cancel_btn")
    cancel_btn.setCursor(Qt.PointingHandCursor)

    launch_btn = QPushButton("Lancer le downgrade")
    launch_btn.setObjectName("steam_downgrade_launch_btn")
    launch_btn.setCursor(Qt.PointingHandCursor)

    content = QWidget()
    content.setObjectName("steam_downgrade_content")
    body = QVBoxLayout(content)
    body.setContentsMargins(24, 22, 24, 16)
    body.setSpacing(14)
    body.addWidget(title)
    body.addWidget(subtitle)
    body.addWidget(step1)
    body.addWidget(step2)
    body.addWidget(status)

    footer = QHBoxLayout()
    footer.setContentsMargins(20, 14, 20, 18)
    footer.setSpacing(10)
    footer.addWidget(cancel_btn, 1)
    footer.addWidget(launch_btn, 2)

    root = QVBoxLayout(panel)
    root.setContentsMargins(0, 0, 0, 0)
    root.setSpacing(0)
    root.addWidget(content, 1)

    footer_widget = QWidget()
    footer_widget.setObjectName("overlay_footer")
    footer_widget.setLayout(footer)
    root.addWidget(footer_widget)

    panel.setMinimumWidth(500)
    panel.setMaximumWidth(520)
    panel.setMinimumHeight(500)
    panel.setMaximumHeight(560)

    self.ui.steam_downgrade_window = panel
    self.ui.steam_downgrade_title = title
    self.ui.steam_downgrade_subtitle = subtitle
    self.ui.steam_downgrade_help = step1_help
    self.ui.steam_downgrade_wayback_btn = wayback_btn
    self.ui.steam_downgrade_url_input = url_input
    self.ui.steam_downgrade_url_preview = url_preview
    self.ui.steam_downgrade_launch_btn = launch_btn
    self.ui.steam_downgrade_status = status
    self.ui.steam_downgrade_cancel_btn = cancel_btn

  def _build_overlay_layouts(self, central: QWidget):
    self._configure_form_overlay(
      self.ui.profile_create_window,
      self.ui.label_profile_name,
      [self.ui.profile_name],
      [self.ui.create_profile_btn, self.ui.cancel_profile_btn],
    )
    self._configure_form_overlay(
      self.ui.set_steam_path_window,
      self.ui.label_steam_path,
      [self.ui.steam_path, self.ui.label_steam_error],
      [self.ui.save_steam_path, self.ui.cancel_steam_path_btn],
    )
    self._configure_form_overlay(
      self.ui.set_greenluma_path_window,
      self.ui.label_greenluma_path,
      [self.ui.greenluma_path, self.ui.label_greenluma_error],
      [self.ui.save_greenluma_path, self.ui.cancel_greenluma_path_btn],
    )
    self._configure_settings_overlay()
    self._configure_popup_overlay()
    self._configure_closing_overlay()

    for widget in (
      self.ui.profile_create_window,
      self.ui.set_steam_path_window,
      self.ui.set_greenluma_path_window,
      self.ui.generic_popup,
      self.ui.closing_steam,
      self.ui.settings_window,
    ):
      widget.setMinimumWidth(420)
      widget.setMaximumWidth(640)

  def _clear_layout(self, widget: QWidget):
    if widget.layout():
      while widget.layout().count():
        item = widget.layout().takeAt(0)
        if item.widget():
          item.widget().setParent(widget)

  def _configure_form_overlay(self, panel, title_label, fields, buttons):
    self._strip_legacy_styles(panel)
    self._clear_layout(panel)
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(24, 24, 24, 24)
    layout.setSpacing(14)
    title_label.setStyleSheet("")
    layout.addWidget(title_label)
    for field in fields:
      self._prepare_widget_for_layout(field)
      layout.addWidget(field)
    layout.addStretch(1)
    btn_row = QHBoxLayout()
    btn_row.setSpacing(12)
    for btn in buttons:
      self._prepare_widget_for_layout(btn)
      btn_row.addWidget(btn, 1)
    layout.addLayout(btn_row)

  def _prepare_widget_for_layout(self, widget: QWidget):
    """Retire les géométries absolues héritées de gui.ui pour éviter les chevauchements."""
    widget.setStyleSheet("")
    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    if isinstance(widget, QLineEdit):
      widget.setMinimumHeight(36)

  def _settings_section(self, title: str, parent=None):
    frame = QFrame(parent)
    frame.setObjectName("settings_section")
    section_layout = QVBoxLayout(frame)
    section_layout.setContentsMargins(14, 12, 14, 12)
    section_layout.setSpacing(10)
    heading = QLabel(title)
    heading.setObjectName("settings_section_title")
    section_layout.addWidget(heading)
    return frame, section_layout

  def _scrollable_overlay(self, panel: QWidget, content: QWidget, footer_layout=None):
    root = QVBoxLayout(panel)
    root.setContentsMargins(0, 0, 0, 0)
    root.setSpacing(0)

    scroll = QScrollArea()
    scroll.setObjectName("overlay_scroll")
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    scroll.setWidget(content)
    root.addWidget(scroll, 1)

    if footer_layout is not None:
      footer = QWidget()
      footer.setObjectName("overlay_footer")
      footer.setLayout(footer_layout)
      root.addWidget(footer)

  def _ensure_settings_steam_widgets(self):
    if hasattr(self.ui, "settings_steam_downgrade_btn"):
      return

    self.ui.settings_label_steam_version = QLabel("Version Steam")
    self.ui.settings_label_steam_version.setObjectName("settings_label_steam_version")
    self.ui.settings_label_steam_version.hide()

    self.ui.settings_steam_cfg_status = QLabel("")
    self.ui.settings_steam_cfg_status.setObjectName("settings_steam_cfg_status")
    self.ui.settings_steam_cfg_status.setWordWrap(True)

    self.ui.settings_steam_downgrade_btn = QPushButton("Downgrade Steam…")
    self.ui.settings_steam_downgrade_btn.setObjectName("settings_steam_downgrade_btn")
    self.ui.settings_steam_downgrade_btn.setCursor(Qt.PointingHandCursor)

    self.ui.settings_steam_restore_btn = QPushButton("Restaurer Steam (dernière version)")
    self.ui.settings_steam_restore_btn.setObjectName("settings_steam_restore_btn")
    self.ui.settings_steam_restore_btn.setCursor(Qt.PointingHandCursor)

  def _configure_settings_overlay(self):
    panel = self.ui.settings_window
    self._ensure_settings_steam_widgets()
    self._strip_legacy_styles(panel)
    self._clear_layout(panel)

    for widget in (
      self.ui.settings_label_main,
      self.ui.settings_label_steam,
      self.ui.settings_steam_path,
      self.ui.settings_label_greenluma,
      self.ui.settings_greenluma_path,
      self.ui.settings_label_steam_version,
      self.ui.settings_steam_cfg_status,
      self.ui.settings_steam_downgrade_btn,
      self.ui.settings_steam_restore_btn,
      self.ui.update_checkbox,
      self.ui.settings_cancel_btn,
    ):
      self._prepare_widget_for_layout(widget)

    self.ui.settings_save_btn.hide()

    layout = QVBoxLayout(panel)
    layout.setContentsMargins(24, 20, 24, 16)
    layout.setSpacing(16)

    layout.addWidget(self.ui.settings_label_main)

    paths_section, paths_layout = self._settings_section("Chemins")
    paths_layout.addWidget(self.ui.settings_label_steam)
    paths_layout.addWidget(self.ui.settings_steam_path)
    paths_layout.addWidget(self.ui.settings_label_greenluma)
    paths_layout.addWidget(self.ui.settings_greenluma_path)
    layout.addWidget(paths_section)

    steam_section, steam_layout = self._settings_section("Version Steam")
    steam_layout.addWidget(self.ui.settings_steam_cfg_status)
    steam_actions = QHBoxLayout()
    steam_actions.setSpacing(10)
    steam_actions.addWidget(self.ui.settings_steam_downgrade_btn, 1)
    steam_actions.addWidget(self.ui.settings_steam_restore_btn, 1)
    steam_layout.addLayout(steam_actions)
    layout.addWidget(steam_section)

    app_section, app_layout = self._settings_section("Application")
    app_layout.addWidget(self.ui.update_checkbox)
    layout.addWidget(app_section)

    footer = QHBoxLayout()
    footer.addStretch(1)
    footer.addWidget(self.ui.settings_cancel_btn)
    layout.addLayout(footer)

    panel.setMinimumWidth(500)
    panel.setMaximumWidth(540)
    panel.setMinimumHeight(400)
    panel.setMaximumHeight(540)

  def _configure_popup_overlay(self):
    panel = self.ui.generic_popup
    self._clear_layout(panel)
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(24, 24, 24, 24)
    layout.setSpacing(16)
    layout.addWidget(self.ui.popup_text, 1)
    btn_row = QHBoxLayout()
    btn_row.setSpacing(12)
    btn_row.addWidget(self.ui.popup_btn1, 1)
    btn_row.addWidget(self.ui.popup_btn2, 1)
    layout.addLayout(btn_row)

  def _configure_closing_overlay(self):
    panel = self.ui.closing_steam
    self._clear_layout(panel)
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(32, 32, 32, 32)
    layout.addWidget(self.ui.label_close_steam, 0, Qt.AlignCenter)

  def position_overlay(self, panel: QWidget, central: QWidget):
    panel.adjustSize()
    max_w = panel.maximumWidth() if panel.maximumWidth() > 0 else 540
    min_w = panel.minimumWidth() if panel.minimumWidth() > 0 else 420
    max_h = min(panel.maximumHeight() if panel.maximumHeight() > 0 else 680, central.height() - 40)
    min_h = panel.minimumHeight() if panel.minimumHeight() > 0 else 320

    w = min(max(panel.sizeHint().width(), min_w), max_w)
    h = min(max(panel.sizeHint().height(), min_h), max_h)
    panel.resize(w, h)
    panel.move(max(0, (central.width() - w) // 2), max(0, (central.height() - h) // 2))

  def sync_overlay_stack(self, overlays) -> None:
    """Place les modales au-dessus du contenu principal."""
    visible = [w for w in overlays if not w.isHidden()]

    if visible:
      self.ui.main_panel.lower()
      for widget in visible:
        widget.setEnabled(True)
        widget.raise_()
    else:
      self.ui.main_panel.raise_()
