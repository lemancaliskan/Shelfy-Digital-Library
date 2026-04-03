import os
import sys
import requests
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                               QPushButton, QScrollArea, QComboBox, QGridLayout,
                               QDialog, QFileDialog, QMessageBox, QFrame, QCheckBox,
                               QSizePolicy, QGraphicsDropShadowEffect, QApplication)
from PySide6.QtGui import QPixmap, QIcon, QColor, QFont, QCursor, QPalette, QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt, QSize, Signal, QVariantAnimation, QEasingCurve
from assets_manager import (Assets, PRIMARY_COLOR, BG_COLOR_DARK, ACCENT_COLOR, HOVER_COLOR, BORDER_COLOR,
                            SIDEBAR_WIDTH, CARD_WIDTH, CARD_HEIGHT, COVER_WIDTH, COVER_HEIGHT,
                            DIALOG_WIDTH, DIALOG_HEIGHT, CAT_COLORS)
from translations import get_text


def apply_shadow(widget, radius=15, alpha=40):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(radius)
    shadow.setColor(QColor(97, 61, 193, alpha))
    shadow.setOffset(0, 4)
    widget.setGraphicsEffect(shadow)


def apply_combo_style(combo, dropdown_bg, fg_color):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    arrow_path = os.path.join(base_dir, "assets", "icon", "arrow.png").replace("\\", "/")

    sb_bg = "rgba(0,0,0,0.03)" if dropdown_bg != BG_COLOR_DARK else "rgba(255,255,255,0.03)"
    sb_handle = "rgba(97, 61, 193, 0.5)"
    sb_handle_hover = "rgba(97, 61, 193, 0.8)"

    combo.setStyleSheet(f"""
        QComboBox {{
            border: 2px solid rgba(151, 223, 252, 0.3);
            border-radius: 12px;
            padding: 5px 10px;
            background: transparent;
        }}
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 30px;
            border-left: none;
        }}
        QComboBox::down-arrow {{
            image: url("{arrow_path}");
            width: 14px;
            height: 14px;
            margin-right: 10px;
        }}
        QComboBox QAbstractItemView {{
            border: 1px solid rgba(151, 223, 252, 0.3);
            border-radius: 8px;
            background-color: {dropdown_bg};
            color: {fg_color};
            selection-background-color: rgba(97, 61, 193, 0.2);
            outline: 0px;
            margin: 0px;
            padding: 0px;
        }}
        QComboBox QAbstractItemView::item {{
            min-height: 35px;
            padding: 5px;
        }}
        QComboBox QAbstractItemView QScrollBar:vertical {{
            border: none;
            background: {sb_bg};
            width: 8px;
            border-radius: 4px;
            margin: 0px;
        }}
        QComboBox QAbstractItemView QScrollBar::handle:vertical {{
            background: {sb_handle};
            min-height: 30px;
            border-radius: 4px;
        }}
        QComboBox QAbstractItemView QScrollBar::handle:vertical:hover {{
            background: {sb_handle_hover};
        }}
        QComboBox QAbstractItemView QScrollBar::add-line:vertical,
        QComboBox QAbstractItemView QScrollBar::sub-line:vertical {{
            height: 0px;
            border: none;
            background: none;
        }}
        QComboBox QAbstractItemView QScrollBar::add-page:vertical,
        QComboBox QAbstractItemView QScrollBar::sub-page:vertical {{
            background: none;
        }}
    """)
    combo.setMaxVisibleItems(5)
    try:
        view = combo.view()
        if view:
            view.window().setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
            view.window().setAttribute(Qt.WA_TranslucentBackground)
    except Exception:
        pass


class IconButton(QPushButton):
    def __init__(self, icon, base_size=24, hover_scale=1.2, parent=None):
        super().__init__(parent)
        if isinstance(icon, QIcon):
            self.setIcon(icon)
        self.base_size = base_size
        self.hover_size = int(base_size * hover_scale)

        self.setIconSize(QSize(self.base_size, self.base_size))
        self.setStyleSheet("QPushButton { background: transparent; border: none; }")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(self.hover_size + 4, self.hover_size + 4)

    def enterEvent(self, event):
        self.setIconSize(QSize(self.hover_size, self.hover_size))
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setIconSize(QSize(self.base_size, self.base_size))
        super().leaveEvent(event)


