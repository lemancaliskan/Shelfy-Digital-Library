import json
import os
import uuid
import shutil
import sys

def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

class JSONManager:
    def __init__(self):
        self.base_dir = get_base_path()
        self.data_folder = os.path.join(self.base_dir, 'data')
        self.db_path = os.path.join(self.data_folder, 'library.json')
        self.covers_folder = os.path.join(self.data_folder, 'covers')

        os.makedirs(self.covers_folder, exist_ok=True)

        if not os.path.exists(self.db_path):
            self._save_data({"books": [], "custom_lists": []})

    def _load_data(self):
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"books": [], "custom_lists": []}

    def _save_data(self, data):
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def get_filtered_books(self, search_query=None, category=None, subcategory=None, language=None, status=None,
                           stock=None, list_type=None, sort_by="sort_newest"):
        data = self._load_data()
        books = data.get("books", [])

        filtered = []
        from translations import get_text

        for book in books:
            match = True

            if search_query:
                q = search_query.lower()
                if q not in book.get('title', '').lower() and q not in book.get('author', '').lower():
                    match = False

            if category and category != get_text("all"):
                if book.get('category') != category:
                    match = False

            if subcategory and subcategory != get_text("all"):
                if book.get('subcategory') != subcategory:
                    match = False

            if language and language != get_text("all"):
                if book.get('language') != language:
                    match = False

            if status and status != "all":
                if book.get('reading_status') != status:
                    match = False

            if stock and stock != "all":
                if book.get('stock_status') != stock:
                    match = False

            if list_type and list_type != "all_list":
                if list_type == "favorites":
                    if not book.get('is_favorite', False):
                        match = False
                else:
                    if list_type not in book.get('lists', []):
                        match = False

            if match:
                filtered.append(book)

        if sort_by == "sort_az":
            filtered.sort(key=lambda x: x.get("title", "").lower())
        elif sort_by == "sort_za":
            filtered.sort(key=lambda x: x.get("title", "").lower(), reverse=True)
        elif sort_by == "sort_oldest":
            pass
        else:
            filtered.reverse()

        return filtered

    def add_book(self, title, author, isbn, year, publisher, category, subcategory, language, owned, reading_status,
                 cover_path=None):
        data = self._load_data()
        book_id = str(uuid.uuid4())
        final_cover_path = "default"

        if cover_path and cover_path != "default":
            if cover_path.startswith(("http://", "https://")):
                final_cover_path = self._download_cover(cover_path, book_id)
            elif os.path.exists(cover_path):
                ext = os.path.splitext(cover_path)[1]
                dest_path = os.path.join(self.covers_folder, f"{book_id}{ext}")
                shutil.copy(cover_path, dest_path)
                final_cover_path = os.path.relpath(dest_path, self.base_dir)

        new_book = {
            "id": book_id,
            "title": title,
            "author": author,
            "isbn": isbn,
            "year": year,
            "publisher": publisher,
            "category": category,
            "subcategory": subcategory,
            "language": language,
            "owned": owned,
            "reading_status": reading_status,
            "cover": final_cover_path,
            "lists": []
        }

        data["books"].append(new_book)
        self._save_data(data)
        return True

    def delete_book(self, book_id):
        data = self._load_data()
        book_to_delete = next((b for b in data["books"] if b['id'] == book_id), None)

        if book_to_delete:
            if book_to_delete['cover'] != 'default':
                full_img_path = os.path.join(self.base_dir, book_to_delete['cover'])
                if os.path.exists(full_img_path):
                    try:
                        os.remove(full_img_path)
                    except:
                        pass

            data["books"] = [b for b in data["books"] if b['id'] != book_id]
            self._save_data(data)
            return True
        return False

    def update_book(self, book_id, updated_data):
        data = self._load_data()
        for i, book in enumerate(data['books']):
            if book['id'] == book_id:
                if 'cover' in updated_data:
                    new_cover = updated_data.get('cover')

                    if new_cover and new_cover != "default":
                        old_cover_rel = book.get('cover', '')
                        is_same_file = False

                        if old_cover_rel and old_cover_rel != "default":
                            old_cover_abs = os.path.abspath(os.path.join(self.base_dir, old_cover_rel))
                            new_cover_abs = os.path.abspath(new_cover) if os.path.exists(new_cover) else new_cover
                            if old_cover_abs == new_cover_abs:
                                is_same_file = True

                        if not is_same_file:
                            if new_cover.startswith(("http://", "https://")):
                                updated_data['cover'] = self._download_cover(new_cover, book_id)
                            elif os.path.exists(new_cover):
                                ext = os.path.splitext(new_cover)[1]
                                dest_path = os.path.join(self.covers_folder, f"{book_id}{ext}")
                                try:
                                    shutil.copy(new_cover, dest_path)
                                    updated_data['cover'] = os.path.relpath(dest_path, self.base_dir)
                                except Exception as e:
                                    print(f"Kapak kopyalama hatası: {e}")
                                    updated_data['cover'] = book.get('cover')
                            else:
                                updated_data['cover'] = book.get('cover')
                        else:
                            updated_data['cover'] = book.get('cover')
                    else:
                        updated_data['cover'] = "default" if not new_cover else new_cover

                data['books'][i].update(updated_data)
                self._save_data(data)
                return True
        return False

    def get_all_categories(self):
        data = self._load_data()
        categories = set()

        for book in data.get("books", []):
            cat = book.get('category', '').strip()
            if cat:
                parts = cat.split(">")
                current_path = ""

                for part in parts:
                    part = part.strip()
                    if current_path == "":
                        current_path = part
                    else:
                        current_path = f"{current_path} > {part}"

                    categories.add(current_path)

        return sorted(list(categories))

    def get_custom_lists(self):
        data = self._load_data()
        return data.get("custom_lists", [])

    def add_custom_list(self, list_name):
        data = self._load_data()
        if "custom_lists" not in data:
            data["custom_lists"] = []
        if list_name not in data["custom_lists"]:
            data["custom_lists"].append(list_name)
            self._save_data(data)

    def delete_custom_list(self, list_name):
        data = self._load_data()

        if "custom_lists" in data and list_name in data["custom_lists"]:
            data["custom_lists"].remove(list_name)

        for book in data.get("books", []):
            if "lists" in book and list_name in book["lists"]:
                book["lists"].remove(list_name)

        self._save_data(data)

    def _download_cover(self, url, book_id):
        import requests
        try:
            response = requests.get(url, timeout=10, stream=True)
            if response.status_code == 200:
                ext = ".jpg"
                if "image/png" in response.headers.get('Content-Type', ''):
                    ext = ".png"

                dest_path = os.path.join(self.covers_folder, f"{book_id}{ext}")
                with open(dest_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)

                return os.path.relpath(dest_path, self.base_dir)
        except Exception as e:
            print(f"Resim indirme hatası: {e}")
        return "default"

    def get_all_books(self):
        data = self._load_data()
        return data.get("books", [])