# 📚 Shelfy - Modern Digital Library Management

*Shelfy is a modern and user-friendly library management interface designed for book enthusiasts. It allows you to categorize your personal book collection, track your reading status, and create custom lists.*
---
📺 Demo
---
*Shelfy offers a sleek, eye-pleasing experience in both light and dark modes, utilizing the modern power of ``CustomTkinter``:*
<br>

---
✨ Features
---

- **Dynamic Language Support (i18n):** Newly added translation system allows you to easily switch between English and Turkish interfaces.

- **Modern Card Design:** Books are displayed as stylish cards with their cover images and essential information.

- **Dynamic Filtering:** Instant filtering by category, subcategory, stock status, or reading status (Read, Reading, To Read).

- **Custom Lists:** Create completely personalized lists like "My E-books" and assign books to these lists.

- **Advanced Search:** Real-time search results by book title, ISBN, or author name.

- **JSON-Based Data Management:** Portable and fast data storage structure that requires no database installation.

- **Dark/Light Theme:** Manually toggleable modern interface.

---
🧬 Technical Architecture
---
*The application consists of three main layers in a sustainable and modular structure:*

- **UI Components:** CustomTkinter-based customized cards, dialog windows, and sidebar elements defined in ``ui_components.py``.

- **Data Manager:** The engine managed via ``data_manager.py`` that handles JSON operations and cover image downloads.

- **Assets Manager:** A centralized system that dynamically manages color palettes, icons, and favicon generation.

---
🛠️ Installation and Usage
---
- ***Standalone Executable (Recommended)***
<br>Run the application directly without needing to install Python:


     - Go to the **[Releases Page](https://github.com/lemancaliskan/Shelfy-Dijital-Kutuphane-Yonetimi/releases/tag/v1.0)**
     - Download the ``Shelfy.exe`` file from the latest release.
     - Double-click to start managing your library.
       
    
- ***For Developers:***
<br>If you want to run the project locally or contribute:

```bash
# Clone the repository
git clone https://github.com/lemancaliskan/Shelfy-Dijital-Kutuphane-Yonetimi.git

# Go to the project directory
cd Shelfy-Dijital-Kutuphane-Yonetimi

# Install required libraries
pip install -r requirements.txt

# Run the application
python main.py
```

---
📁 Project Structure
---

```bash
Shelfy/
├── 📁 assets/                # Application icons, logo
├── 📁 data/                  # Local data storage
│   ├── 📁 covers/            # Book cover images (protected by .gitkeep)
│   └── 📄 library.json       # Main file holding book and list data
├── 📄 main.py                # Application entry point and main loop
├── 📄 data_manager.py        # Data processing and JSON management layer
├── 📄 ui_components.py       # Interface elements and custom widgets
├── 📄 assets_manager.py      # Theme, color, and asset management
├── 📜 requirements.txt       # Required libraries
└── ⚙️ .gitignore             # Files untracked by Git
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
