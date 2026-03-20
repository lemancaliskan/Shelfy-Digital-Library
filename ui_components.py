import customtkinter as ctk
from PIL import Image, ImageOps
import os
from tkinter import filedialog, messagebox
import tkinter as tk
from assets_manager import Assets
from assets_manager import PRIMARY_COLOR, ACCENT_COLOR, BG_COLOR, TEXT_COLOR, LIGHT_TEXT_COLOR, BUTTON_TEXT_COLOR
from assets_manager import LOCAL_CARD_BG, LOCAL_SIDEBAR_BG, CAT_COLORS
from assets_manager import SIDEBAR_WIDTH, CARD_WIDTH, CARD_HEIGHT, COVER_WIDTH, COVER_HEIGHT
from assets_manager import DIALOG_WIDTH, DIALOG_HEIGHT, DIALOG_PADX, ADD_LIST_DIALOG_HEIGHT
from assets_manager import FIXED_BUTTON_WIDTH, BUTTON_HEIGHT, SEARCH_BOX_WIDTH


def show_context_menu(event):
    menu = tk.Menu(None, tearoff=0)

    widget = event.widget

    menu.add_command(label="Kes", command=lambda: widget.event_generate("<<Cut>>"))
    menu.add_command(label="Kopyala", command=lambda: widget.event_generate("<<Copy>>"))
    menu.add_command(label="Yapıştır", command=lambda: widget.event_generate("<<Paste>>"))
    menu.add_separator()
    menu.add_command(label="Tümünü Seç", command=lambda: widget.event_generate("<<SelectAll>>"))
    menu.tk_popup(event.x_root, event.y_root)

# =======================
# ADD LIST DIALOG
# =======================
class AddListDialog(ctk.CTkToplevel):
    def __init__(self, master, on_save_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.on_save_callback = on_save_callback
        self.transient(master)
        self.title("Yeni Liste Oluştur")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = int((screen_width / 2) - (DIALOG_WIDTH / 2))
        y = int((screen_height / 2) - (ADD_LIST_DIALOG_HEIGHT / 2))

        self.geometry(f"{DIALOG_WIDTH}x{ADD_LIST_DIALOG_HEIGHT}+{x}+{y}")
        self.resizable(False, False)

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.grab_set()

        self.grid_rowconfigure((0, 1), weight=0)
        self.grid_columnconfigure(0, weight=1)

        content_frame = ctk.CTkFrame(self, fg_color=BG_COLOR)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)

        ctk.CTkLabel(content_frame, text="Liste Adı", font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_COLOR).grid(row=0, column=0, padx=DIALOG_PADX, pady=(15, 0), sticky="w")
        self.list_name_entry = ctk.CTkEntry(content_frame, placeholder_text="Örn: Favorilerim",
                                            fg_color=LOCAL_CARD_BG, border_color=PRIMARY_COLOR,
                                            border_width=1, corner_radius=12, height=40)
        self.list_name_entry.grid(row=1, column=0, padx=DIALOG_PADX, pady=(3, 15), sticky="ew")

        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, padx=DIALOG_PADX, pady=(15, 15), sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        ctk.CTkButton(button_frame, text="İptal", command=self.destroy,
                      fg_color=LOCAL_CARD_BG, text_color=TEXT_COLOR, hover_color=ACCENT_COLOR,
                      corner_radius=12, height=40, border_color=PRIMARY_COLOR, border_width=1).grid(row=0, column=0,
                                                                                                    padx=(0, 10),
                                                                                                    sticky="ew")

        ctk.CTkButton(button_frame, text="Oluştur", command=self._save_list,
                      fg_color=PRIMARY_COLOR, hover_color=ACCENT_COLOR,
                      corner_radius=12, height=40).grid(row=0, column=1, padx=(10, 0), sticky="ew")

    def _save_list(self):
        list_name = self.list_name_entry.get().strip()
        if not list_name:
            messagebox.showerror("Hata", "Liste Adı boş bırakılamaz.", parent=self)
            return
        self.on_save_callback(list_name)
        self.destroy()


