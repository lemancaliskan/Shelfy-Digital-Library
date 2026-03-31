import os
from PIL import Image
from PySide6.QtGui import QIcon, QPixmap

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
png_path = os.path.join(ASSETS_DIR, "icon.png")
ico_path = os.path.join(ASSETS_DIR, "favicon.ico")

def initialize_assets():
    if os.path.exists(ico_path):
        return

    try:
        if not os.path.exists(ASSETS_DIR):
            os.makedirs(ASSETS_DIR)

        if os.path.exists(png_path):
            img = Image.open(png_path)
            icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            img.save(ico_path, sizes=icon_sizes)
            print("Icon generated successfully.")
    except Exception as e:
        print(f"An error occurred while creating the icon: {e}")

PRIMARY_COLOR = "#613DC1"
ACCENT_COLOR = "#4E148C"
HOVER_COLOR = "#858AE3"
BORDER_COLOR = "#97DFFC"

BG_COLOR_LIGHT = "#FFFFFF"
CARD_BG_LIGHT = "#FFFFFF"
TEXT_COLOR_LIGHT = "#030213"

BG_COLOR_DARK = "#10002B"
CARD_BG_DARK = "#1E1E1E"
TEXT_COLOR_DARK = "#FFFFFF"

CAT_COLORS = [
    ("#E0E7FF", "#4338CA"),
    ("#F3E8FF", "#7E22CE"),
    ("#E0F2FE", "#0369A1"),
    ("#DBEAFE", "#1D4ED8"),
    ("#ECFEFF", "#0E7490"),
]

SIDEBAR_WIDTH = 320
CARD_WIDTH = 220
CARD_HEIGHT = 380
COVER_WIDTH = 140
COVER_HEIGHT = 200

DIALOG_WIDTH = 450
DIALOG_HEIGHT = 650

class Assets:
    _icons = {}
    _initialized = False

    @classmethod
    def _ensure_initialized(cls):
        if not cls._initialized:
            base_path = os.path.dirname(os.path.abspath(__file__))
            icon_dir = os.path.join(base_path, "assets", "icon")

            icon_files = {
                "book": "book.png",
                "add_book": "add_book.png",
                "list_add": "list_add.png",
                "list_del": "list_delete.png",
                "search": "search.png",
                "add_list": "add_list.png",
                "edit": "edit.png",
                "remove": "remove.png",
                "light_m" : "light_mode.png",
                "dark_m" : "dark_mode.png",
                "language": "language.png",
                "arrow": "arrow.png"
            }

            for name, filename in icon_files.items():
                path = os.path.join(icon_dir, filename)
                if os.path.exists(path):
                    cls._icons[name] = QIcon(path)
                else:
                    cls._icons[name] = QIcon()

            logo_path = os.path.join(base_path, "assets", "logo.png")
            if os.path.exists(logo_path):
                cls._icons["logo"] = QPixmap(logo_path)
            else:
                cls._icons["logo"] = QPixmap()

            cls._initialized = True

    @classmethod
    def get_icon(cls, name):
        cls._ensure_initialized()
        return cls._icons.get(name, QIcon())

    @classmethod
    def get_logo(cls):
        cls._ensure_initialized()
        return cls._icons.get("logo", QPixmap())