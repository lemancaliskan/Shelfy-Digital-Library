from PySide6.QtWidgets import QVBoxLayout, QWidget
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtGui import QIcon
from PySide6.QtCore import QPointF


class BookReader(QWidget):
    def __init__(self, book_path, book_data):
        super().__init__()

        self.current_page = int(book_data.get('current_page'))

        # Objects
        self.setWindowTitle('Book reader')
        self.setWindowIcon(QIcon('assets/icon/book_reader_icon.png'))
        self.setMinimumSize(1100, 700)

        self.book = QPdfDocument(self)

        self.book_view = QPdfView(self)
        self.book_view.setDocument(self.book)

        self.book_view.setPageMode(QPdfView.PageMode.MultiPage)
        self.book_view.setZoomMode(QPdfView.ZoomMode.Custom)
        self.book_view.setZoomFactor(1.5)

        # Desining
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.book_view)

        self.load_book(book_path)
        if self.current_page == 0:
            self.book_view.pageNavigator().jump(0, QPointF(0, 0), self.book_view.zoomFactor())

        self.book_view.pageNavigator().jump(self.current_page - 1, QPointF(0, 0), self.book_view.zoomFactor())

        self.setLayout(self.main_layout)

    def load_book(self, path):
        self.book.load(path)
