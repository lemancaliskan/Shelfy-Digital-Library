from PySide6.QtWidgets import QVBoxLayout, QWidget
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtGui import QIcon


class BookReader(QWidget):
    def __init__(self, book_path):
        super().__init__()

        # Objects
        self.setWindowTitle('Book reader')
        self.setWindowIcon(QIcon('assets/icon/book_reader_icon.png'))
        self.setMinimumSize(1100, 700)

        self.book = QPdfDocument(self)

        self.book_view = QPdfView(self)
        self.book_view.setDocument(self.book)

        self.book_view.setPageMode(QPdfView.PageMode.MultiPage)

        # Desining
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.book_view)

        self.load_book(book_path)

        self.setLayout(self.main_layout)

    def load_book(self, path):
        self.book.load(path)