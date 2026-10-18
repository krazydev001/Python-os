from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from desktop.window_frame import DraggableWindowFrame

class WebBrowserApp(DraggableWindowFrame):
    def __init__(self, parent=None):
        super().__init__("Web Browser", parent)

        self.content_area = QWidget(self)
        self.layout.addWidget(self.content_area, stretch=1)

        browser_layout = QVBoxLayout(self.content_area)
        browser_layout.setContentsMargins(0, 0, 0, 0)
        browser_layout.setSpacing(0)

        nav_bar = QWidget(self.content_area)
        nav_bar.setFixedHeight(40)
        nav_bar.setStyleSheet("background-color: #202020; border-bottom: 1px solid #2d2d2d;")
        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(10, 0, 10, 0)

        self.url_bar = QLineEdit(nav_bar)
        self.url_bar.setStyleSheet("background-color: #2b2b2b; color: white; border: 1px solid #3a3a3a; border-radius: 4px; padding: 4px 8px;")
        self.url_bar.setText("https://google.com")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_layout.addWidget(self.url_bar)

        go_btn = QPushButton("Go", nav_bar)
        go_btn.setFixedSize(50, 26)
        go_btn.setStyleSheet("background-color: #005fb8; color: white; border: none; border-radius: 4px;")
        go_btn.clicked.connect(self.navigate_to_url)
        nav_layout.addWidget(go_btn)

        browser_layout.addWidget(nav_bar)

        self.web_engine = QWebEngineView(self.content_area)
        self.web_engine.load(QUrl("https://google.com"))
        browser_layout.addWidget(self.web_engine, stretch=1)

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "https://" + url
        self.web_engine.load(QUrl(url))