class StyledButton(QPushButton):
    def __init__(self, text, icon=None, is_primary=False, parent=None):
        super().__init__(text, parent)
        if icon:
            self.setIcon(icon)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(40)

        if is_primary:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {PRIMARY_COLOR}, stop:1 {ACCENT_COLOR});
                    color: white;
                    border-radius: 12px;
                    font-weight: bold;
                    padding: 5px 15px;
                }}
                QPushButton:hover {{
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {ACCENT_COLOR}, stop:1 {HOVER_COLOR});
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {PRIMARY_COLOR};
                    border: 2px solid {BORDER_COLOR};
                    border-radius: 12px;
                    font-weight: bold;
                    padding: 5px 15px;
                }}
                QPushButton:hover {{
                    border-color: {PRIMARY_COLOR};
                    background-color: rgba(151, 223, 252, 0.1);
                }}
            """)


class StyledInput(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setFixedHeight(40)
        self.setStyleSheet(f"""
            QLineEdit {{
                border: 2px solid rgba(151, 223, 252, 0.3);
                border-radius: 12px;
                padding: 0 10px;
                background-color: transparent;
            }}
            QLineEdit:focus {{
                border-color: {PRIMARY_COLOR};
            }}
        """)


class CheckableComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.lineEdit().setPlaceholderText("Listelerde ara...")
        self.model = QStandardItemModel(self)
        self.setModel(self.model)
        self.view().pressed.connect(self.handle_item_pressed)
        self.lineEdit().textChanged.connect(self.filter_items)
        self._items = []

    def add_item(self, text, checked=False):
        item = QStandardItem(text)
        item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        item.setData(Qt.Checked if checked else Qt.Unchecked, Qt.CheckStateRole)
        self.model.appendRow(item)
        self._items.append(item)

    def handle_item_pressed(self, index):
        item = self.model.itemFromIndex(index)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)

    def filter_items(self, text):
        for i in range(self.model.rowCount()):
            item = self.model.item(i)
            if text.lower() in item.text().lower():
                self.view().setRowHidden(i, False)
            else:
                self.view().setRowHidden(i, True)

    def get_checked_items(self):
        return [self.model.item(i).text() for i in range(self.model.rowCount()) if
                self.model.item(i).checkState() == Qt.Checked]


class AddListDialog(QDialog):
    def __init__(self, parent, on_save_callback):
        super().__init__(parent)
        self.on_save_callback = on_save_callback
        self.setWindowTitle(get_text("new_list_title"))
        self.setFixedSize(380, 200)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {parent.styleSheet().split('background-color:')[1].split(';')[0].strip()} }}
            QLabel {{ font-size: 14px; font-weight: bold; color: {PRIMARY_COLOR}; }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        lbl = QLabel(get_text("list_name"))
        layout.addWidget(lbl)

        self.list_name_entry = StyledInput(get_text("ex_favorites"))
        layout.addWidget(self.list_name_entry)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        cancel_btn = StyledButton(get_text("cancel"))
        cancel_btn.clicked.connect(self.reject)
        create_btn = StyledButton(get_text("create"), is_primary=True)
        create_btn.clicked.connect(self._save_list)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(create_btn)
        layout.addLayout(btn_layout)

    def _save_list(self):
        list_name = self.list_name_entry.text().strip()
        if not list_name:
            QMessageBox.critical(self, get_text("error"), get_text("empty_list_name"))
            return
        self.on_save_callback(list_name)
        self.accept()


class TotalBooksCard(QFrame):
    def __init__(self, theme, parent=None):
        super().__init__(parent)

        self.theme = theme
        self.setFixedHeight(80)
        self.setCursor(Qt.PointingHandCursor)
        self.lay = QHBoxLayout(self)
        self.lay.setContentsMargins(20, 10, 20, 10)
        self.lay.setSpacing(15)

        self.icon_lbl = QLabel()
        self.icon_lbl.setPixmap(Assets.get_icon("book").pixmap(32, 32))
        self.icon_lbl.setStyleSheet("background: transparent; border: none;")
        self.lay.addWidget(self.icon_lbl)

        self.text_lay = QVBoxLayout()
        self.text_lay.setSpacing(2)

        self.title_lbl = QLabel(get_text("total_books") if "total_books" in globals() else "Toplam Kitap")
        self.title_lbl.setFont(QFont("Segoe UI", 10))
        self.title_lbl.setStyleSheet("color: rgba(255, 255, 255, 0.9); background: transparent; border: none;")

        self.count_lbl = QLabel("0")
        self.count_lbl.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.count_lbl.setStyleSheet("color: white; background: transparent; border: none;")

        self.text_lay.addWidget(self.title_lbl)
        self.text_lay.addWidget(self.count_lbl)

        self.lay.addLayout(self.text_lay)
        self.lay.addStretch()
        self._apply_base_style()

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(4)
        self.shadow.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(self.shadow)

        self.anim = QVariantAnimation(self)
        self.anim.setDuration(200)
        self.anim.setStartValue(15)
        self.anim.setEndValue(30)
        self.anim.valueChanged.connect(self._update_shadow)

    def _apply_base_style(self, hover=False):
        bg = PRIMARY_COLOR if not hover else HOVER_COLOR
        self.setStyleSheet(f"TotalBooksCard {{ background-color: {bg}; border-radius: 12px; border: none; }}")

    def enterEvent(self, event):
        self._apply_base_style(hover=True)
        self.anim.setDirection(QVariantAnimation.Forward)
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._apply_base_style(hover=False)
        self.anim.setDirection(QVariantAnimation.Backward)
        self.anim.start()
        super().leaveEvent(event)

    def _update_shadow(self, blur_radius):
        self.shadow.setBlurRadius(blur_radius)
        alpha = int(40 + (blur_radius - 15) * 3)
        self.shadow.setColor(QColor(0, 0, 0, alpha))

    def set_count(self, count):
        self.count_lbl.setText(str(count))


class Sidebar(QScrollArea):
    def __init__(self, parent, theme, categories, subcategories, languages, custom_lists, on_list_select,
                 on_select_category,
                 on_select_subcategory, on_select_language, on_search_change, on_filter_change, on_add_list,
                 on_delete_list,
                 ):
        super().__init__(parent)
        self.theme = theme
        self.setFixedWidth(SIDEBAR_WIDTH)
        self.setWidgetResizable(True)
        self.setStyleSheet("QScrollArea { border: none; border-right: 1px solid rgba(151, 223, 252, 0.3); }")

        self.content_widget = QWidget()
        self.layout = QVBoxLayout(self.content_widget)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        self.categories = categories
        self.subcategories = subcategories
        self.languages = languages
        self.custom_lists = custom_lists if custom_lists else []

        self.on_select_category = on_select_category
        self.on_select_subcategory = on_select_subcategory
        self.on_select_language = on_select_language
        self.on_search_change = on_search_change
        self.on_filter_change = on_filter_change
        self.on_list_select = on_list_select
        self.on_add_list = on_add_list
        self.on_delete_list = on_delete_list

        self._build_search()
        self._build_categories()
        self._build_lists()
        self._build_filters()

        self.layout.addStretch()

        self.total_card = TotalBooksCard(theme)
        self.layout.addWidget(self.total_card)

        self.setWidget(self.content_widget)

    def _build_search(self):
        lbl = QLabel(get_text("search").upper())
        lbl.setFont(QFont("Arial", 9, QFont.Bold))
        lbl.setStyleSheet(f"color: {PRIMARY_COLOR};")
        self.layout.addWidget(lbl)

        self.search_entry = StyledInput(get_text("search_placeholder"))
        self.search_entry.textChanged.connect(self.on_search_change)
        self.layout.addWidget(self.search_entry)

    def _build_categories(self):
        lbl = QLabel(get_text("categories").upper())
        lbl.setFont(QFont("Arial", 9, QFont.Bold))
        lbl.setStyleSheet(f"color: {PRIMARY_COLOR};")
        self.layout.addWidget(lbl)

        self.cat_combo = QComboBox()
        self._style_combo(self.cat_combo)
        self.cat_combo.addItems([get_text("all")] + [c for c in self.categories if c != get_text("all")])
        self.cat_combo.currentTextChanged.connect(self._on_cat_changed)
        self.layout.addWidget(self.cat_combo)

        self.subcat_lbl = QLabel(get_text("subcategories").upper())
        self.subcat_lbl.setFont(QFont("Arial", 9, QFont.Bold))
        self.subcat_lbl.setStyleSheet(f"color: {PRIMARY_COLOR};")
        self.layout.addWidget(self.subcat_lbl)

        self.subcat_combo = QComboBox()
        self._style_combo(self.subcat_combo)
        self.subcat_combo.addItems([get_text("all")] + [c for c in self.subcategories if c != get_text("all")])
        self.subcat_combo.currentTextChanged.connect(self.on_select_subcategory)
        self.layout.addWidget(self.subcat_combo)

        self.lang_lbl = QLabel(get_text("language_label"))
        self.lang_lbl.setFont(QFont("Arial", 9, QFont.Bold))
        self.lang_lbl.setStyleSheet(f"color: {PRIMARY_COLOR};")
        self.layout.addWidget(self.lang_lbl)

        self.lang_combo = QComboBox()
        self._style_combo(self.lang_combo)
        self.lang_combo.addItems([get_text("all")] + [l for l in self.languages if l != get_text("all")])
        self.lang_combo.currentTextChanged.connect(self.on_select_language)
        self.layout.addWidget(self.lang_combo)

        self._toggle_subcats()

    def _on_cat_changed(self, text):
        self.on_select_category(text)
        self._toggle_subcats()

    def _toggle_subcats(self):
        if self.cat_combo.currentText() == get_text("all") or not self.cat_combo.currentText():
            self.subcat_lbl.hide()
            self.subcat_combo.hide()
        else:
            self.subcat_lbl.show()
            self.subcat_combo.show()

    def _build_lists(self):
        header_layout = QHBoxLayout()
        lbl = QLabel(get_text("my_lists").upper())
        lbl.setFont(QFont("Arial", 9, QFont.Bold))
        lbl.setStyleSheet(f"color: {PRIMARY_COLOR};")
        header_layout.addWidget(lbl)

        self.del_list_btn = IconButton(Assets.get_icon("list_del"), base_size=18, hover_scale=1.2)
        self.del_list_btn.clicked.connect(self._delete_selected_list)
        self.del_list_btn.hide()
        header_layout.addWidget(self.del_list_btn)

        add_list_btn = IconButton(Assets.get_icon("list_add"), base_size=18, hover_scale=1.2)
        add_list_btn.clicked.connect(self._open_add_list_dialog)
        header_layout.addWidget(add_list_btn)

        self.layout.addLayout(header_layout)

        self.list_combo = QComboBox()
        self._style_combo(self.list_combo)
        self.update_lists(self.custom_lists)
        self.list_combo.currentTextChanged.connect(self._on_list_changed)
        self.layout.addWidget(self.list_combo)

    def update_languages(self, langs):
        self.languages = langs
        curr = self.lang_combo.currentText()
        self.lang_combo.blockSignals(True)
        self.lang_combo.clear()
        self.lang_combo.addItems([get_text("all")] + [l for l in langs if l != get_text("all")])
        if curr in [self.lang_combo.itemText(i) for i in range(self.lang_combo.count())]:
            self.lang_combo.setCurrentText(curr)
        self.lang_combo.blockSignals(False)

    def _on_list_changed(self, choice):
        if choice in [get_text("all_books"), get_text("favorites")]:
            self.del_list_btn.hide()
        else:
            self.del_list_btn.show()
        self.on_list_select(choice)

    def _delete_selected_list(self):
        selected = self.list_combo.currentText()
        if selected in [get_text("all_books"), get_text("favorites")]:
            return
        reply = QMessageBox.question(self, get_text("list_delete"), get_text("list_delete_confirm", selected=selected))
        if reply == QMessageBox.Yes:
            self.on_delete_list(selected)
            self.list_combo.setCurrentText(get_text("all_books"))

    def _open_add_list_dialog(self):
        dlg = AddListDialog(self.window(), self.on_add_list)
        dlg.exec()

    def _build_filters(self):
        lbl = QLabel(get_text("reading_status").upper())
        lbl.setFont(QFont("Arial", 9, QFont.Bold))
        lbl.setStyleSheet(f"color: {PRIMARY_COLOR};")
        self.layout.addWidget(lbl)

        self.read_btn_group = []
        read_layout = QGridLayout()
        opts = [("all", get_text("all")), ("read", get_text("read")),
                ("in_progress", get_text("in_progress")), ("unread", get_text("unread"))]

        for i, (val, txt) in enumerate(opts):
            btn = QPushButton(txt)
            btn.setCheckable(True)
            btn.setFixedHeight(30)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{ border: 2px solid rgba(151,223,252,0.3); border-radius: 8px; background: transparent; }}
                QPushButton:checked {{ background-color: {PRIMARY_COLOR}; color: white; border: none; }}
                QPushButton:hover:!checked {{ background-color: rgba(151, 223, 252, 0.1); }}
            """)
            if val == "all": btn.setChecked(True)
            btn.clicked.connect(lambda checked, v=val, b=btn: self._handle_read_filter(v, b))
            self.read_btn_group.append(btn)
            read_layout.addWidget(btn, i // 2, i % 2)
        self.layout.addLayout(read_layout)

        lbl2 = QLabel(get_text("stock_status").upper())
        lbl2.setFont(QFont("Arial", 9, QFont.Bold))
        lbl2.setStyleSheet(f"color: {PRIMARY_COLOR};")
        self.layout.addWidget(lbl2)

        self.stock_btn_group = []
        stock_layout = QGridLayout()
        opts2 = [("all", get_text("all")), ("available", get_text("available")), ("borrowed", get_text("borrowed"))]

        for i, (val, txt) in enumerate(opts2):
            btn = QPushButton(txt)
            btn.setCheckable(True)
            btn.setFixedHeight(30)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{ border: 2px solid rgba(151,223,252,0.3); border-radius: 8px; background: transparent; }}
                QPushButton:checked {{ background-color: {PRIMARY_COLOR}; color: white; border: none; }}
                QPushButton:hover:!checked {{ background-color: rgba(151, 223, 252, 0.1); }}
            """)
            if val == "all": btn.setChecked(True)
            btn.clicked.connect(lambda checked, v=val, b=btn: self._handle_stock_filter(v, b))
            self.stock_btn_group.append(btn)
            stock_layout.addWidget(btn, i // 2, i % 2)
        self.layout.addLayout(stock_layout)

    def _handle_read_filter(self, val, clicked_btn):
        for btn in self.read_btn_group:
            if btn != clicked_btn: btn.setChecked(False)
        clicked_btn.setChecked(True)
        self.on_filter_change(reading=val)

    def _handle_stock_filter(self, val, clicked_btn):
        for btn in self.stock_btn_group:
            if btn != clicked_btn: btn.setChecked(False)
        clicked_btn.setChecked(True)
        self.on_filter_change(stock=val)

    def _style_combo(self, combo):
        combo.setFixedHeight(40)
        dropdown_bg = BG_COLOR_DARK if getattr(self, "theme", "Light") == "Dark" else "white"
        fg_color = "white" if dropdown_bg == BG_COLOR_DARK else "black"
        apply_combo_style(combo, dropdown_bg, fg_color)

    def update_categories(self, cats):
        self.categories = cats
        curr = self.cat_combo.currentText()
        self.cat_combo.blockSignals(True)
        self.cat_combo.clear()
        self.cat_combo.addItems([get_text("all")] + [c for c in cats if c != get_text("all")])
        if curr in [self.cat_combo.itemText(i) for i in range(self.cat_combo.count())]:
            self.cat_combo.setCurrentText(curr)
        self.cat_combo.blockSignals(False)

    def update_subcategories(self, subcats):
        self.subcategories = subcats
        curr = self.subcat_combo.currentText()
        self.subcat_combo.blockSignals(True)
        self.subcat_combo.clear()
        self.subcat_combo.addItems([get_text("all")] + [c for c in subcats if c != get_text("all")])
        if curr in [self.subcat_combo.itemText(i) for i in range(self.subcat_combo.count())]:
            self.subcat_combo.setCurrentText(curr)
        self.subcat_combo.blockSignals(False)
        self._toggle_subcats()

    def update_lists(self, lists):
        self.custom_lists = lists
        curr = self.list_combo.currentText()
        self.list_combo.blockSignals(True)
        self.list_combo.clear()
        self.list_combo.addItems([get_text("all_books"), get_text("favorites")] + lists)
        if curr in [self.list_combo.itemText(i) for i in range(self.list_combo.count())]:
            self.list_combo.setCurrentText(curr)
        self.list_combo.blockSignals(False)

    def update_stats(self, total):
        self.total_card.set_count(total)


class AddBookDialog(QDialog):
    def __init__(self, parent, cat_dict, lang_list, on_save_callback):
        super().__init__(parent)
        self.cat_dict = cat_dict
        self.lang_list = lang_list
        self.on_save_callback = on_save_callback
        self.setWindowTitle(get_text("add_new_book"))
        self.setFixedSize(DIALOG_WIDTH, DIALOG_HEIGHT)
        self.setStyleSheet(
            f"QDialog {{ background-color: {parent.styleSheet().split('background-color:')[1].split(';')[0].strip()} }}")

        main_layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        self.content = QWidget()
        self.layout = QVBoxLayout(self.content)

        self.title_entry = self._add_field(get_text("book_name_req"), get_text("ex_1984"))
        self.author_entry = self._add_field(get_text("author_req"), get_text("ex_orwell"))
        self.publisher_entry = self._add_field(get_text("publisher_req"), get_text("ex_can"))
        self.isbn_entry = self._add_field(get_text("isbn_req"), get_text("ex_isbn"))

        lbl = QLabel(get_text("category_req"))
        lbl.setFont(QFont("Arial", 10, QFont.Bold))
        self.layout.addWidget(lbl)
        self.cat_combo = QComboBox()
        self.cat_combo.setEditable(True)
        self.cat_combo.lineEdit().setStyleSheet("background: transparent; border: none;")
        self.layout.addWidget(self.cat_combo)

        lbl2 = QLabel(get_text("subcategory_opt"))
        lbl2.setFont(QFont("Arial", 10, QFont.Bold))
        self.layout.addWidget(lbl2)
        self.subcat_combo = QComboBox()
        self.subcat_combo.setEditable(True)
        self.subcat_combo.lineEdit().setStyleSheet("background: transparent; border: none;")
        self.layout.addWidget(self.subcat_combo)

        self.cat_combo.addItems([c for c in self.cat_dict.keys() if c != get_text("all")])
        self.cat_combo.currentTextChanged.connect(self._on_cat_change)

        self._style_combo(self.cat_combo)
        self._style_combo(self.subcat_combo)

        lbl_lang = QLabel(get_text("language_req"))
        lbl_lang.setFont(QFont("Arial", 10, QFont.Bold))
        self.layout.addWidget(lbl_lang)

        self.lang_combo = QComboBox()
        self.lang_combo.setEditable(True)
        self.lang_combo.lineEdit().setStyleSheet("background: transparent; border: none;")
        self.lang_combo.addItems([l for l in self.lang_list if l != get_text("all")])
        self._style_combo(self.lang_combo)
        self.layout.addWidget(self.lang_combo)

        if self.cat_combo.count() > 0:
            self._on_cat_change(self.cat_combo.currentText())

        self.year_entry = self._add_field(get_text("pub_year"), get_text("ex_year"))

        self.read_status = self._add_radio_group(get_text("reading_status_req"),
                                                 [(get_text("unread"), "unread"),
                                                  (get_text("in_progress"), "in_progress"), (get_text("read"), "read")])
        self.stock_status = self._add_radio_group(get_text("stock_status_req"),
                                                  [(get_text("available"), "available"),
                                                   (get_text("borrowed"), "borrowed")])

        self._add_cover_section()

        scroll.setWidget(self.content)
        main_layout.addWidget(scroll)

        btn_lay = QHBoxLayout()
        cancel = StyledButton(get_text("cancel"))
        cancel.clicked.connect(self.reject)
        self.save_btn = StyledButton(get_text("add"), is_primary=True)
        self.save_btn.clicked.connect(self._save)
        btn_lay.addWidget(cancel)
        btn_lay.addWidget(self.save_btn)
        main_layout.addLayout(btn_lay)

    def _add_field(self, label, placeholder):
        lbl = QLabel(label)
        lbl.setFont(QFont("Arial", 10, QFont.Bold))
        self.layout.addWidget(lbl)
        entry = StyledInput(placeholder)
        self.layout.addWidget(entry)
        return entry

    def _style_combo(self, combo):
        combo.setFixedHeight(40)
        dropdown_bg = "white"
        fg_color = "black"
        try:
            if hasattr(self.parent(), "current_theme"):
                if self.parent().current_theme == "Dark":
                    dropdown_bg = BG_COLOR_DARK
                    fg_color = "white"
        except:
            pass
        apply_combo_style(combo, dropdown_bg, fg_color)

    def _add_radio_group(self, label, options):
        lbl = QLabel(label)
        lbl.setFont(QFont("Arial", 10, QFont.Bold))
        self.layout.addWidget(lbl)
        frame = QFrame()
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(0, 0, 0, 0)

        btn_group = []
        for text, val in options:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setFixedHeight(35)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setProperty("val", val)
            btn.setStyleSheet(f"""
                QPushButton {{ border: 2px solid rgba(151,223,252,0.3); border-radius: 8px; background: transparent; }}
                QPushButton:checked {{ background-color: {PRIMARY_COLOR}; color: white; border: none; }}
                QPushButton:hover:!checked {{ background-color: rgba(151, 223, 252, 0.1); }}
            """)
            btn.clicked.connect(lambda checked, b=btn, grp=btn_group: self._on_radio_click(b, grp))
            btn_group.append(btn)
            lay.addWidget(btn)

        if btn_group: btn_group[0].setChecked(True)
        self.layout.addWidget(frame)
        return btn_group

    def _add_cover_section(self):
        lbl3 = QLabel(get_text("cover_image"))
        lbl3.setFont(QFont("Arial", 10, QFont.Bold))
        self.layout.addWidget(lbl3)

        cover_lay = QHBoxLayout()

        self.preview_lbl = QLabel()
        self.preview_lbl.setFixedSize(60, 85)
        self.preview_lbl.setStyleSheet("border: 1px dashed rgba(151, 223, 252, 0.5); border-radius: 8px; color: gray;")
        self.preview_lbl.setAlignment(Qt.AlignCenter)
        self.preview_lbl.setText("Görsel\nYok")
        cover_lay.addWidget(self.preview_lbl)

        input_lay = QVBoxLayout()
        self.cover_entry = StyledInput(get_text("cover_placeholder"))
        self.cover_entry.textChanged.connect(self._update_preview)
        input_lay.addWidget(self.cover_entry)

        browse_btn = StyledButton(get_text("browse"), is_primary=True)
        browse_btn.clicked.connect(self._browse)
        input_lay.addWidget(browse_btn)

        cover_lay.addLayout(input_lay)
        self.layout.addLayout(cover_lay)

    def _update_preview(self):
        path = self.cover_entry.text().strip()
        pixmap = QPixmap()

        if path.startswith(("http://", "https://")):
            try:
                resp = requests.get(path, timeout=3)
                if resp.status_code == 200:
                    pixmap.loadFromData(resp.content)
            except:
                pass
        elif os.path.exists(path):
            pixmap.load(path)

        if not pixmap.isNull():
            self.preview_lbl.setPixmap(pixmap.scaled(60, 85, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
            self.preview_lbl.setStyleSheet("border: none; border-radius: 8px;")
        else:
            self.preview_lbl.clear()
            self.preview_lbl.setText("Görsel\nYok")
            self.preview_lbl.setStyleSheet(
                "border: 1px dashed rgba(151, 223, 252, 0.5); border-radius: 8px; color: gray; font-size: 10px;")

    def _on_radio_click(self, clicked_btn, group):
        for btn in group:
            if btn != clicked_btn: btn.setChecked(False)
        clicked_btn.setChecked(True)

    def _on_cat_change(self, text):
        subcats = self.cat_dict.get(text, [])
        self.subcat_combo.clear()
        self.subcat_combo.addItems([s for s in subcats if s != get_text("all") and s])

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(self, get_text("select_cover"), "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.cover_entry.setText(path)

    def _save(self):
        try:
            year_val = int(self.year_entry.text()) if self.year_entry.text() else None
        except ValueError:
            QMessageBox.critical(self, get_text("error"), get_text("year_error"))
            return

        read_val = next((b.property("val") for b in self.read_status if b.isChecked()), "unread")
        stock_val = next((b.property("val") for b in self.stock_status if b.isChecked()), "available")

        data = {
            'title': self.title_entry.text().strip(),
            'author': self.author_entry.text().strip(),
            'isbn': self.isbn_entry.text().strip(),
            'publisher': self.publisher_entry.text().strip(),
            'category': self.cat_combo.currentText().strip(),
            'subcategory': self.subcat_combo.currentText().strip(),
            'language': self.lang_combo.currentText().strip(),
            'year': year_val,
            'readingStatus': read_val,
            'stockStatus': stock_val,
            'cover': self.cover_entry.text().strip()
        }

        if not all(
                [data['title'], data['author'], data['isbn'], data['publisher'], data['category'], data['language']]):
            QMessageBox.critical(self, get_text("error"), get_text("req_fields_error"))
            return

        self.on_save_callback(data)
        self.accept()


class EditBookDialog(AddBookDialog):
    def __init__(self, parent, cat_dict, lang_list, on_save, book_data):
        self.book_data = book_data
        super().__init__(parent, cat_dict, lang_list, on_save)
        self.setWindowTitle(get_text("edit_book"))
        self.save_btn.setText(get_text("update"))
        self._fill_data()

    def _fill_data(self):
        self.title_entry.setText(self.book_data.get('title', ''))
        self.author_entry.setText(self.book_data.get('author', ''))
        self.isbn_entry.setText(self.book_data.get('isbn', ''))
        self.publisher_entry.setText(self.book_data.get('publisher', ''))
        self.cat_combo.setCurrentText(self.book_data.get('category', ''))
        self.subcat_combo.setCurrentText(self.book_data.get('subcategory', ''))
        self.lang_combo.setCurrentText(self.book_data.get('language', ''))
        if self.book_data.get('year'): self.year_entry.setText(str(self.book_data.get('year')))

        cover = self.book_data.get('cover', '')
        if cover and cover != 'default':
            self.cover_entry.setText(cover)
            self._update_preview()

        r_stat = self.book_data.get('reading_status', 'unread')
        for b in self.read_status:
            b.setChecked(b.property("val") == r_stat)

        s_stat = 'available' if self.book_data.get('owned', True) else 'borrowed'
        for b in self.stock_status:
            b.setChecked(b.property("val") == s_stat)

    def _save(self):
        year_val = None
        if self.year_entry.text():
            try:
                year_val = int(self.year_entry.text())
            except ValueError:
                QMessageBox.critical(self, get_text("error"), get_text("year_error"))
                return

        read_val = next((b.property("val") for b in self.read_status if b.isChecked()), "unread")
        stock_val = next((b.property("val") for b in self.stock_status if b.isChecked()), "available")

        data = {
            "id": self.book_data.get('id'),
            "title": self.title_entry.text().strip(),
            "author": self.author_entry.text().strip(),
            "isbn": self.isbn_entry.text().strip(),
            "year": year_val,
            "publisher": self.publisher_entry.text().strip(),
            "category": self.cat_combo.currentText().strip(),
            "subcategory": self.subcat_combo.currentText().strip(),
            "language": self.lang_combo.currentText().strip(),
            "reading_status": read_val,
            "owned": (stock_val == "available"),
            "cover": self.cover_entry.text().strip()
        }

        if not all(
                [data['title'], data['author'], data['isbn'], data['publisher'], data['category'], data['language']]):
            QMessageBox.critical(self, get_text("error"), get_text("req_fields_error_2"))
            return

        self.on_save_callback(data)
        self.accept()


class AddToListDialog(QDialog):
    def __init__(self, parent, book_data, available_lists, on_save):
        super().__init__(parent)
        self.on_save = on_save
        self.setWindowTitle(get_text("manage_lists") if "get_text" in globals() else "Listeleri Yönet")

        self.setFixedSize(300, 200)

        bg_color = "white"
        if parent and hasattr(parent, "styleSheet"):
            try:
                bg_color = parent.styleSheet().split('background-color:')[1].split(';')[0].strip()
            except:
                pass

        self.setStyleSheet(f"""
            QDialog {{ background-color: {bg_color}; }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        lbl = QLabel(f"'{book_data.get('title')}'")
        lbl.setFont(QFont("Arial", 12, QFont.Bold))
        lbl.setStyleSheet(f"color: {PRIMARY_COLOR};")
        lbl.setWordWrap(True)
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)

        self.combo = CheckableComboBox(self)
        self.combo.setFixedHeight(40)

        dropdown_bg = BG_COLOR_DARK if bg_color == BG_COLOR_DARK else "white"
        fg_color = "white" if dropdown_bg == BG_COLOR_DARK else "black"

        apply_combo_style(self.combo, dropdown_bg, fg_color)
        self.combo.lineEdit().setStyleSheet("background: transparent; border: none;")

        curr = book_data.get("lists", [])
        for lst in available_lists:
            self.combo.add_item(lst, checked=(lst in curr))

        layout.addWidget(self.combo)
        layout.addStretch()

        btn_lay = QHBoxLayout()
        cancel = StyledButton(get_text("cancel") if "get_text" in globals() else "İptal")
        cancel.clicked.connect(self.reject)
        save = StyledButton(get_text("save") if "get_text" in globals() else "Kaydet", is_primary=True)
        save.clicked.connect(self._do_save)
        btn_lay.addWidget(cancel)
        btn_lay.addWidget(save)
        layout.addLayout(btn_lay)

    def _do_save(self):
        selected = self.combo.get_checked_items()
        self.on_save(selected)
        self.accept()


