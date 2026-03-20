import customtkinter as ctk
from PIL import Image
import os

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

# COLOR CONSTANTS #
PRIMARY_COLOR = ("#7b2cbf", "#9d4edd")      # Royal Violet / Lavender Purple
ACCENT_COLOR = ("#5a189a", "#c77dff")       # Indigo Velvet / Mauve Magic
BG_COLOR = ("#FFFFFF", "#10002b")           # White / Dark Amethyst(<darkest)
CARD_BG = ("#FFFFFF", "#3c096c")            # White / Indigo Ink
TEXT_COLOR = ("#10002b", "#FFFFFF")         # Dark Amethyst / White
LIGHT_TEXT_COLOR = ("#5a189a", "#e0aaff")   # Indigo Velvet / Mauve
BUTTON_TEXT_COLOR = ("#FFFFFF", "#FFFFFF")  # White / White
SIDEBAR_BG = ("#e0aaff", "#240046")         # Mauve / Dark Amethyst

LOCAL_CARD_BG = ("#F3E8FF", "#3C096C")
LOCAL_SIDEBAR_BG = ("#FFFFFF", "#10002B")

CAT_COLORS = [
    (("#E0E7FF", "#1E1B4B"), ("#4338CA", "#A5B4FC")),  #Indigo
    (("#F3E8FF", "#3B0764"), ("#7E22CE", "#D8B4FE")),  #Purple
    (("#E0F2FE", "#0C4A6E"), ("#0369A1", "#7DD3FC")),  #Sky
    (("#DBEAFE", "#172554"), ("#1D4ED8", "#93C5FD")),  #Blue
    (("#ECFEFF", "#083344"), ("#0E7490", "#67E8F9")),  #Cyan
    (("#F1F5F9", "#0F172A"), ("#475569", "#94A3B8")),  #Slate
    (("#EDE9FE", "#2E1065"), ("#6D28D9", "#C4B5FD")),  #Violet
    (("#F0FDFA", "#042F2E"), ("#0F766E", "#5EEAD4")),  #Teal
    (("#FAFAF9", "#1C1917"), ("#57534E", "#A8A29E")),  #Stone
    (("#EFF6FF", "#1E3A8A"), ("#2563EB", "#60A5FA")),  #Royal Blue
    (("#F5F5F4", "#292524"), ("#44403C", "#D6D3D1")),  #Warm Grey
    (("#EBE9FE", "#1E1B4B"), ("#5945E4", "#A294FB")),  #Deep Purple
    (("#E0F7FA", "#003E4A"), ("#00838F", "#80DEEA")),  #Aqua
    (("#F8FAFC", "#020617"), ("#334155", "#CBD5E1")),  #Ice Blue
    (("#EEF2FF", "#312E81"), ("#4338CA", "#818CF8")),  #Navy Soft
    (("#FAF5FF", "#3B0764"), ("#8B5CF6", "#C4B5FD")),  #Lavender
    (("#F0F9FF", "#082F49"), ("#0284C7", "#7DD3FC")),  #Ocean
    (("#F1F1F1", "#18181B"), ("#52525B", "#D4D4D8")),  #Neutral
    (("#E0FCFF", "#004040"), ("#008080", "#80FFFF")),  #Dark Teal
    (("#E8E8E8", "#262626"), ("#404040", "#A3A3A3")),  #Metallic
]

# DIMENSION CONSTANTS #
SIDEBAR_WIDTH = 350
CARD_WIDTH = 140
CARD_HEIGHT = 400
COVER_WIDTH = 120
COVER_HEIGHT = 167

# DIALOG CONSTANTS #
DIALOG_WIDTH = 400
DIALOG_HEIGHT = 640
DIALOG_PADX = 15
ADD_LIST_DIALOG_HEIGHT = 175

# WIDGET CONSTANTS #
FIXED_BUTTON_WIDTH = 95
BUTTON_HEIGHT = 30
SEARCH_BOX_WIDTH = 310


class Assets:
    _icons = {}
    _initialized = False

    @classmethod
    def _ensure_initialized(cls):
        if not cls._initialized:
            base_path = os.path.dirname(os.path.abspath(__file__))
            icon_dir = os.path.join(base_path, "assets", "icon")
            logo_path = os.path.join(base_path, "assets", "logo.png")

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
            }

            for name, filename in icon_files.items():
                path = os.path.join(icon_dir, filename)
                if os.path.exists(path):
                    img = Image.open(path)
                    cls._icons[name] = ctk.CTkImage(
                        light_image=img,
                        dark_image=img,
                        size=(24, 24)
                    )
                else:
                    cls._icons[name] = None

            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                cls._icons["logo"] = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(200, 87))
            else:
                print(f"UYARI: Logo bulunamadı! Yol: {logo_path}")
                cls._icons["logo"] = None

            cls._initialized = True

    @classmethod
    def get_icon(cls, name, size=(24, 24)):
        cls._ensure_initialized()

        icon = cls._icons.get(name)
        if icon:
            try:
                icon.configure(size=size)
            except:
                pass
            return icon
        return None

    @classmethod
    def get_logo(cls):
        return cls.get_icon("logo", size=(150, 65))