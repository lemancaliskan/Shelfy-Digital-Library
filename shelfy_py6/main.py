import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, \
    QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from data_manager import JSONManager
from assets_manager import Assets, initialize_assets, ico_path, PRIMARY_COLOR, BG_COLOR_LIGHT, BG_COLOR_DARK
from ui_components import Sidebar, BookList, AddBookDialog, EditBookDialog, AddToListDialog, StyledButton, IconButton
from translations import get_text, get_language, set_language

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(get_text("app_title"))

        initialize_assets()
        if os.path.exists(ico_path):
            self.setWindowIcon(QIcon(ico_path))

        self.setMinimumSize(1100, 700)

        try:
            self.db = JSONManager()
        except Exception as e:
            QMessageBox.critical(self, get_text("db_error"), get_text("db_error_msg", e=e))
            sys.exit(1)

        self.current_theme = "Light"
        self.current_category = get_text("all")
        self.current_subcategory = get_text("all")
        self.current_search_term = ""
        self.current_reading_status = "all"
        self.current_stock_status = "all"
        self.current_list_type = "all_list"

        self.custom_lists = self.db.get_custom_lists()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.apply_theme()
        self.create_widgets()
        self.load_books()

    def apply_theme(self):
        bg = BG_COLOR_LIGHT if self.current_theme == "Light" else BG_COLOR_DARK
        fg = "black" if self.current_theme == "Light" else "white"
        sb_bg = "rgba(0,0,0,0.03)" if self.current_theme == "Light" else "rgba(255,255,255,0.03)"
        sb_handle = "rgba(97, 61, 193, 0.5)"
        sb_handle_hover = "rgba(97, 61, 193, 0.8)"

        qss = f"""
        QMainWindow {{ background-color: {bg}; }} 
        QWidget {{ background-color: {bg}; color: {fg}; }}

        QScrollArea {{ border: none; background: transparent; }}

        QScrollBar:vertical {{
            border: none;
            background: {sb_bg};
            width: 8px;
            border-radius: 4px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: {sb_handle};
            min-height: 30px;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {sb_handle_hover};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}

        QScrollBar:horizontal {{
            border: none;
            background: {sb_bg};
            height: 8px;
            border-radius: 4px;
            margin: 0px;
        }}
        QScrollBar::handle:horizontal {{
            background: {sb_handle};
            min-width: 30px;
            border-radius: 4px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {sb_handle_hover};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0px; }}
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: none; }}
        """
        self.setStyleSheet(qss)

    def create_widgets(self):
        for i in reversed(range(self.main_layout.count())):
            widget = self.main_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        self.sidebar = Sidebar(self, theme=self.current_theme,
                               categories=self.get_unique_categories(),
                               subcategories=self.get_unique_subcategories(get_text("all")),
                               custom_lists=self.custom_lists,
                               on_select_category=self.filter_by_category,
                               on_select_subcategory=self.filter_by_subcategory,
                               on_search_change=self.filter_by_search,
                               on_filter_change=self.filter_by_status,
                               on_add_list=self.add_custom_list,
                               on_delete_list=self.delete_custom_list,
                               on_list_select=self.select_list)
        self.main_layout.addWidget(self.sidebar)

        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(0)

        self.header = QWidget()
        self.header.setFixedHeight(80)
        self.header.setStyleSheet("border-bottom: 1px solid rgba(151, 223, 252, 0.3);")
        h_layout = QHBoxLayout(self.header)
        h_layout.setContentsMargins(20, 10, 20, 10)

        logo_pix = Assets.get_logo()
        self.logo_lbl = QLabel()
        if not logo_pix.isNull():
            self.logo_lbl.setPixmap(logo_pix.scaledToHeight(50, Qt.SmoothTransformation))
        else:
            self.logo_lbl.setText("SHELFY")
            self.logo_lbl.setFont(QFont("Arial", 24, QFont.Bold))
            self.logo_lbl.setStyleSheet(f"color: {PRIMARY_COLOR};")
        self.logo_lbl.setCursor(Qt.PointingHandCursor)
        self.logo_lbl.mousePressEvent = self.reset_to_dashboard
        h_layout.addWidget(self.logo_lbl)
        h_layout.addStretch()

        self.add_btn = StyledButton(get_text("add_book"), Assets.get_icon("add_book"), is_primary=True)
        self.add_btn.clicked.connect(self.open_add_book_dialog)
        h_layout.addWidget(self.add_btn)

        self.theme_btn = IconButton(Assets.get_icon("dark_m" if self.current_theme == "Light" else "light_m"),
                                    base_size=24, hover_scale=1.2)
        self.theme_btn.clicked.connect(self.toggle_theme)
        h_layout.addWidget(self.theme_btn)

        self.lang_btn = IconButton(Assets.get_icon("language"), base_size=24, hover_scale=1.2)
        self.lang_btn.clicked.connect(self.toggle_language)
        h_layout.addWidget(self.lang_btn)

        self.right_layout.addWidget(self.header)

        self.book_list = BookList(self, theme=self.current_theme, books=[],
                                  on_edit=self.edit_book,
                                  on_delete=self.delete_book_confirmation,
                                  on_add_to_list=self.open_add_to_list_dialog,
                                  on_author_click=self.filter_by_author,
                                  on_category_click=self.filter_by_category_from_card)
        self.right_layout.addWidget(self.book_list)

        self.main_layout.addWidget(self.right_panel)

    def reset_to_dashboard(self, event=None):
        self.current_category = get_text("all")
        self.current_subcategory = get_text("all")
        self.current_search_term = ""
        self.current_reading_status = "all"
        self.current_stock_status = "all"
        self.current_list_type = "all_list"

        self.sidebar.search_entry.clear()
        self.sidebar.cat_combo.setCurrentText(get_text("all"))
        self.sidebar.list_combo.setCurrentText(get_text("all_books"))

        for b in self.sidebar.read_btn_group:
            b.setChecked(b.text() == get_text("all"))
        for b in self.sidebar.stock_btn_group:
            b.setChecked(b.text() == get_text("all"))

        self.load_books()

    def toggle_theme(self):
        self.current_theme = "Dark" if self.current_theme == "Light" else "Light"
        self.theme_btn.setIcon(Assets.get_icon("dark_m" if self.current_theme == "Light" else "light_m"))
        self.apply_theme()
        self.create_widgets()
        self.load_books()

    def toggle_language(self):
        new_lang = "EN" if get_language() == "TR" else "TR"
        set_language(new_lang)
        self.setWindowTitle(get_text("app_title"))
        self.current_category = get_text("all")
        self.current_subcategory = get_text("all")
        self.current_list_type = "all_list"
        self.create_widgets()
        self.load_books()

    def select_list(self, list_name):
        if list_name in [get_text("all_books"), get_text("all")]:
            self.current_list_type = "all_list"
        elif list_name == get_text("favorites"):
            self.current_list_type = "favorites"
        else:
            self.current_list_type = list_name
        self.load_books()

    def load_books(self):
        books = self.db.get_filtered_books(
            search_query=self.current_search_term,
            category=self.current_category,
            subcategory=self.current_subcategory,
            status=self.current_reading_status,
            stock=self.current_stock_status,
            list_type=self.current_list_type
        )
        self.book_list.update_books(books)

        self.sidebar.update_categories(self.get_unique_categories())
        self.sidebar.update_subcategories(self.get_unique_subcategories(self.current_category))
        self.sidebar.update_lists(self.custom_lists)

        self.sidebar.update_stats(len(books))

    def get_unique_categories(self):
        data = self.db._load_data()
        books = data.get("books", [])
        categories = list(set([b['category'] for b in books if 'category' in b and b['category']]))
        all_text = get_text("all")
        if all_text not in categories: categories.insert(0, all_text)
        return sorted(categories, key=lambda x: (x != all_text, x))

    def get_unique_subcategories(self, category_name):
        data = self.db._load_data()
        books = data.get("books", [])
        all_text = get_text("all")
        if category_name == all_text:
            subcats = list(set([b.get('subcategory', '') for b in books if b.get('subcategory')]))
        else:
            subcats = list(set([b.get('subcategory', '') for b in books if
                                b.get('category') == category_name and b.get('subcategory')]))
        if all_text not in subcats: subcats.insert(0, all_text)
        return sorted(subcats, key=lambda x: (x != all_text, x))

    def get_all_categories_with_subcats(self):
        data = self.db._load_data()
        books = data.get("books", [])
        cat_dict = {}
        for b in books:
            c = b.get('category')
            sc = b.get('subcategory')
            if c:
                if c not in cat_dict: cat_dict[c] = set()
                if sc: cat_dict[c].add(sc)
        for c in cat_dict: cat_dict[c] = sorted(list(cat_dict[c]))
        return cat_dict

    def filter_by_category(self, category_name):
        self.current_category = category_name
        self.current_subcategory = get_text("all")
        self.load_books()

    def filter_by_subcategory(self, subcategory_name):
        self.current_subcategory = subcategory_name
        self.load_books()

    def filter_by_category_from_card(self, category_name, subcategory_name=None):
        self.current_category = category_name
        self.sidebar.cat_combo.setCurrentText(category_name)
        if subcategory_name:
            self.current_subcategory = subcategory_name
            self.sidebar.subcat_combo.setCurrentText(subcategory_name)
        else:
            self.current_subcategory = get_text("all")
            self.sidebar.subcat_combo.setCurrentText(get_text("all"))
        self.load_books()

    def filter_by_search(self, search_term):
        self.current_search_term = search_term
        self.load_books()

    def filter_by_status(self, reading=None, stock=None, list_type=None):
        if reading is not None: self.current_reading_status = reading
        if stock is not None: self.current_stock_status = stock
        if list_type is not None: self.current_list_type = list_type
        self.load_books()

    def filter_by_author(self, author_name):
        self.sidebar.search_entry.setText(author_name)
        self.filter_by_search(author_name)

    def add_custom_list(self, list_name):
        invalid_names = [get_text("all"), "all_list", get_text("favorites"), "Favorilerim", "Favorites", "Klasikler"]
        if list_name in self.custom_lists or list_name in invalid_names:
            QMessageBox.warning(self, get_text("warning"), get_text("list_exists", list_name=list_name))
            return
        self.db.add_custom_list(list_name)
        self.custom_lists = self.db.get_custom_lists()
        self.sidebar.update_lists(self.custom_lists)
        QMessageBox.information(self, get_text("success"), get_text("list_created", list_name=list_name))

    def delete_custom_list(self, list_name):
        try:
            self.db.delete_custom_list(list_name)
            self.custom_lists = self.db.get_custom_lists()
            if self.current_list_type == list_name:
                self.current_list_type = "all_list"
                self.sidebar.list_combo.setCurrentText(get_text("all_books"))
            self.sidebar.update_lists(self.custom_lists)
            self.load_books()
            QMessageBox.information(self, get_text("success"), get_text("list_deleted", list_name=list_name))
        except Exception as e:
            QMessageBox.critical(self, get_text("error"), get_text("list_delete_error", e=e))

    def open_add_to_list_dialog(self, book_data):
        def save_book_lists(updated_lists):
            if self.db.update_book(book_data['id'], {'lists': updated_lists}):
                self.load_books()
            else:
                QMessageBox.critical(self, get_text("error"), get_text("list_update_error"))

        all_available_lists = ["Favorilerim"] + self.custom_lists
        dlg = AddToListDialog(self, book_data, all_available_lists, save_book_lists)
        dlg.exec()

    def open_add_book_dialog(self):
        dlg = AddBookDialog(self, self.get_all_categories_with_subcats(), self.add_book)
        if dlg.exec():
            self.load_books()

    def add_book(self, data):
        try:
            success = self.db.add_book(
                title=data['title'], author=data['author'], isbn=data['isbn'], year=data['year'],
                publisher=data['publisher'], category=data['category'], subcategory=data.get('subcategory', ''),
                owned=(data['stockStatus'] == "available"), reading_status=data['readingStatus'],
                cover_path=data['cover']
            )
            if success:
                QMessageBox.information(self, get_text("success"), get_text("book_added", title=data['title']))
                return True
        except Exception as e:
            QMessageBox.critical(self, get_text("error"), get_text("book_add_error", e=e))
            return False

    def delete_book_confirmation(self, book_data):
        reply = QMessageBox.question(self, get_text("delete_confirm"),
                                     get_text("book_delete_msg", title=book_data['title']))
        if reply == QMessageBox.Yes:
            self.delete_book(book_data.get('id'))

    def delete_book(self, book_id):
        if self.db.delete_book(book_id):
            QMessageBox.information(self, get_text("success"), get_text("book_deleted"))
            self.load_books()
        else:
            QMessageBox.critical(self, get_text("error"), get_text("book_delete_error"))

    def edit_book(self, book_data):
        def save_changes(updated_data):
            if self.db.update_book(updated_data['id'], updated_data):
                QMessageBox.information(self, get_text("success"), get_text("book_updated"))
                self.load_books()
            else:
                QMessageBox.critical(self, get_text("error"), get_text("book_update_error"))

        dlg = EditBookDialog(self, save_changes, book_data)
        dlg.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())