class BookCard(QFrame):
    def __init__(self, book_data, theme, on_edit, on_delete, on_add_to_list, on_author_click, on_category_click):
        super().__init__()
        self.book_data = book_data
        self.theme = theme
        self.setFixedSize(CARD_WIDTH, CARD_HEIGHT)
        self._hover_offset = 0
        self.original_pos = None
        self.setCursor(Qt.PointingHandCursor)

        self.styles = {
            "Light": {
                "default": f"""
                    QFrame {{
                        background-color: rgba(255, 255, 255, 0.8);
                        border: 1px solid rgba(151, 223, 252, 0.4);
                        border-radius: 16px;
                    }}
                """,
                "hover": f"""
                    QFrame {{
                        background-color: white;
                        border: 2px solid {BORDER_COLOR};
                        border-radius: 16px;
                    }}
                """,
                "title": f"color: {PRIMARY_COLOR}; border: none; background: transparent;",
                "author": f"color: {HOVER_COLOR}; border: none; background: transparent;"
            },
            "Dark": {
                "default": f"""
                    QFrame {{
                        background-color: {BG_COLOR_DARK};
                        border: 1px solid rgba(151, 223, 252, 0.2);
                        border-radius: 16px;
                    }}
                """,
                "hover": f"""
                    QFrame {{
                        background-color: {BG_COLOR_DARK};
                        border: 2px solid {PRIMARY_COLOR};
                        border-radius: 16px;
                    }}
                """,
                "title": f"color: #FFFFFF; border: none; background: transparent;",
                "author": f"color: #AAAAAA; border: none; background: transparent;"
            }
        }

        self.default_style = self.styles[self.theme]["default"]
        self.hover_style = self.styles[self.theme]["hover"]
        self.setStyleSheet(self.default_style)

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(4)
        self.shadow.setColor(QColor(0, 0, 0, 40 if self.theme == "Light" else 80))
        self.setGraphicsEffect(self.shadow)

        self.anim = QVariantAnimation(self)
        self.anim.setDuration(150)
        self.anim.setStartValue(0)
        self.anim.setEndValue(6)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.valueChanged.connect(self._update_hover_effect)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(0)

        self.cover_lbl = QLabel()
        self.cover_lbl.setFixedSize(COVER_WIDTH, COVER_HEIGHT)
        self.cover_lbl.setAlignment(Qt.AlignCenter)
        self.cover_lbl.setStyleSheet("border-radius: 10px; background-color: #f8f9fa; border: none;")
        self._load_cover()
        layout.addWidget(self.cover_lbl, alignment=Qt.AlignCenter)
        layout.addSpacing(10)

        title = book_data.get('title', get_text("no_title"))
        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title_lbl.setStyleSheet(self.styles[self.theme]["title"])
        title_lbl.setAlignment(Qt.AlignCenter)
        title_lbl.setWordWrap(True)
        title_lbl.setFixedHeight(34)
        layout.addWidget(title_lbl)
        layout.addSpacing(2)

        author = book_data.get('author', get_text("unknown"))

        class ClickableLabel(QLabel):
            clicked = Signal(str)

            def mousePressEvent(self, ev): self.clicked.emit(self.text())

        author_clickable = ClickableLabel(author)
        author_clickable.setFont(QFont("Segoe UI", 10))
        author_clickable.setStyleSheet(self.styles[self.theme]["author"])
        author_clickable.setAlignment(Qt.AlignCenter)
        author_clickable.setCursor(Qt.PointingHandCursor)
        author_clickable.setFixedHeight(18)
        if on_author_click:
            author_clickable.clicked.connect(lambda t: on_author_click(author))
        layout.addWidget(author_clickable)

        layout.addSpacing(14)

        tags_container = QWidget()
        tags_container.setStyleSheet("background: transparent; border: none;")
        tags_lay = QHBoxLayout(tags_container)
        tags_lay.setContentsMargins(0, 0, 0, 0)
        tags_lay.setSpacing(5)

        cat = book_data.get('category', get_text("category"))
        cat_bg, cat_fg = self._get_cat_colors(cat)
        cat_lbl = QLabel(cat)
        cat_lbl.setStyleSheet(
            f"background-color: {cat_bg}; color: {cat_fg}; border-radius: 5px; "
            f"padding: 3px 8px; font-size: 11px; font-weight: bold; border: none;")
        cat_lbl.setFixedHeight(24)
        tags_lay.addWidget(cat_lbl)

        status = book_data.get('reading_status', 'unread')
        status_map = {
            'read': (get_text("read"), "#DCFCE7", "#166534"),
            'in_progress': (get_text("in_progress"), "#FEF3C7", "#D97706"),
            'unread': (get_text("unread"), "#FCE7F3", "#DB2777")
        }
        s_text, s_bg, s_fg = status_map.get(status, status_map['unread'])
        stat_lbl = QLabel(s_text)
        stat_lbl.setStyleSheet(
            f"background-color: {s_bg}; color: {s_fg}; border-radius: 5px; "
            f"padding: 3px 8px; font-size: 11px; font-weight: bold; border: none;")
        stat_lbl.setFixedHeight(24)
        tags_lay.addWidget(stat_lbl)

        layout.addWidget(tags_container, alignment=Qt.AlignCenter)
        layout.addStretch()

        act_lay = QHBoxLayout()
        act_lay.setSpacing(12)

        def make_btn(icon_name, callback):
            b = IconButton(Assets.get_icon(icon_name), base_size=18, hover_scale=1.4)
            b.clicked.connect(lambda: callback(self.book_data))
            return b

        act_lay.addStretch()
        act_lay.addWidget(make_btn("add_list", on_add_to_list))
        act_lay.addWidget(make_btn("edit", on_edit))
        act_lay.addWidget(make_btn("remove", on_delete))
        act_lay.addStretch()
        layout.addLayout(act_lay)

    def enterEvent(self, event):
        self.raise_()
        if self.original_pos is None:
            self.original_pos = self.pos()
        self.setStyleSheet(self.hover_style)
        self.shadow.setBlurRadius(25)
        self.shadow.setColor(QColor(0, 0, 0, 60 if self.theme == "Light" else 100))
        self.anim.setDirection(QVariantAnimation.Forward)
        self.anim.start()

    def leaveEvent(self, event):
        self.setStyleSheet(self.default_style)
        self.shadow.setBlurRadius(15)
        self.shadow.setColor(QColor(0, 0, 0, 40 if self.theme == "Light" else 80))
        self.anim.setDirection(QVariantAnimation.Backward)
        self.anim.start()

    def _update_hover_effect(self, value):
        if self.original_pos:
            self.move(self.original_pos.x(), self.original_pos.y() - value)

    def _get_cat_colors(self, name):
        idx = hash(name) % len(CAT_COLORS)
        return CAT_COLORS[idx]

    def _load_cover(self):
        path = self.book_data.get('cover', 'default')
        pixmap = QPixmap()
        if path and path != 'default' and os.path.exists(path):
            pixmap.load(path)
        elif path.startswith("http"):
            try:
                r = requests.get(path, timeout=2)
                if r.status_code == 200: pixmap.loadFromData(r.content)
            except:
                pass

        if pixmap.isNull():
            pixmap = QPixmap(COVER_WIDTH, COVER_HEIGHT)
            pixmap.fill(QColor("#5A189A"))

        self.cover_lbl.setPixmap(
            pixmap.scaled(COVER_WIDTH, COVER_HEIGHT, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))


