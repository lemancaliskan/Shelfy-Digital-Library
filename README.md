# 📚 Shelfy - Modern Digital Library Management

*Shelfy is a comprehensive and user-friendly library management ecosystem designed for book enthusiasts. It allows you to organize your personal collection, track reading progress, and manage custom lists across multiple modern Python frameworks.*

---
🚀 Featured Version: PySide6 Edition
---
*The latest evolution of Shelfy, built with PySide6 (Qt for Python). This version focuses on high performance, advanced UI/UX, and professional desktop standards.*

---
📺 Screenshots
---

---
✨ Key Features (PySide6)
---
- **Advanced UI Engine:** Powered by Qt, offering smoother animations and a more robust desktop experience.

- **Dynamic Theme Engine:** Full support for system-aware Dark and Light modes with custom styled widgets.

- **Rich Interaction:** Enhanced drag-and-drop feel, custom combo boxes with search, and refined dialog windows.

- **Global Localization:** Integrated i18n system for instant switching between English and Turkish.

- **Smart Filtering & Search:** Real-time results by Category, Subcategory, ISBN, or Author.

- **Asset Intelligence:** Automated favicon generation and dynamic icon scaling.

- **JSON-Based Data Management:** Portable and fast data storage structure that requires no database installation.

---
🧬 Technical Architecture
---
*The project follows a modular, scalable architecture shared (logic-wise) across versions:*

- **UI Layer:** Framework-specific implementations (``shelfy_pyside`` or ``shelfy_ctk``).

- **Core Logic (``data_manager.py``):** Handles JSON-based portable storage and automated cover image downloads via API.

- **Assets Engine (``assets_manager.py``):** Centralized palette management and dynamic asset loading.

---
🛠️ Installation and Usage
---
- ***For Developers:***
<br>If you want to run the project locally or contribute:

```bash
# Clone the repository
git clone https://github.com/lemancaliskan/Shelfy-Digital-Library.git

# Go to the project directory
cd Shelfy-Digital-Library

# Install required libraries
pip install -r requirements.txt

# Run the application (Preferred Version)
To run the latest PySide6 version (Recommended):
python shelfy_pyside/main.py

# Run the application (CustomTkinter Version)
To run the CustomTkinter version:
python shelfy_ctk/main_ctk.py
```

---
🕰️ Legacy Version: CustomTkinter
---
*For those who prefer a lightweight CustomTkinter experience, the original version of Shelfy is still maintained in the shelfy_ctk/ directory. It offers the same core library management features with a different visual aesthetic.
<br>Legacy version offers a sleek, eye-pleasing experience in both light and dark modes, utilizing the modern power of ``CustomTkinter``:*
<br>

<img width="770" alt="image" src="https://github.com/user-attachments/assets/f405d231-1211-4bea-ac7e-57872a519e23" />
<img width="770" alt="image" src="https://github.com/user-attachments/assets/2b643011-e60c-454c-b0ff-38171670985f" />

---
📁 Project Structure
---
```bash
Shelfy/
├── 📁 shelfy_py6/          # Featured: Main PySide6 implementation
│   ├── 📁 assets/                # Application icons, logo
│   ├── 📁 data/                  # Local data storage
│   ├── 📁 covers/                # Book cover images (protected by .gitkeep)
│   └── 📄 library.json           # Main file holding book and list data
│   ├── 📄 main.py                # Application entry point and main loop
│   ├── 📄 data_manager.py        # Data processing and JSON management layer
│   ├── 📄 ui_components.py       # Interface elements and custom widgets
│   ├── 📄 assets_manager.py      # Theme, color, and asset management
│   ├── 📜 requirements.txt       # Required libraries
├── 📁 shelfy_ctk/          # Alternative: CustomTkinter implementation
│   ├── 📁 assets/                # Application icons, logo
│   ├── 📁 data/                  # Local data storage
│   ├── 📁 covers/                # Book cover images (protected by .gitkeep)
│   └── 📄 library.json           # Main file holding book and list data
│   ├── 📄 main.py                # Application entry point and main loop
│   ├── 📄 data_manager.py        # Data processing and JSON management layer
│   ├── 📄 ui_components.py       # Interface elements and custom widgets
│   ├── 📄 assets_manager.py      # Theme, color, and asset management
│   ├── 📜 requirements.txt       # Required libraries
├── 📄 README.md             # Project documentation
├── 📄 LICENSE               # MIT License file
└── ⚙️ .gitignore            # Files untracked by Git
```

---
🤝 Contributing
---
Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated!

```bash
# Fork the Project

# Create your Feature Branch 
(git checkout -b feature/AmazingFeature)

# Commit your Changes 
(git commit -m 'Add some AmazingFeature')

# Push to the Branch 
(git push origin feature/AmazingFeature)

# Open a Pull Request
```

---
⚖️ License
---
This project is licensed under the MIT License. See the ``LICENSE`` file for more details.