# =======================
# SIDEBAR #
# =======================
class Sidebar(ctk.CTkScrollableFrame):
    def __init__(self, master, categories, subcategories, custom_lists, on_list_select, on_select_category,
                 on_select_subcategory, on_search_change,
                 on_filter_change,
                 on_add_list, on_delete_list, **kwargs):
        super().__init__(master, fg_color=LOCAL_SIDEBAR_BG, corner_radius=0, width=SIDEBAR_WIDTH,
                         scrollbar_fg_color=LOCAL_SIDEBAR_BG,
                         **kwargs)
        self.grid_propagate()
        self.columnconfigure(0, weight=1)

        self.categories = categories
        self.subcategories = subcategories
        self.on_select_category = on_select_category
        self.on_select_subcategory = on_select_subcategory
        self.on_search_change = on_search_change
        self.on_filter_change = on_filter_change
        self.on_list_select = on_list_select
        self.on_add_list = on_add_list
        self.on_delete_list = on_delete_list

        self.category_status = ctk.StringVar(value=getattr(self.master, 'current_category', "Tümü"))
        self.subcategory_status = ctk.StringVar(value=getattr(self.master, 'current_subcategory', "Tümü"))
        self.list_status = ctk.StringVar(value=getattr(self.master, 'current_list_type', "all_list"))
        self.reading_status = ctk.StringVar(value="all")
        self.stock_status = ctk.StringVar(value="all")
        self.custom_lists = custom_lists if custom_lists is not None else []

        self.reading_buttons = {}
        self.stock_buttons = {}

        row_idx = 0

        search_header_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_header_frame.grid(row=row_idx, column=0, padx=20, pady=(20, 5), sticky="ew")
        search_header_frame.columnconfigure(0, weight=1)
        row_idx += 1

        ctk.CTkLabel(
            search_header_frame,
            text="ARA",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=ACCENT_COLOR
        ).grid(row=0, column=0, sticky="w")

        search_icon_button = ctk.CTkButton(
            search_header_frame,
            text="",
            image=Assets.get_icon("search", size=(16, 16)),
            command=lambda: on_search_change(self.search_entry.get()),
            width=24,
            height=24,
            corner_radius=5,
            fg_color="transparent",
            text_color=PRIMARY_COLOR,
            hover_color=LOCAL_CARD_BG
        )
        search_icon_button.grid(row=0, column=1, sticky="e")

        self.search_entry = ctk.CTkEntry(
            self,
            placeholder_text="Kitap ara...",
            fg_color=BG_COLOR,
            border_color=PRIMARY_COLOR,
            border_width=1,
            corner_radius=12,
            height=30,
            width=SEARCH_BOX_WIDTH
        )
        self.search_entry.grid(row=row_idx, column=0, padx=20, pady=(0, 10), sticky="n")
        row_idx += 1

        self.search_entry.bind('<KeyRelease>', lambda event: on_search_change(self.search_entry.get()))

        # CATEGORIES #
        ctk.CTkLabel(self, text="KATEGORİLER", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=ACCENT_COLOR).grid(row=row_idx, column=0, padx=20, pady=(15, 5), sticky="w")
        row_idx += 1

        self.category_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.category_frame.grid(row=row_idx, column=0, padx=20, pady=(0, 5), sticky="ew")
        self.category_frame.columnconfigure(0, weight=1)
        row_idx += 1

        self._create_category_combo()

        # SUBCATEGORIES #
        self.subcat_label = ctk.CTkLabel(self, text="ALT KATEGORİLER", font=ctk.CTkFont(size=12, weight="bold"),
                                         text_color=ACCENT_COLOR)
        self.subcat_label.grid(row=row_idx, column=0, padx=20, pady=(15, 5), sticky="w")
        row_idx += 1

        self.subcategory_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.subcategory_frame.grid(row=row_idx, column=0, padx=20, pady=(0, 5), sticky="ew")
        self.subcategory_frame.columnconfigure(0, weight=1)
        row_idx += 1

        self._create_subcategory_combo()

        # LİSTS #
        list_header_frame = ctk.CTkFrame(self, fg_color="transparent")
        list_header_frame.grid(row=row_idx, column=0, padx=20, pady=(15, 5), sticky="ew")
        list_header_frame.columnconfigure(0, weight=1)
        row_idx += 1

        ctk.CTkLabel(list_header_frame, text="LİSTELERİM", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=ACCENT_COLOR).grid(row=0, column=0, sticky="w")

        self.delete_list_btn = ctk.CTkButton(
            list_header_frame,
            text="",
            image=Assets.get_icon("list_del", size=(18, 18)),
            command=self._delete_selected_list,
            width=24,
            height=24,
            corner_radius=5,
            fg_color="transparent",
            hover_color=LOCAL_CARD_BG
        )
        self.delete_list_btn.grid(row=0, column=1, padx=(0, 5), sticky="e")

        add_list_button = ctk.CTkButton(
            list_header_frame,
            text="",
            image=Assets.get_icon("list_add", size=(18, 18)),
            command=self._open_add_list_dialog,
            width=24,
            height=24,
            corner_radius=5,
            fg_color="transparent",
            text_color=PRIMARY_COLOR,
            hover_color=LOCAL_CARD_BG
        )
        add_list_button.grid(row=0, column=2, sticky="e")

        self.list_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.list_frame.grid(row=row_idx, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.list_frame.columnconfigure(0, weight=1)
        row_idx += 1

        self._create_list_combo()

        # READING STATUS #
        ctk.CTkLabel(self, text="OKUMA DURUMU", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=ACCENT_COLOR).grid(row=row_idx, column=0, padx=20, pady=(15, 5), sticky="w")
        row_idx += 1

        self.reading_filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.reading_filter_frame.grid(row=row_idx, column=0, padx=20, pady=(0, 10), sticky="ew")
        row_idx += 1
        self.reading_filter_frame.columnconfigure((0, 1, 2), weight=1)

        self.btn_reading_all = self._create_filter_button(self.reading_filter_frame, "Tümü", "all", self.reading_status,
                                                          lambda value: on_filter_change(reading=value),
                                                          self.reading_buttons)
        self.btn_reading_all.grid(row=0, column=0, padx=5, pady=5, sticky="n")

        self.btn_reading_read = self._create_filter_button(self.reading_filter_frame, "Okundu", "read",
                                                           self.reading_status,
                                                           lambda value: on_filter_change(reading=value),
                                                           self.reading_buttons)
        self.btn_reading_read.grid(row=0, column=1, padx=5, pady=5, sticky="n")

        self.btn_reading_inprogress = self._create_filter_button(self.reading_filter_frame, "Okunuyor", "in_progress",
                                                                 self.reading_status,
                                                                 lambda value: on_filter_change(reading=value),
                                                                 self.reading_buttons)
        self.btn_reading_inprogress.grid(row=0, column=2, padx=5, pady=5, sticky="n")

        self.btn_reading_unread = self._create_filter_button(self.reading_filter_frame, "Okunacak", "unread",
                                                             self.reading_status,
                                                             lambda value: on_filter_change(reading=value),
                                                             self.reading_buttons)
        self.btn_reading_unread.grid(row=1, column=0, padx=5, pady=5, sticky="n")

        # STOCK STATUS #
        ctk.CTkLabel(self, text="STOK DURUMU", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=ACCENT_COLOR).grid(row=row_idx, column=0, padx=20, pady=(15, 5), sticky="w")
        row_idx += 1

        self.stock_filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stock_filter_frame.grid(row=row_idx, column=0, padx=20, pady=(0, 10), sticky="ew")
        row_idx += 1
        self.stock_filter_frame.columnconfigure((0, 1, 2), weight=1)

        self.btn_stock_all = self._create_filter_button(self.stock_filter_frame, "Tümü", "all", self.stock_status,
                                                        lambda value: on_filter_change(stock=value), self.stock_buttons)
        self.btn_stock_all.grid(row=0, column=0, padx=5, pady=5, sticky="n")

        self.btn_stock_available = self._create_filter_button(self.stock_filter_frame, "Elimde", "available",
                                                              self.stock_status,
                                                              lambda value: on_filter_change(stock=value),
                                                              self.stock_buttons)
        self.btn_stock_available.grid(row=0, column=1, padx=5, pady=5, sticky="n")

        self.btn_stock_borrowed = self._create_filter_button(self.stock_filter_frame, "Ödünç Verildi", "borrowed",
                                                             self.stock_status,
                                                             lambda value: on_filter_change(stock=value),
                                                             self.stock_buttons)
        self.btn_stock_borrowed.grid(row=1, column=0, padx=5, pady=5, sticky="n")

        # BOOK COUNTS #
        self.total_count_frame = ctk.CTkFrame(self, fg_color=PRIMARY_COLOR, corner_radius=12)
        self.total_count_frame.grid(row=row_idx, column=0, padx=20, pady=(20, 20), sticky="ew")
        row_idx += 1

        self.icon_label = ctk.CTkLabel(
            self.total_count_frame,
            text="",
            image=Assets.get_icon("book", size=(40, 40))
        )
        self.icon_label.pack(side="left", padx=(15, 5), pady=10)

        text_f = ctk.CTkFrame(self.total_count_frame, fg_color="transparent")
        text_f.pack(side="left", padx=(10, 15), pady=10)

        self.total_label = ctk.CTkLabel(
            text_f,
            text="Toplam Kitap",
            text_color="#E0E0E0",
            font=ctk.CTkFont(size=14)
        )
        self.total_label.pack(anchor="center")

        self.count_label = ctk.CTkLabel(
            text_f,
            text="0",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.count_label.pack(anchor="center")

        self._toggle_subcategory_visibility()

    def _toggle_subcategory_visibility(self):
        current_cat = self.category_status.get()
        if current_cat == "Tümü" or current_cat == "":
            self.subcat_label.grid_remove()
            self.subcategory_frame.grid_remove()
        else:
            self.subcat_label.grid()
            self.subcategory_frame.grid()

    # COMBOBOX #
    def _create_category_combo(self):

        for widget in self.category_frame.winfo_children():
            widget.destroy()

        categories_list = ["Tümü"] + [c for c in self.categories if c != "Tümü"]

        self.category_combo = ctk.CTkComboBox(
            self.category_frame,
            values=categories_list,
            command=self.on_select_category,
            variable=self.category_status,
            height=30,
            corner_radius=12,
            fg_color=BG_COLOR,
            border_color=PRIMARY_COLOR,
            border_width=1,
            button_color=PRIMARY_COLOR,
            button_hover_color=ACCENT_COLOR,
            dropdown_fg_color=BG_COLOR,
            dropdown_hover_color=ACCENT_COLOR,
            dropdown_text_color=TEXT_COLOR,
            text_color=TEXT_COLOR,
            font=ctk.CTkFont(size=13),
            state="readonly"
        )
        self.category_combo.pack(padx=5, pady=5, fill="x")

    def _create_subcategory_combo(self):
        for widget in self.subcategory_frame.winfo_children():
            widget.destroy()

        subcats_list = ["Tümü"] + [c for c in self.subcategories if c != "Tümü"]

        self.subcategory_combo = ctk.CTkComboBox(
            self.subcategory_frame,
            values=subcats_list,
            command=self.on_select_subcategory,
            variable=self.subcategory_status,
            height=30,
            corner_radius=12,
            fg_color=BG_COLOR,
            border_color=PRIMARY_COLOR,
            border_width=1,
            button_color=PRIMARY_COLOR,
            button_hover_color=ACCENT_COLOR,
            dropdown_fg_color=BG_COLOR,
            dropdown_hover_color=ACCENT_COLOR,
            dropdown_text_color=TEXT_COLOR,
            text_color=TEXT_COLOR,
            font=ctk.CTkFont(size=13),
            state="readonly"
        )
        self.subcategory_combo.pack(padx=5, pady=5, fill="x")

    def _create_list_combo(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        self.list_options = ["📚 Tüm Kitaplar", "⭐ Favorilerim"]
        self.list_options.extend(self.custom_lists)

        current_val = getattr(self.master, 'current_list_type', "all_list")
        if current_val == "all_list":
            self.list_status.set("📚 Tüm Kitaplar")
        elif current_val == "favorites":
            self.list_status.set("⭐ Favorilerim")
        else:
            self.list_status.set(current_val)

        self.list_combo = ctk.CTkComboBox(
            self.list_frame,
            values=self.list_options,
            command=self._on_list_combo_change,
            variable=self.list_status,
            height=30,
            corner_radius=12,
            fg_color=BG_COLOR,
            border_color=PRIMARY_COLOR,
            border_width=1,
            button_color=PRIMARY_COLOR,
            button_hover_color=ACCENT_COLOR,
            dropdown_fg_color=BG_COLOR,
            dropdown_hover_color=ACCENT_COLOR,
            dropdown_text_color=TEXT_COLOR,
            text_color=TEXT_COLOR,
            font=ctk.CTkFont(size=13),
            state="readonly"
        )
        self.list_combo.pack(padx=5, pady=5, fill="x")

        if self.list_status.get() not in ["📚 Tüm Kitaplar", "⭐ Favorilerim"]:
            self.delete_list_btn.grid()
        else:
            self.delete_list_btn.grid_remove()

    def _on_list_combo_change(self, choice):
        if choice == "📚 Tüm Kitaplar":
            self.on_filter_change(list_type="all_list")
            self.delete_list_btn.grid_remove()
        elif choice == "⭐ Favorilerim":
            self.on_filter_change(list_type="favorites")
            self.delete_list_btn.grid_remove()
        else:
            self.on_filter_change(list_type=choice)
            self.delete_list_btn.grid()

    def _delete_selected_list(self):
        selected = self.list_status.get()

        if selected in ["📚 Tüm Kitaplar", "⭐ Favorilerim"]:
            messagebox.showwarning("Uyarı", f"'{selected}' listesi sistem listesidir ve silinemez!")
            return

        if messagebox.askyesno("Liste Silme", f"'{selected}' listesini silmek istediğinizden emin misiniz?"):
            self.on_delete_list(selected)
            self.list_status.set("📚 Tüm Kitaplar")

            if hasattr(self, 'delete_list_btn'):
                self.delete_list_btn.grid_remove()

    def update_categories(self, new_categories):
        self.categories = new_categories
        categories_list = ["Tümü"] + [c for c in self.categories if c != "Tümü"]
        self.category_combo.configure(values=categories_list)

    def update_subcategories(self, new_subcategories):
        self.subcategories = new_subcategories
        subcats_list = ["Tümü"] + [c for c in self.subcategories if c != "Tümü"]
        if hasattr(self, 'subcategory_combo'):
            self.subcategory_combo.configure(values=subcats_list)
        self._toggle_subcategory_visibility()

    def update_lists(self, new_custom_lists):
        self.custom_lists = new_custom_lists
        self.list_options = ["📚 Tüm Kitaplar", "⭐ Favorilerim"]
        self.list_options.extend(self.custom_lists)
        self.list_combo.configure(values=self.list_options)

    def _open_add_list_dialog(self):
        if not hasattr(self.master,
                       'add_list_dialog') or self.master.add_list_dialog is None or not self.master.add_list_dialog.winfo_exists():
            self.master.add_list_dialog = AddListDialog(self.master, self.on_add_list)
        self.master.add_list_dialog.focus()

    def update_total_count(self, count):
        self.count_label.configure(text=str(count))

    # TOGGLE BUTTONS #
    def _create_filter_button(self, parent, text, value, var, command, buttons_dict):
        btn_kwargs = {
            "text": text,
            "command": lambda: button_command(),
            "corner_radius": 20,
            "font": ctk.CTkFont(size=13, weight="bold"),
            "height": BUTTON_HEIGHT
        }
        btn = ctk.CTkButton(parent, **btn_kwargs)
        buttons_dict[value] = btn

        def button_command():
            current_value = var.get()
            new_value = "all" if current_value == value else value
            var.set(new_value)
            command(new_value)
            self._update_filter_ui_toggle(buttons_dict, new_value)

        if value == var.get():
            btn.configure(fg_color=PRIMARY_COLOR, text_color=BUTTON_TEXT_COLOR, hover_color=ACCENT_COLOR,
                          border_width=0)
        else:
            btn.configure(fg_color=BG_COLOR, text_color=TEXT_COLOR, hover_color=LOCAL_CARD_BG,
                          border_color=PRIMARY_COLOR,
                          border_width=1)

        return btn

    def _update_filter_ui_toggle(self, buttons_dict, selected_value):
        for value, btn in buttons_dict.items():
            is_selected = (value == selected_value)
            if is_selected:
                btn.configure(fg_color=PRIMARY_COLOR, text_color=BUTTON_TEXT_COLOR, hover_color=ACCENT_COLOR,
                              border_width=0)
            else:
                btn.configure(fg_color=BG_COLOR, text_color=TEXT_COLOR, hover_color=LOCAL_CARD_BG,
                              border_color=PRIMARY_COLOR,
                              border_width=1)


# =======================
# ADD BOOK DIALOG
# =======================
class AddBookDialog(ctk.CTkToplevel):
    def __init__(self, master, cat_dict, on_save_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.on_save_callback = on_save_callback
        self.cat_dict = cat_dict
        self.transient(master)
        self.title("Yeni Kitap Ekle")

        self.reading_status_var = ctk.StringVar(value="unread")
        self.stock_status_var = ctk.StringVar(value="available")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = int((screen_width / 2) - (DIALOG_WIDTH / 2))
        y = int(screen_height * 0.05)

        self.geometry(f"{DIALOG_WIDTH}x{DIALOG_HEIGHT}+{x}+{y}")
        self.resizable(False, False)

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.grab_set()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color=BG_COLOR)
        self.scroll_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.scroll_frame.columnconfigure(0, weight=1)

        self._create_input_fields()

    def _create_label(self, parent, text, row):
        label = ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_COLOR)
        label.grid(row=row, column=0, padx=DIALOG_PADX, pady=(10, 2), sticky="w")
        return label

    def _create_entry(self, parent, placeholder, row):
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, fg_color=LOCAL_CARD_BG,
                             text_color=TEXT_COLOR, border_color=PRIMARY_COLOR, border_width=1,
                             corner_radius=12, height=40)
        entry.grid(row=row, column=0, padx=DIALOG_PADX, pady=(3, 8), sticky="ew")
        return entry

    def _create_toggle_buttons(self, parent, options, variable, button_width=100):
        outer_frame = ctk.CTkFrame(parent, fg_color="transparent")
        outer_frame.columnconfigure((0, 1, 2, 3), weight=1)
        inner_frame = ctk.CTkFrame(outer_frame, fg_color="transparent")
        inner_frame.pack(side="top")
        buttons = {}

        def update_selection(selected_value):
            variable.set(selected_value)
            for text, value in options:
                btn = buttons[value]
                if value == selected_value:
                    btn.configure(fg_color=PRIMARY_COLOR, text_color=BUTTON_TEXT_COLOR, hover_color=ACCENT_COLOR,
                                  border_width=0)
                else:
                    btn.configure(fg_color=LOCAL_CARD_BG, text_color=TEXT_COLOR, hover_color=BG_COLOR,
                                  border_color=PRIMARY_COLOR, border_width=1)

        for i, (text, value) in enumerate(options):
            btn = ctk.CTkButton(inner_frame, text=text, command=lambda v=value: update_selection(v), corner_radius=20,
                                font=ctk.CTkFont(size=13, weight="bold"), height=BUTTON_HEIGHT, width=button_width)
            if value == variable.get():
                btn.configure(fg_color=PRIMARY_COLOR, text_color=BUTTON_TEXT_COLOR, hover_color=ACCENT_COLOR,
                              border_width=0)
            else:
                btn.configure(fg_color=LOCAL_CARD_BG, text_color=TEXT_COLOR, hover_color=BG_COLOR,
                              border_color=PRIMARY_COLOR,
                              border_width=1)
            btn.grid(row=0, column=i, padx=(5 if i > 0 else 0, 5), sticky="n")
            buttons[value] = btn
        return outer_frame

    def _create_input_fields(self):
        row_idx = 0

        self._create_label(self.scroll_frame, "Kitap Adı *", row_idx)
        row_idx += 1
        self.title_entry = self._create_entry(self.scroll_frame, "Örn: 1984", row_idx)
        row_idx += 1

        self._create_label(self.scroll_frame, "Yazar *", row_idx)
        row_idx += 1
        self.author_entry = self._create_entry(self.scroll_frame, "Örn: George Orwell", row_idx)
        row_idx += 1

        self._create_label(self.scroll_frame, "Yayınevi *", row_idx)
        row_idx += 1
        self.publisher_entry = self._create_entry(self.scroll_frame, "Örn: Can Yayınları", row_idx)
        row_idx += 1

        self._create_label(self.scroll_frame, "ISBN * (13 Haneli)", row_idx)
        row_idx += 1
        self.isbn_entry = self._create_entry(self.scroll_frame, "Örn: 9781234567890", row_idx)
        row_idx += 1

        self._create_label(self.scroll_frame, "Kategori * (Seç/Yaz)", row_idx)
        row_idx += 1
        filtered_cats = [c for c in self.cat_dict.keys() if c != "Tümü"]
        self.category_combo = ctk.CTkComboBox(
            self.scroll_frame, values=filtered_cats, fg_color=LOCAL_CARD_BG,
            text_color=TEXT_COLOR, border_color=PRIMARY_COLOR, border_width=1,
            corner_radius=12, height=40, button_color=PRIMARY_COLOR, button_hover_color=ACCENT_COLOR,
            dropdown_fg_color=LOCAL_CARD_BG, dropdown_text_color=TEXT_COLOR, font=ctk.CTkFont(size=13),
            command=self._on_category_change
        )
        self.category_combo.grid(row=row_idx, column=0, padx=DIALOG_PADX, pady=(3, 8), sticky="ew")
        row_idx += 1

        self._create_label(self.scroll_frame, "Alt Kategori (Seç/Yaz)", row_idx)
        row_idx += 1
        self.subcategory_combo = ctk.CTkComboBox(
            self.scroll_frame, values=[], fg_color=LOCAL_CARD_BG,
            text_color=TEXT_COLOR, border_color=PRIMARY_COLOR, border_width=1,
            corner_radius=12, height=40, button_color=PRIMARY_COLOR, button_hover_color=ACCENT_COLOR,
            dropdown_fg_color=LOCAL_CARD_BG, dropdown_text_color=TEXT_COLOR, font=ctk.CTkFont(size=13)
        )
        self.subcategory_combo.grid(row=row_idx, column=0, padx=DIALOG_PADX, pady=(3, 8), sticky="ew")
        row_idx += 1

        self.category_combo.set("")
        self.subcategory_combo.set("")

        self._create_label(self.scroll_frame, "Basım Yılı", row_idx)
        row_idx += 1
        self.year_entry = self._create_entry(self.scroll_frame, "Örn: 2025", row_idx)
        row_idx += 1

        self._create_label(self.scroll_frame, "Okuma Durumu *", row_idx)
        row_idx += 1
        reading_options = [("Okunacak", "unread"), ("Okunuyor", "in_progress"), ("Okundu", "read")]
        self.reading_button_frame = self._create_toggle_buttons(self.scroll_frame, reading_options,
                                                                self.reading_status_var, FIXED_BUTTON_WIDTH)
        self.reading_button_frame.grid(row=row_idx, column=0, padx=DIALOG_PADX, pady=(3, 8), sticky="ew")
        row_idx += 1

        self._create_label(self.scroll_frame, "Stok Durumu *", row_idx)
        row_idx += 1
        stock_options = [("Elimde", "available"), ("Ödünç Verildi", "borrowed")]
        self.stock_button_frame = self._create_toggle_buttons(self.scroll_frame, stock_options, self.stock_status_var,
                                                              FIXED_BUTTON_WIDTH)
        self.stock_button_frame.grid(row=row_idx, column=0, padx=DIALOG_PADX, pady=(3, 8), sticky="ew")
        row_idx += 1

        self._create_label(self.scroll_frame, "Kapak Resmi (URL veya Dosya Yolu)", row_idx)
        row_idx += 1
        path_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        path_frame.grid(row=row_idx, column=0, padx=DIALOG_PADX, pady=(3, 15), sticky="ew")
        path_frame.columnconfigure(0, weight=1)

        self.cover_path_entry = ctk.CTkEntry(path_frame, placeholder_text="http://... veya Dosya seçin",
                                             fg_color=LOCAL_CARD_BG, border_color=PRIMARY_COLOR,
                                             border_width=1, corner_radius=12, height=40)
        self.cover_path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.browse_button = ctk.CTkButton(path_frame, text="Gözat", command=self._select_cover_path,
                                           fg_color=PRIMARY_COLOR, hover_color=ACCENT_COLOR, corner_radius=12,
                                           height=40, width=80)
        self.browse_button.grid(row=0, column=1, sticky="e")
        row_idx += 1

        # BUTTONS #
        button_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        button_frame.grid(row=row_idx, column=0, padx=DIALOG_PADX, pady=(15, 15), sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        ctk.CTkButton(button_frame, text="İptal", command=self.destroy, fg_color=LOCAL_CARD_BG, text_color=TEXT_COLOR,
                      hover_color=ACCENT_COLOR, corner_radius=12, height=40, border_color=PRIMARY_COLOR,
                      border_width=1).grid(row=0, column=0, padx=(0, 10), sticky="ew")

        ctk.CTkButton(button_frame, text="Ekle", command=self._save_book, fg_color=PRIMARY_COLOR,
                      hover_color=ACCENT_COLOR, corner_radius=12, height=40).grid(row=0, column=1, padx=(10, 0),
                                                                                  sticky="ew")

    def _on_category_change(self, choice):
        subcats = self.cat_dict.get(choice, [])
        filtered_subcats = [sc for sc in subcats if sc != "Tümü" and sc != ""]
        self.subcategory_combo.configure(values=filtered_subcats)
        if filtered_subcats:
            self.subcategory_combo.set(filtered_subcats[0])
        else:
            self.subcategory_combo.set("")

    def _select_cover_path(self):
        file_path = filedialog.askopenfilename(title="Kapak Resmi Seç",
                                               filetypes=[
                                                   ("Görsel Dosyaları", "*.png *.jpg *.jpeg *.bmp *.webp *.gif")])
        if file_path:
            self.cover_path_entry.delete(0, tk.END)
            self.cover_path_entry.insert(0, file_path)

    def _save_book(self):
        try:
            year_val = int(self.year_entry.get()) if self.year_entry.get() else None
        except ValueError:
            messagebox.showerror("Hata", "Yıl alanı sayı olmalıdır.")
            return

        data = {
            'title': self.title_entry.get().strip(),
            'author': self.author_entry.get().strip(),
            'isbn': self.isbn_entry.get().strip(),
            'publisher': self.publisher_entry.get().strip(),
            'category': self.category_combo.get().strip(),
            'subcategory': self.subcategory_combo.get().strip(),
            'year': year_val,
            'readingStatus': self.reading_status_var.get(),
            'stockStatus': self.stock_status_var.get(),
            'cover': self.cover_path_entry.get().strip()
        }

        if not all([data['title'], data['author'], data['isbn'], data['publisher'], data['category']]):
            messagebox.showerror("Hata", "Kitap Adı, Yazar, ISBN, Yayınevi ve Kategori zorunludur.")
            return

        self.on_save_callback(data)
        self.destroy()


# =======================
# BOOK LIST
# =======================
class BookList(ctk.CTkScrollableFrame):

    def __init__(self, master, books, on_edit, on_delete, on_add_to_list=None, on_author_click=None,
                 on_category_click=None, **kwargs):
        super().__init__(master, fg_color=BG_COLOR, label_text="Tüm Kitaplar", label_fg_color="transparent",
                         label_text_color=TEXT_COLOR, label_font=ctk.CTkFont(size=24, weight="bold"), **kwargs)
        self.books = books
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_add_to_list = on_add_to_list
        self.on_author_click = on_author_click
        self.on_category_click = on_category_click
        self.grid_columnconfigure((0, 1, 2, 3), weight=1, minsize=CARD_WIDTH + 30)
        self.update_books(books)

    def update_books(self, new_books):
        self.books = new_books[::-1]
        self.configure(label_text=f"Kitaplar ({len(new_books)})",
                       label_text_color=PRIMARY_COLOR)
        for widget in self.winfo_children():
            if widget.winfo_class() != 'CTkLabel':
                widget.destroy()
        for i, book in enumerate(self.books):
            row = i // 4
            col = i % 4
            card = BookCard(
                self,
                book_data=book,
                on_edit=self.on_edit,
                on_delete=self.on_delete,
                on_add_to_list=self.on_add_to_list,
                on_author_click=self.on_author_click,
                on_category_click=self.on_category_click)
            card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")


# =======================
# BOOK CARD
# =======================
class BookCard(ctk.CTkFrame):

    def __init__(self, master, book_data, on_edit, on_delete, on_add_to_list=None, on_author_click=None,
                 on_category_click=None, **kwargs):
        super().__init__(master, fg_color=LOCAL_CARD_BG, corner_radius=12, width=CARD_WIDTH, height=CARD_HEIGHT,
                         **kwargs)
        self.grid_propagate(False)
        self.book_data = book_data
        self.on_author_click = on_author_click
        self.on_category_click = on_category_click
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._load_cover_image()

        image_frame = ctk.CTkFrame(self, fg_color="transparent")
        image_frame.grid(row=0, column=0, padx=15, pady=(15, 0), sticky="n")

        image_label = ctk.CTkLabel(image_frame, text="", image=self.ctk_image, width=COVER_WIDTH, height=COVER_HEIGHT)
        image_label.pack()

        status = book_data.get('reading_status', 'unread')

        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.grid(row=1, column=0, padx=10, pady=(15, 5), sticky="ew")

        raw_title = book_data.get('title', 'Başlık Yok')
        raw_author = book_data.get('author', 'Bilinmiyor')

        MAX_TITLE_LEN = 40
        MAX_AUTHOR_LEN = 30

        display_title = raw_title if len(raw_title) <= MAX_TITLE_LEN else raw_title[:MAX_TITLE_LEN - 3] + "..."
        display_author = raw_author if len(raw_author) <= MAX_AUTHOR_LEN else raw_author[:MAX_AUTHOR_LEN - 3] + "..."

        ctk.CTkLabel(
            info_frame,
            text=display_title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_COLOR,
            wraplength=CARD_WIDTH - 25,
            justify="center"
        ).pack(anchor="center", fill="x")

        self.author_label = ctk.CTkLabel(
            info_frame,
            text=display_author,
            font=ctk.CTkFont(size=12),
            text_color=LIGHT_TEXT_COLOR,
            justify="center",
            cursor="hand2"
        )
        self.author_label.pack(anchor="center", fill="x", pady=(0, 2))

        if self.on_author_click:
            self.author_label.bind("<Button-1>", lambda e, a=raw_author: self.on_author_click(a))

        tag_frame = ctk.CTkFrame(self, fg_color="transparent")
        tag_frame.grid(row=2, column=0, padx=15, pady=(0, 10), sticky="n")

        tags_container = ctk.CTkFrame(tag_frame, fg_color="transparent")
        tags_container.pack(anchor="center")

        row1 = ctk.CTkFrame(tags_container, fg_color="transparent")
        row1.pack(anchor="center", pady=(0, 4))

        row2 = ctk.CTkFrame(tags_container, fg_color="transparent")

        cat_name = book_data.get('category', 'Kategori')
        cat_bg, cat_text = self._get_category_colors(cat_name)

        category_tag = ctk.CTkLabel(row1, text=cat_name, fg_color=cat_bg,
                                    text_color=cat_text, corner_radius=6, padx=7, height=26, font=ctk.CTkFont(size=12))
        category_tag.pack(side="left", padx=3)

        category_tag.configure(cursor="hand2")
        if self.on_category_click:
            category_tag.bind("<Button-1>", lambda e, c=cat_name: self.on_category_click(c))

        subcat_name = book_data.get('subcategory', '')
        if subcat_name:
            subcat_bg, subcat_text = self._get_category_colors(subcat_name + cat_name)
            subcat_tag = ctk.CTkLabel(row1, text=subcat_name, fg_color=subcat_bg,
                                      text_color=subcat_text, corner_radius=6, padx=7, height=26,
                                      font=ctk.CTkFont(size=12))
            subcat_tag.pack(side="left", padx=3)

            subcat_tag.configure(cursor="hand2")
            if self.on_category_click:
                subcat_tag.bind("<Button-1>", lambda e, c=cat_name, sc=subcat_name: self.on_category_click(c, sc))

            target_row_for_reading = row2
            row2.pack(anchor="center", pady=(4, 0))
        else:
            target_row_for_reading = row1

        if status == 'read':
            reading_text, reading_bg, reading_color = "Okundu", ("#DCFCE7", "#052e16"), ("#166534", "#4ade80")
        elif status == 'in_progress':
            reading_text, reading_bg, reading_color = "Okunuyor", ("#FEF3C7", "#451a03"), ("#D97706", "#fcd34d")
        else:
            reading_text, reading_bg, reading_color = "Okunacak", ("#FCE7F3", "#4c0519"), ("#DB2777", "#f43f5e")

        reading_tag = ctk.CTkLabel(target_row_for_reading, text=reading_text, fg_color=reading_bg,
                                   text_color=reading_color,
                                   corner_radius=6, padx=7, height=26, font=ctk.CTkFont(size=12))
        reading_tag.pack(side="left", padx=3)

        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=3, column=0, padx=15, pady=(5, 15), sticky="s")
        action_frame.columnconfigure(0, weight=1)
        action_frame.columnconfigure(1, weight=1)
        action_frame.grid_columnconfigure((0, 1, 2), weight=1)

        edit_btn = ctk.CTkButton(
            action_frame,
            text="",
            image=Assets.get_icon("edit", size=(18, 18)),
            command=lambda: on_edit(self.book_data),
            fg_color="transparent",
            hover_color=BG_COLOR,
            width=30
        )
        edit_btn.grid(row=0, column=1, padx=2, sticky="ew")

        delete_btn = ctk.CTkButton(
            action_frame,
            text="",
            image=Assets.get_icon("remove", size=(18, 18)),
            command=lambda: on_delete(self.book_data),
            fg_color="transparent",
            hover_color=BG_COLOR,
            width=30,
        )
        delete_btn.grid(row=0, column=2, padx=5, sticky="e")

        add_btn = ctk.CTkButton(
            action_frame,
            text="",
            image=Assets.get_icon("add_list", size=(18, 18)),
            command=lambda: on_add_to_list(self.book_data),
            fg_color="transparent",
            hover_color=BG_COLOR,
            width=30
        )
        add_btn.grid(row=0, column=0, padx=2, sticky="ew")

    def _get_category_colors(self, category_name):
        index = hash(category_name) % len(CAT_COLORS)
        return CAT_COLORS[index]

    def _load_cover_image(self):
        image = None
        cover_path = self.book_data.get('cover', 'default')

        if cover_path and cover_path != 'default' and os.path.exists(cover_path):
            try:
                image = Image.open(cover_path)
            except Exception:
                pass

        if image is None:
            image = Image.new('RGB', (COVER_WIDTH, COVER_HEIGHT), color='#5A189A')

        image = ImageOps.expand(image, border=5, fill='#5A189A')

        image = image.resize((COVER_WIDTH, COVER_HEIGHT), Image.Resampling.LANCZOS)

        self.ctk_image = ctk.CTkImage(
            light_image=image,
            dark_image=image,
            size=(COVER_WIDTH, COVER_HEIGHT)
        )


# =======================
# EDIT BOOK DIALOG#
# =======================
class EditBookDialog(AddBookDialog):
    def __init__(self, parent, on_save, book_data):
        self.book_data = book_data
        cat_dict = parent.get_all_categories_with_subcats()
        super().__init__(parent, cat_dict=cat_dict, on_save_callback=on_save)
        self.title("Kitabı Düzenle")
        self._fill_existing_data()
        self._update_ui_elements()

    def _fill_existing_data(self):
        self.title_entry.insert(0, self.book_data.get('title', ''))
        self.author_entry.insert(0, self.book_data.get('author', ''))
        self.isbn_entry.insert(0, self.book_data.get('isbn', ''))
        self.publisher_entry.insert(0, self.book_data.get('publisher', ''))
        self.category_combo.set(self.book_data.get('category', ''))
        self.subcategory_combo.set(self.book_data.get('subcategory', ''))

        year = self.book_data.get('year')
        if year: self.year_entry.insert(0, str(year))

        cover = self.book_data.get('cover', '')
        if cover and cover != 'default':
            self.cover_path_entry.delete(0, tk.END)
            self.cover_path_entry.insert(0, cover)

        self.reading_status_var.set(self.book_data.get('reading_status', 'unread'))
        is_owned = self.book_data.get('owned', True)
        self.stock_status_var.set('available' if is_owned else 'borrowed')

    def _update_ui_elements(self):
        for child in self.scroll_frame.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                for sub_child in child.winfo_children():
                    if isinstance(sub_child, ctk.CTkButton) and sub_child.cget("text") == "Ekle":
                        sub_child.configure(text="Güncelle")

    def _save_book(self):
        data = {
            "id": self.book_data.get('id'),
            "title": self.title_entry.get().strip(),
            "author": self.author_entry.get().strip(),
            "isbn": self.isbn_entry.get().strip(),
            "year": self.year_entry.get().strip(),
            "publisher": self.publisher_entry.get().strip(),
            "category": self.category_combo.get().strip(),
            "subcategory": self.subcategory_combo.get().strip(),
            "reading_status": self.reading_status_var.get(),
            "owned": (self.stock_status_var.get() == "available"),
            "cover": self.cover_path_entry.get().strip()
        }

        if not all([data['title'], data['author'], data['isbn'], data['publisher'], data['category']]):
            messagebox.showwarning("Hata", "Lütfen tüm zorunlu alanları doldurun.", parent=self)
            return

        self.on_save_callback(data)
        self.destroy()


# =======================
# ADD TO LIST DIALOG
# =======================
class AddToListDialog(ctk.CTkToplevel):
    def __init__(self, master, book_data, available_lists, on_save_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=BG_COLOR)
        self.title("Listeleri Yönet")
        self.geometry("350x450")
        self.transient(master)
        self.grab_set()
        self.resizable(False, False)

        self.update_idletasks()
        x = int((self.winfo_screenwidth() / 2) - (350 / 2))
        y = int((self.winfo_screenheight() / 2) - (450 / 2))
        self.geometry(f"+{x}+{y}")

        self.book_data = book_data
        self.on_save_callback = on_save_callback
        self.current_lists = book_data.get("lists", [])
        self.checkboxes = {}

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        title_lbl = ctk.CTkLabel(self, text=f"'{book_data.get('title')}'",
                                 font=ctk.CTkFont(size=14, weight="bold"),
                                 text_color=PRIMARY_COLOR, wraplength=300)
        title_lbl.grid(row=0, column=0, pady=(20, 10), padx=20)

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))

        for lst in available_lists:
            is_checked = lst in self.current_lists
            var = ctk.BooleanVar(value=is_checked)

            cb = ctk.CTkCheckBox(
                self.scroll_frame, text=lst, variable=var,
                fg_color=PRIMARY_COLOR, hover_color=ACCENT_COLOR,
                font=ctk.CTkFont(size=13), text_color=TEXT_COLOR
            )
            cb.pack(anchor="w", pady=8, padx=10)
            self.checkboxes[lst] = var

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        btn_frame.columnconfigure((0, 1), weight=1)

        cancel_btn = ctk.CTkButton(btn_frame, text="İptal", command=self.destroy,
                                   fg_color=LOCAL_CARD_BG, text_color=TEXT_COLOR, hover_color=ACCENT_COLOR)
        cancel_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        save_btn = ctk.CTkButton(btn_frame, text="Kaydet", command=self._save,
                                 fg_color=PRIMARY_COLOR, hover_color=ACCENT_COLOR)
        save_btn.grid(row=0, column=1, padx=(5, 0), sticky="ew")

    def _save(self):
        selected_lists = [name for name, var in self.checkboxes.items() if var.get()]
        self.on_save_callback(selected_lists)
        self.destroy()