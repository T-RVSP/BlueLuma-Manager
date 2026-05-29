"""Design system et feuille de style globale pour BlueLuma Manager."""

from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtWidgets import QApplication


class Colors:
    BG = "#0c1017"
    SURFACE = "#151b26"
    SURFACE_ELEVATED = "#1e2736"
    CARD = "#1a2230"
    BORDER = "#2a3548"
    BORDER_FOCUS = "#3dd68c"
    TEXT = "#eef2f8"
    TEXT_MUTED = "#8b9ab5"
    TEXT_DIM = "#5c6b82"
    ACCENT = "#3dd68c"
    ACCENT_HOVER = "#62e8a4"
    ACCENT_PRESSED = "#2eb872"
    PRIMARY = "#4c9aff"
    PRIMARY_HOVER = "#6eb0ff"
    DANGER = "#f07178"
    DANGER_HOVER = "#ff8a90"
    OPERA_RED = "#fa1e4e"
    OPERA_RED_HOVER = "#ff4769"
    OPERA_RED_PRESSED = "#d0163d"
    INPUT_BG = "#0f141c"
    OVERLAY = "rgba(8, 12, 18, 0.72)"


FONT_FAMILY = "Segoe UI"
FONT_MONO = "Cascadia Mono, Consolas, monospace"