class BookList(QScrollArea):
    def __init__(self, parent, theme, books, on_edit, on_delete, on_add_to_list, on_author_click, on_category_click):
        super().__init__(parent)
        self.theme = theme
        self.setWidgetResizable(True)
        self.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.content = QWidget()
        self.content.setStyleSheet("background: transparent;")

        self.layout = QVBoxLayout(self.content)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.header = QLabel()
        self.header.setFont(QFont("Arial", 20, QFont.Bold))
        self.header.setStyleSheet(f"color: {PRIMARY_COLOR}; background: transparent;")
        self.header.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.header)

        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet("background: transparent;")
        self.grid = QGridLayout(self.grid_widget)
        self.grid.setSpacing(20)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.layout.addWidget(self.grid_widget)

        self.layout.addStretch()
        self.setWidget(self.content)

        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_add_to_list = on_add_to_list
        self.on_author_click = on_author_click
        self.on_category_click = on_category_click

        self._cards = []
        self._current_cols = 0

        self.update_books(books)

    def update_books(self, books):
        self.books = books[::-1]
        self.header.setText(get_text("books_count", count=len(self.books)))

        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._cards.clear()
        self._current_cols = 0

        for b in self.books:
            card = BookCard(b, self.theme, self.on_edit, self.on_delete, self.on_add_to_list,
                            self.on_author_click, self.on_category_click)
            self._cards.append(card)

        self._reflow_grid()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reflow_grid()

    def _reflow_grid(self):
        if not hasattr(self, '_cards') or not self._cards:
            return

        available_width = self.viewport().width() - 40
        card_total_width = CARD_WIDTH + 20

        cols = max(1, available_width // card_total_width)

        if hasattr(self, '_current_cols') and self._current_cols == cols:
            return
        self._current_cols = cols

        for i in reversed(range(self.grid.count())):
            self.grid.takeAt(i)

        for i, card in enumerate(self._cards):
            self.grid.addWidget(card, i // cols, i % cols)