# 📚 Shelfy - Modern Dijital Kütüphane Yönetimi

*Shelfy, kitap tutkunları için tasarlanmış, modern ve kullanıcı dostu bir kütüphane yönetim arayüzüdür. Kişisel kitap koleksiyonunuzu kategorize etmenize, okuma durumunuzu takip etmenize ve özel listeler oluşturmanıza olanak tanır.*
---
📺 Demo
---
*Shelfy, ``CustomTkinter``'ın modern gücünü kullanarak hem açık hem de koyu modda göz yormayan, zarif bir deneyim sunar:*
<br>

---
✨ Özellikler
---

- **Modern Kart Tasarımı:** Kitaplar, kapak resimleri ve temel bilgileriyle şık kartlar halinde sergilenir.

- **Dinamik Filtreleme:** Kategori, alt kategori, stok durumu veya okuma durumuna (Okundu, Okunuyor, Okunacak) göre anlık filtreleme.

- **Özel Listeler (Custom Lists):** "E-kitaplarım" gibi tamamen size özel listeler oluşturma ve kitapları bu listelere atama.

- **Gelişmiş Arama:** Kitap adı, isbn veya yazar ismine göre anlık arama sonuçları.

- **JSON Tabanlı Veri Yönetimi:** Veritabanı kurulumu gerektirmeyen, taşınabilir ve hızlı veri saklama yapısı.

- **Koyu/Açık Tema:** Manuel değiştirilebilir modern arayüz.

---
🧬 Teknik Mimari
---
*Uygulama, sürdürülebilir ve modüler bir yapıda üç temel katmandan oluşur:*

- **UI Components:** ui_components.py içerisinde tanımlanan, CustomTkinter tabanlı özelleştirilmiş kartlar, diyalog pencereleri ve kenar çubuğu elemanları.

- **Data Manager:** data_manager.py üzerinden yönetilen, JSON işlemlerini ve resim indirme (cover download) işlemlerini yürüten motor.

- **Assets Manager:** Renk paletleri, ikon yönetimi ve favicon üretimini dinamik olarak yöneten merkezi sistem.

---
🛠️ Kurulum ve Kullanım
---
 
- ***Standalone Executable (Önerilen)***
<br>Python kurmanıza gerek kalmadan uygulamayı doğrudan çalıştırın:

    -  **[Releases Page](https://github.com/lemancaliskan/Shelfy-Dijital-Kutuphane-Yonetimi/releases/tag/v1.0)** sayfasına gidin.
    - En son sürümdeki ``Shelfy.exe`` dosyasını indirin.
    - Çift tıklayarak kütüphanenizi yönetmeye başlayın.
    
- ***Geliştiriciler İçin:***
<br>Projeyi yerelinizde çalıştırmak veya katkıda bulunmak isterseniz:

```bash
# Depoyu klonlayın
git clone https://github.com/kullaniciadi/Shelfy.git

# Proje dizinine gidin
cd Shelfy

# Gerekli kütüphaneleri yükleyin
pip install -r requirements.txt

# Uygulamayı başlatın
python main.py
```

---
📁 Proje Yapısı
---

```bash
Shelfy/
├── 📁 assets/                # Uygulama ikonları, logo
├── 📁 data/                  # Yerel veri depolama
│   ├── 📁 covers/            # Kitap kapak resimleri (.gitkeep ile korunur)
│   └── 📄 library.json       # Kitap ve liste verilerinin tutulduğu ana dosya
├── 📄 main.py                # Uygulamanın giriş noktası ve ana döngüsü
├── 📄 data_manager.py        # Veri işleme ve JSON yönetim katmanı
├── 📄 ui_components.py       # Arayüz elemanları ve özel widget'lar
├── 📄 assets_manager.py      # Tema, renk ve varlık yönetimi
├── 📜 requirements.txt       # Gerekli kütüphaneler
└── ⚙️ .gitignore             # Git tarafından izlenmeyecek dosyalar
```

---
🤝 Katkıda Bulunma
---
Projeyi geliştirmek için her türlü katkıya açığım!

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
⚖️ Lisans
---
Bu proje MIT Lisansı ile lisanslanmıştır. Detaylar için LICENSE dosyasına bakabilirsiniz.
