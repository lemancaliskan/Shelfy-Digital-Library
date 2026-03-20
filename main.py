import customtkinter as ctk
import sys
import os
from tkinter import filedialog, messagebox
from data_manager import JSONManager
from ui_components import Sidebar, BookList, AddBookDialog, AddToListDialog
from PIL import Image
from assets_manager import Assets, initialize_assets, ico_path
from assets_manager import PRIMARY_COLOR, ACCENT_COLOR, BG_COLOR, LOCAL_SIDEBAR_BG
from ui_components import show_context_menu
from translations import get_text, get_language, set_language

ctk.set_appearance_mode("Light")

# DIMENSION CONSTANTS #
APP_WIDTH = 1000
APP_HEIGHT = 650


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(get_text("app_title"))

        initialize_assets()
        if os.path.exists(ico_path):
            self.iconbitmap(ico_path)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width / 2) - (APP_WIDTH / 2))
        y = int((screen_height / 2) - (APP_HEIGHT / 2))
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}+{x}+{y}")
        self.minsize(APP_WIDTH, APP_HEIGHT)

        self.bind_class("Entry", "<Button-3>", show_context_menu)
        self.bind_class("CTkEntry", "<Button-3>", show_context_menu)

        try:
            self.db = JSONManager()
        except Exception as e:
            messagebox.showerror(get_text("db_error"), get_text("db_error_msg", e=e))
            sys.exit(1)

        self.current_category = get_text("all")
        self.current_subcategory = get_text("all")
        self.current_search_term = ""
        self.current_reading_status = "all"
        self.current_stock_status = "all"
        self.current_list_type = "all_list"

        self.custom_lists = self.db.get_custom_lists()

        self.add_dialog = None
        self.add_list_dialog = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.create_widgets()
        self.load_books()

    def create_widgets(self):
        # SIDEBAR #
        self.sidebar = Sidebar(self,
                               categories=self.get_unique_categories(),
                               subcategories=self.get_unique_subcategories(get_text("all")),
                               custom_lists=self.custom_lists,
                               on_select_category=self.filter_by_category,
                               on_select_subcategory=self.filter_by_subcategory,
                               on_search_change=self.filter_by_search,
                               on_filter_change=self.filter_by_status,
                               on_add_list=self.add_custom_list,
                               on_delete_list=self.delete_custom_list,
                               on_list_select=self.select_list
                               )
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # MAIN FRAME #
        self.main_frame = ctk.CTkFrame(self, fg_color=BG_COLOR)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # HEADER #
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color=LOCAL_SIDEBAR_BG, height=70, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        logo_img = Assets.get_icon("logo", size=(180, 53))

        if logo_img:
            self.logo_label = ctk.CTkLabel(self.header_frame, image=logo_img, text="")
        else:
            self.logo_label = ctk.CTkLabel(self.header_frame, text="SHELFY",
                                           font=ctk.CTkFont(size=24, weight="bold"),
                                           text_color=PRIMARY_COLOR)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(18, 9), sticky="w")

        self.logo_label.configure(cursor="hand2")
        self.logo_label.bind("<Button-1>", self.reset_to_dashboard)

        # BOOK ADD BUTTON #
        self.add_button = ctk.CTkButton(
            self.header_frame,
            text=get_text("add_book"),
            image=Assets.get_icon("add_book", size=(20, 20)),
            compound="left",
            command=self.open_add_book_dialog,
            fg_color=PRIMARY_COLOR,
            hover_color=ACCENT_COLOR,
            text_color="white",
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=35
        )
        self.add_button.grid(row=0, column=1, padx=(0, 10), pady=15, sticky="e")

        # THEME TOGGLE #
        self.light_icon = Assets.get_icon("light_m", size=(20, 20))
        self.dark_icon = Assets.get_icon("dark_m", size=(20, 20))

        initial_icon = self.dark_icon if ctk.get_appearance_mode() == "Light" else self.light_icon

        self.theme_btn = ctk.CTkButton(
            self.header_frame,
            image=initial_icon,
            text="",
            width=20,
            height=20,
            fg_color="transparent",
            hover_color=ACCENT_COLOR,
            command=self.toggle_theme
        )
        self.theme_btn.grid(row=0, column=2, padx=(0, 10), pady=15, sticky="e")

        # LANGUAGE TOGGLE #
        self.lang_icon = Assets.get_icon("language", size=(20, 20))
        self.lang_btn = ctk.CTkButton(
            self.header_frame,
            image=self.lang_icon,
            text="",
            width=20,
            height=20,
            fg_color="transparent",
            hover_color=ACCENT_COLOR,
            command=self.toggle_language
        )
        self.lang_btn.grid(row=0, column=3, padx=(0, 20), pady=15, sticky="e")

        # BOOK LIST #
        self.book_list = BookList(self.main_frame, books=[],
                                  on_edit=self.edit_book,
                                  on_delete=self.delete_book_confirmation,
                                  on_add_to_list=self.open_add_to_list_dialog,
                                  on_author_click=self.filter_by_author,
                                  on_category_click=self.filter_by_category_from_card)
        self.book_list.grid(row=1, column=0, sticky="nsew", padx=0, pady=(0, 0))

    def reset_to_dashboard(self, event=None):
        self.current_category = get_text("all")
        self.current_subcategory = get_text("all")
        self.current_search_term = ""
        self.current_reading_status = "all"
        self.current_stock_status = "all"
        self.current_list_type = "all_list"

        self.sidebar.search_entry.delete(0, 'end')
        self.sidebar.category_status.set(get_text("all"))
        self.sidebar.subcategory_status.set(get_text("all"))
        self.sidebar.list_status.set(get_text("all_books"))

        if hasattr(self.sidebar, 'delete_list_btn'):
            self.sidebar.delete_list_btn.pack_forget()

        self.sidebar.reading_status.set("all")
        self.sidebar._update_filter_ui_toggle(self.sidebar.reading_buttons, "all")

        self.sidebar.stock_status.set("all")
        self.sidebar._update_filter_ui_toggle(self.sidebar.stock_buttons, "all")

        self.load_books()

    def toggle_theme(self):
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Light":
            new_mode = "Dark"
            self.theme_btn.configure(image=self.light_icon)
        else:
            new_mode = "Light"
            self.theme_btn.configure(image=self.dark_icon)
        ctk.set_appearance_mode(new_mode)

    def toggle_language(self):
        current = get_language()
        new_lang = "EN" if current == "TR" else "TR"
        set_language(new_lang)

        self.title(get_text("app_title"))
        self.current_category = get_text("all")
        self.current_subcategory = get_text("all")
        self.current_list_type = "all_list"

        self.sidebar.destroy()
        self.main_frame.destroy()
        self.create_widgets()
        self.load_books()

    def select_list(self, list_name):
        if list_name == get_text("all_books") or list_name == get_text("all"):
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
        self.sidebar.update_total_count(len(books))
        self.sidebar.update_categories(self.get_unique_categories())
        self.sidebar.update_subcategories(self.get_unique_subcategories(self.current_category))
        self.sidebar.update_lists(self.custom_lists)

    def get_unique_categories(self):
        data = self.db._load_data()
        books = data.get("books", [])
        categories = list(set([b['category'] for b in books if 'category' in b and b['category']]))
        all_text = get_text("all")
        if all_text not in categories:
            categories.insert(0, all_text)
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

        if all_text not in subcats:
            subcats.insert(0, all_text)
        return sorted(subcats, key=lambda x: (x != all_text, x))

    def get_all_categories_with_subcats(self):
        data = self.db._load_data()
        books = data.get("books", [])
        cat_dict = {}
        for b in books:
            c = b.get('category')
            sc = b.get('subcategory')
            if c:
                if c not in cat_dict:
                    cat_dict[c] = set()
                if sc:
                    cat_dict[c].add(sc)
        for c in cat_dict:
            cat_dict[c] = sorted(list(cat_dict[c]))
        return cat_dict

    def filter_by_category(self, category_name):
        self.current_category = category_name
        self.current_subcategory = get_text("all")
        self.sidebar.subcategory_status.set(get_text("all"))
        self.load_books()

    def filter_by_subcategory(self, subcategory_name):
        self.current_subcategory = subcategory_name
        self.load_books()

    def filter_by_category_from_card(self, category_name, subcategory_name=None):
        self.sidebar.category_status.set(category_name)
        self.current_category = category_name

        if subcategory_name:
            self.sidebar.subcategory_status.set(subcategory_name)
            self.current_subcategory = subcategory_name
        else:
            self.sidebar.subcategory_status.set(get_text("all"))
            self.current_subcategory = get_text("all")

        self.load_books()

    def filter_by_search(self, search_term):
        self.current_search_term = search_term
        self.load_books()

    def filter_by_status(self, reading=None, stock=None, list_type=None):
        if reading is not None:
            self.current_reading_status = reading
        if stock is not None:
            self.current_stock_status = stock
        if list_type is not None:
            self.current_list_type = list_type
        self.load_books()

    def filter_by_author(self, author_name):
        self.sidebar.search_entry.delete(0, 'end')
        self.sidebar.search_entry.insert(0, author_name)

        self.filter_by_search(author_name)

    def add_custom_list(self, list_name):
        invalid_names = [get_text("all"), "all_list", get_text("favorites"), "Favorilerim", "Favorites", "Klasikler"]
        if list_name in self.custom_lists or list_name in invalid_names:
            messagebox.showwarning(get_text("warning"), get_text("list_exists", list_name=list_name), parent=self)
            return
        self.db.add_custom_list(list_name)
        self.custom_lists = self.db.get_custom_lists()
        self.sidebar.update_lists(self.custom_lists)
        messagebox.showinfo(get_text("success"), get_text("list_created", list_name=list_name), parent=self)

    def delete_custom_list(self, list_name):
        try:
            self.db.delete_custom_list(list_name)
            self.custom_lists = self.db.get_custom_lists()
            if self.current_list_type == list_name:
                self.current_list_type = "all_list"
                if hasattr(self.sidebar, 'list_status'):
                    self.sidebar.list_status.set(get_text("all_books"))
            self.sidebar.update_lists(self.custom_lists)
            self.load_books()
            messagebox.showinfo(get_text("success"), get_text("list_deleted", list_name=list_name), parent=self)
        except Exception as e:
            messagebox.showerror(get_text("error"), get_text("list_delete_error", e=e), parent=self)

    def open_add_to_list_dialog(self, book_data):
        def save_book_lists(updated_lists):
            if self.db.update_book(book_data['id'], {'lists': updated_lists}):
                self.load_books()
            else:
                messagebox.showerror(get_text("error"), get_text("list_update_error"), parent=self)

        all_available_lists = ["Favorilerim"] + self.custom_lists
        dialog = AddToListDialog(self, book_data, all_available_lists, save_book_lists)
        self.wait_window(dialog)

    def open_add_book_dialog(self):
        if self.add_dialog is None or not self.add_dialog.winfo_exists():
            self.add_dialog = AddBookDialog(self,
                                            cat_dict=self.get_all_categories_with_subcats(),
                                            on_save_callback=self.add_book)
            self.wait_window(self.add_dialog)
            self.load_books()

    def add_book(self, data):
        try:
            success = self.db.add_book(
                title=data['title'],
                author=data['author'],
                isbn=data['isbn'],
                year=data['year'],
                publisher=data['publisher'],
                category=data['category'],
                subcategory=data.get('subcategory', ''),
                owned=(data['stockStatus'] == "available"),
                reading_status=data['readingStatus'],
                cover_path=data['cover']
            )
            if success:
                messagebox.showinfo(get_text("success"), get_text("book_added", title=data['title']))
                self.load_books()
                return True
        except Exception as e:
            messagebox.showerror(get_text("error"), get_text("book_add_error", e=e))
            return False

    def delete_book_confirmation(self, book_data):
        if messagebox.askyesno(get_text("delete_confirm"), get_text("book_delete_msg", title=book_data['title'])):
            book_id = book_data.get('id')
            self.delete_book(book_id)

    def delete_book(self, book_id):
        if self.db.delete_book(book_id):
            messagebox.showinfo(get_text("success"), get_text("book_deleted"))
            self.load_books()
        else:
            messagebox.showerror(get_text("error"), get_text("book_delete_error"))

    def edit_book(self, book_data):
        from ui_components import EditBookDialog
        def save_changes(updated_data):
            if self.db.update_book(updated_data['id'], updated_data):
                messagebox.showinfo(get_text("success"), get_text("book_updated"))
                self.load_books()
            else:
                messagebox.showerror(get_text("error"), get_text("book_update_error"))

        EditBookDialog(self, save_changes, book_data)

    def on_closing(self):
        try:
            if hasattr(self.db, 'close'):
                self.db.close()
        except Exception:
            pass
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()