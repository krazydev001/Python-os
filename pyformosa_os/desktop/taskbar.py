import os
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLineEdit
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSize

class TaskbarWidget(QWidget):
    """Windows 11 inspired hotbar containing active app shortcuts."""
    def __init__(self, parent=None, on_start_click=None, on_browser_click=None, on_explorer_click=None, on_tray_click=None):
        super().__init__(parent)
        self.setFixedHeight(48)
        self.setStyleSheet("background-color: rgba(243, 243, 243, 0.85); border-top: 1px solid rgba(0,0,0,0.05);")
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 0, 15, 0)
        
        main_layout.addStretch(1)

        center_widget = QWidget(self)
        center_layout = QHBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(8)

        # Start Pill
        self.start_btn = QPushButton("🔹", self)
        self.start_btn.setFixedSize(36, 36)
        self.start_btn.clicked.connect(on_start_click)
        center_layout.addWidget(self.start_btn)

        # Pill Search Field
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("🔍 Search")
        self.search_bar.setFixedWidth(180)
        self.search_bar.setFixedHeight(32)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 16px;
                padding-left: 12px;
                font-family: 'Segoe UI';
                font-size: 12px;
                color: #333333;
            }
            QLineEdit:focus { border: 1px solid #005fb8; }
        """)
        center_layout.addWidget(self.search_bar)

        # Web Browser Shortcut
        self.browser_btn = QPushButton("🌐", self)
        self.browser_btn.setFixedSize(36, 36)
        self.browser_btn.clicked.connect(on_browser_click)
        center_layout.addWidget(self.browser_btn)

        # File Explorer Shortcut
        self.explorer_btn = QPushButton(self)
        self.explorer_btn.setFixedSize(36, 36)
        
        # Load your custom file explorer image directly onto the launch pad hook
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons")
        icon_set = False
        for ext in [".png", ".svg", ".ico", ".jpg"]:
            path = os.path.join(assets_dir, f"file_explorer{ext}")
            if os.path.exists(path):
                self.explorer_btn.setIcon(QIcon(path))
                self.explorer_btn.setIconSize(QSize(24, 24))
                icon_set = True
                break
        if not icon_set:
            self.explorer_btn.setText("📁")

        self.explorer_btn.clicked.connect(on_explorer_click)
        center_layout.addWidget(self.explorer_btn)

        main_layout.addWidget(center_widget)
        main_layout.addStretch(1)
        
        # Tray Area
        self.tray_btn = QPushButton("⚙️ 35°C", self)
        self.tray_btn.setFixedSize(90, 36)
        self.tray_btn.clicked.connect(on_tray_click)
        main_layout.addWidget(self.tray_btn)