def app_stylesheet() -> str:
    c = Colors
    return f"""
QMainWindow, QWidget#centralwidget {{
    background-color: {c.BG};
    color: {c.TEXT};
    font-family: "{FONT_FAMILY}";
    font-size: 10pt;
}}

QLabel#label_main {{
    font-size: 15pt;
    font-weight: 600;
    color: {c.TEXT};
    letter-spacing: 0.3px;
}}

QLabel#label_profile, QLabel#label_games_list, QLabel#label_editor,
QLabel#label_profile_name, QLabel#label_steam_path,
QLabel#label_greenluma_path, QLabel#settings_label_steam,
QLabel#settings_label_greenluma {{
    font-size: 9pt;
    font-weight: 600;
    color: {c.TEXT_MUTED};
    text-transform: uppercase;
    letter-spacing: 0.8px;
}}

QLabel#version_label, QLabel#author_label {{
    font-size: 8pt;
    color: {c.TEXT_DIM};
}}

QLabel#settings_label_main {{
    color: {c.TEXT};
    font-size: 13pt;
    font-weight: 700;
    padding-bottom: 4px;
}}

QFrame#settings_section {{
    background-color: {c.CARD};
    border: 1px solid {c.BORDER};
    border-radius: 10px;
}}

QLabel#settings_section_title {{
    color: {c.TEXT_MUTED};
    font-size: 9pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}}

QScrollArea#overlay_scroll {{
    background: transparent;
    border: none;
}}

QWidget#overlay_footer {{
    background-color: {c.SURFACE_ELEVATED};
    border-top: 1px solid {c.BORDER};
}}

QLabel#steam_downgrade_field_label {{
    color: {c.TEXT_MUTED};
    font-size: 9pt;
    font-weight: 600;
}}

QLabel#popup_text, QLabel#label_close_steam, QLabel#label_searching {{
    color: {c.TEXT};
}}

QLabel#label_steam_error, QLabel#label_greenluma_error {{
    color: {c.DANGER};
    font-size: 9pt;
}}

QWidget#card, QFrame#card {{
    background-color: {c.CARD};
    border: 1px solid {c.BORDER};
    border-radius: 12px;
}}

QWidget#overlay_panel, QFrame#overlay_panel {{
    background-color: {c.SURFACE_ELEVATED};
    border: 1px solid {c.BORDER};
    border-radius: 14px;
}}

QWidget#overlay_backdrop {{
    background-color: {c.OVERLAY};
}}

QLineEdit, QComboBox {{
    background-color: {c.INPUT_BG};
    color: {c.TEXT};
    border: 1px solid {c.BORDER};
    border-radius: 8px;
    padding: 8px 12px;
    min-height: 20px;
    font-family: "{FONT_MONO}";
    font-size: 9pt;
    selection-background-color: {c.ACCENT};
    selection-color: {c.BG};
}}

QLineEdit:focus, QComboBox:focus {{
    border-color: {c.BORDER_FOCUS};
}}

QComboBox::drop-down {{
    border: none;
    width: 28px;
}}

QComboBox::down-arrow {{
    image: url(:/images/down-arrow.png);
    width: 14px;
    height: 14px;
}}

QComboBox QAbstractItemView {{
    background-color: {c.SURFACE_ELEVATED};
    color: {c.TEXT};
    border: 1px solid {c.BORDER};
    border-radius: 8px;
    padding: 4px;
    selection-background-color: {c.ACCENT};
    selection-color: {c.BG};
}}

QPushButton {{
    background-color: {c.SURFACE_ELEVATED};
    color: {c.TEXT};
    border: 1px solid {c.BORDER};
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
    min-height: 18px;
}}

QPushButton:hover {{
    background-color: {c.BORDER};
    border-color: {c.TEXT_MUTED};
}}

QPushButton:pressed {{
    background-color: {c.SURFACE};
}}

QPushButton#generate_btn {{
    background-color: {c.ACCENT};
    color: {c.BG};
    border: none;
    font-weight: 600;
    font-size: 10pt;
    border-radius: 10px;
    min-height: 44px;
}}

QPushButton#generate_btn:hover {{
    background-color: {c.ACCENT_HOVER};
}}

QPushButton#generate_btn:pressed {{
    background-color: {c.ACCENT_PRESSED};
}}

QPushButton#add_to_profile,
QPushButton#run_GreenLuma_btn,
QPushButton#remove_game {{
    min-height: 36px;
    max-height: 36px;
    padding: 8px 12px;
    font-size: 9pt;
    font-weight: 600;
    border-radius: 8px;
}}

QPushButton#add_to_profile {{
    background-color: {c.ACCENT};
    color: {c.BG};
    border: none;
}}

QPushButton#add_to_profile:hover {{
    background-color: {c.ACCENT_HOVER};
}}

QPushButton#add_to_profile:pressed {{
    background-color: {c.ACCENT_PRESSED};
}}

QPushButton#run_GreenLuma_btn {{
    background-color: {c.PRIMARY};
    color: {c.BG};
    border: none;
}}

QPushButton#run_GreenLuma_btn:hover {{
    background-color: {c.PRIMARY_HOVER};
}}

QPushButton#remove_game {{
    background-color: {c.OPERA_RED};
    color: #ffffff;
    border: none;
}}

QPushButton#remove_game:hover {{
    background-color: {c.OPERA_RED_HOVER};
}}

QPushButton#remove_game:pressed {{
    background-color: {c.OPERA_RED_PRESSED};
}}

QPushButton#delete_profile {{
    color: {c.DANGER};
    border-color: {c.DANGER};
}}

QPushButton#delete_profile:hover {{
    background-color: {c.DANGER};
    color: {c.BG};
}}

QPushButton#search_btn {{
    background-color: {c.ACCENT};
    border: none;
    border-radius: 8px;
    min-width: 40px;
    max-width: 40px;
    padding: 4px;
}}

QPushButton#search_btn:hover {{
    background-color: {c.ACCENT_HOVER};
}}

QPushButton#settings_btn {{
    background-color: transparent;
    border: 1px solid {c.BORDER};
    border-radius: 8px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    padding: 4px;
}}

QPushButton#settings_btn:hover {{
    background-color: {c.SURFACE_ELEVATED};
    border-color: {c.ACCENT};
}}

QPushButton#greenluma_install_download_btn,
QPushButton#greenluma_install_zip_btn,
QPushButton#settings_steam_downgrade_btn,
QPushButton#steam_downgrade_wayback_btn,
QPushButton#steam_downgrade_cancel_btn,
QPushButton#settings_cancel_btn {{
    background-color: {c.SURFACE};
    color: {c.TEXT};
    border: 1px solid {c.BORDER};
    border-radius: 8px;
    padding: 10px 16px;
    font-weight: 600;
    min-height: 20px;
}}

QPushButton#greenluma_install_download_btn:hover,
QPushButton#greenluma_install_zip_btn:hover,
QPushButton#settings_steam_downgrade_btn:hover,
QPushButton#steam_downgrade_wayback_btn:hover,
QPushButton#steam_downgrade_cancel_btn:hover,
QPushButton#settings_cancel_btn:hover {{
    border-color: {c.ACCENT};
    color: {c.ACCENT};
    background-color: {c.SURFACE_ELEVATED};
}}

QPushButton#settings_steam_restore_btn,
QPushButton#steam_downgrade_launch_btn {{
    background-color: {c.PRIMARY};
    color: {c.BG};
    border: 1px solid {c.PRIMARY};
    border-radius: 8px;
    padding: 10px 16px;
    font-weight: 600;
    min-height: 20px;
}}

QPushButton#settings_steam_restore_btn:hover,
QPushButton#steam_downgrade_launch_btn:hover {{
    background-color: {c.PRIMARY_HOVER};
    border-color: {c.PRIMARY_HOVER};
    color: {c.BG};
}}

QPushButton#greenluma_install_download_btn:disabled,
QPushButton#greenluma_install_zip_btn:disabled,
QPushButton#steam_downgrade_launch_btn:disabled {{
    color: {c.TEXT_DIM};
    border-color: {c.BORDER};
    background-color: {c.SURFACE};
}}

QLabel#overlay_subtitle {{
    color: {c.TEXT_MUTED};
    font-size: 9pt;
    margin-bottom: 2px;
}}

QFrame#downgrade_preview_box {{
    background-color: {c.INPUT_BG};
    border: 1px solid {c.BORDER};
    border-radius: 8px;
}}

QLabel#steam_downgrade_url_preview {{
    color: {c.ACCENT};
    font-family: "{FONT_MONO}";
    font-size: 8pt;
    background: transparent;
    border: none;
    padding: 0px;
}}

QLabel#steam_downgrade_url_preview[empty="true"] {{
    color: {c.TEXT_DIM};
    font-family: "{FONT_FAMILY}";
    font-size: 9pt;
    font-style: italic;
}}

QLineEdit#steam_downgrade_url_input {{
    min-height: 36px;
}}

QLabel#settings_steam_cfg_status {{
    color: {c.TEXT_DIM};
    font-size: 9pt;
    padding: 2px 0 4px 0;
}}

QLabel#greenluma_install_status,
QLabel#steam_downgrade_status {{
    color: {c.TEXT_MUTED};
    font-size: 9pt;
}}

QLabel#label_greenluma_install_title,
QLabel#label_steam_downgrade_title {{
    color: {c.TEXT};
    font-size: 12pt;
    font-weight: 700;
}}

QLabel#steam_downgrade_help {{
    color: {c.TEXT_MUTED};
    font-size: 9pt;
    line-height: 1.45;
}}

QPushButton#popup_btn1, QPushButton#create_profile_btn,
QPushButton#save_steam_path, QPushButton#save_greenluma_path,
QPushButton#settings_save_btn {{
    background-color: {c.ACCENT};
    color: {c.BG};
    border: none;
    font-weight: 600;
}}

QPushButton#popup_btn1:hover, QPushButton#create_profile_btn:hover,
QPushButton#save_steam_path:hover, QPushButton#save_greenluma_path:hover,
QPushButton#settings_save_btn:hover {{
    background-color: {c.ACCENT_HOVER};
}}

QPushButton#editor_toolbar_btn {{
    padding: 6px 14px;
    min-height: 16px;
    font-size: 9pt;
}}

QTableView#editor_table {{
    background-color: {c.INPUT_BG};
    alternate-background-color: {c.INPUT_BG};
    border: 1px solid {c.BORDER};
    border-radius: 10px;
    gridline-color: {c.BORDER};
    outline: none;
    padding: 0px;
    selection-background-color: {c.INPUT_BG};
    selection-color: {c.TEXT};
}}

QTableView#editor_table::item {{
    background-color: {c.INPUT_BG};
    color: {c.TEXT};
    padding: 4px 8px;
    border: none;
}}

QTableView#editor_table::item:selected,
QTableView#editor_table::item:hover,
QTableView#editor_table::item:focus {{
    background-color: {c.INPUT_BG};
    color: {c.TEXT};
    border: none;
    outline: none;
}}

QTableView#editor_table QLineEdit#editor_cell_input,
QTableView#editor_table QComboBox#editor_cell_combo {{
    background-color: {c.INPUT_BG};
    color: {c.TEXT};
    border: 1px solid {c.BORDER};
    border-radius: 4px;
    padding: 2px 6px;
    min-height: 0px;
    max-height: 28px;
    margin: 0px;
    font-family: "{FONT_MONO}";
    font-size: 9pt;
    selection-background-color: {c.ACCENT};
    selection-color: {c.BG};
}}

QTableView#editor_table QLineEdit#editor_cell_input:focus,
QTableView#editor_table QComboBox#editor_cell_combo:focus {{
    border: 1px solid {c.BORDER_FOCUS};
    background-color: {c.INPUT_BG};
}}

QTableView#editor_table QLineEdit#editor_cell_input::placeholder {{
    color: {c.TEXT_DIM};
}}

QTableView#editor_table QComboBox#editor_cell_combo::drop-down {{
    width: 22px;
    border: none;
}}

QTableView#editor_table QHeaderView::section {{
    background-color: {c.SURFACE_ELEVATED};
    color: {c.TEXT_MUTED};
    border: none;
    border-right: 1px solid {c.BORDER};
    border-bottom: 1px solid {c.BORDER};
    padding: 6px 8px;
    font-weight: 600;
    font-size: 9pt;
}}

QTableView#editor_table QToolButton#editor_header_add_btn {{
    background-color: {c.SURFACE};
    color: {c.ACCENT};
    border: 1px solid {c.BORDER};
    border-radius: 4px;
    font-weight: 700;
    font-size: 11pt;
    padding: 0px;
    margin: 0px;
}}

QTableView#editor_table QToolButton#editor_header_add_btn:hover {{
    background-color: {c.SURFACE_ELEVATED};
    border-color: {c.ACCENT};
    color: {c.ACCENT_HOVER};
}}

QTableView#editor_table QToolButton#editor_header_add_btn:pressed {{
    background-color: {c.ACCENT_PRESSED};
    color: {c.BG};
}}

QTableView, QListWidget {{
    background-color: {c.INPUT_BG};
    color: {c.TEXT};
    border: 1px solid {c.BORDER};
    border-radius: 10px;
    gridline-color: {c.BORDER};
    outline: none;
    alternate-background-color: {c.SURFACE};
}}

QListWidget#games_list {{
    background-color: {c.INPUT_BG};
    border: 1px solid {c.BORDER};
    border-radius: 10px;
    padding: 6px 4px 6px 8px;
}}

QListWidget#games_list::item {{
    padding: 7px 10px;
    margin: 1px 2px;
    border-radius: 6px;
}}

QListWidget#games_list::item:hover {{
    background-color: {c.SURFACE_ELEVATED};
}}

QListWidget#games_list::item:selected {{
    background-color: {c.ACCENT};
    color: {c.BG};
}}

QListWidget#games_list QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 6px 3px 6px 0;
    border: none;
}}

QListWidget#games_list QScrollBar::handle:vertical {{
    background: {c.BORDER};
    border-radius: 4px;
    min-height: 36px;
    margin: 0 1px;
}}

QListWidget#games_list QScrollBar::handle:vertical:hover {{
    background: {c.ACCENT};
}}

QListWidget#games_list QScrollBar::handle:vertical:pressed {{
    background: {c.ACCENT_PRESSED};
}}

QListWidget#games_list QScrollBar::add-line:vertical,
QListWidget#games_list QScrollBar::sub-line:vertical {{
    height: 0px;
    background: transparent;
    border: none;
}}

QListWidget#games_list QScrollBar::add-page:vertical,
QListWidget#games_list QScrollBar::sub-page:vertical {{
    background: transparent;
}}

QTableView::item, QListWidget::item {{
    padding: 6px 8px;
    border: none;
}}

QTableView::item:selected, QListWidget::item:selected {{
    background-color: {c.ACCENT};
    color: {c.BG};
}}

QTableView#editor_table::item:selected {{
    background-color: {c.INPUT_BG};
    color: {c.TEXT};
}}

QHeaderView::section {{
    background-color: {c.SURFACE_ELEVATED};
    color: {c.TEXT_MUTED};
    border: none;
    border-bottom: 1px solid {c.BORDER};
    padding: 8px;
    font-weight: 600;
    font-size: 9pt;
}}

QCheckBox {{
    color: {c.TEXT_MUTED};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid {c.BORDER};
    background: {c.INPUT_BG};
}}

QCheckBox::indicator:checked {{
    background-color: {c.ACCENT};
    border-color: {c.ACCENT};
}}

QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 4px 2px;
    border: none;
}}

QScrollBar::handle:vertical {{
    background: {c.BORDER};
    border-radius: 4px;
    min-height: 32px;
}}

QScrollBar::handle:vertical:hover {{
    background: {c.TEXT_DIM};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0px;
    background: transparent;
    border: none;
}}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{
    background: transparent;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 8px;
    margin: 2px 4px;
    border: none;
}}

QScrollBar::handle:horizontal {{
    background: {c.BORDER};
    border-radius: 4px;
    min-width: 32px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {c.TEXT_DIM};
}}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
    width: 0px;
    background: transparent;
    border: none;
}}

QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {{
    background: transparent;
}}

QFrame#searching_frame {{
    background-color: {c.SURFACE_ELEVATED};
    border: 1px solid {c.BORDER};
    border-radius: 12px;
}}
"""


def apply_theme(app: QApplication) -> None:
    font = QFont(FONT_FAMILY, 10)
    app.setFont(font)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(Colors.BG))
    palette.setColor(QPalette.WindowText, QColor(Colors.TEXT))
    palette.setColor(QPalette.Base, QColor(Colors.INPUT_BG))
    palette.setColor(QPalette.AlternateBase, QColor(Colors.SURFACE))
    palette.setColor(QPalette.Text, QColor(Colors.TEXT))
    palette.setColor(QPalette.Button, QColor(Colors.SURFACE_ELEVATED))
    palette.setColor(QPalette.ButtonText, QColor(Colors.TEXT))
    palette.setColor(QPalette.Highlight, QColor(Colors.ACCENT))
    palette.setColor(QPalette.HighlightedText, QColor(Colors.BG))
    app.setPalette(palette)
    app.setStyleSheet(app_stylesheet())
