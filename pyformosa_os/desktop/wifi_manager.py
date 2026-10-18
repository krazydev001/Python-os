from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLabel
from PyQt6.QtCore import Qt

class WifiManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(230)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        
        self.title = QLabel("Available Networks")
        self.title.setStyleSheet("color: white; font-weight: bold; font-family: 'Segoe UI'; font-size: 12px;")
        self.layout.addWidget(self.title)

        self.network_list = QListWidget()
        self.network_list.setStyleSheet("""
            QListWidget { 
                background: rgba(45, 45, 45, 0.8); 
                color: white; 
                border: 1px solid rgba(255,255,255,0.1); 
                border-radius: 6px; 
            }
            QListWidget::item { padding: 6px; }
            QListWidget::item:selected { background: #005fb8; border-radius: 4px; }
        """)
        self.layout.addWidget(self.network_list)

        self.refresh_btn = QPushButton("Scan Networks")
        self.refresh_btn.setStyleSheet("""
            QPushButton { background: #3c3c3c; color: white; border: none; padding: 6px; border-radius: 4px; }
            QPushButton:hover { background: #505050; }
        """)
        self.refresh_btn.clicked.connect(self.scan_networks)
        self.layout.addWidget(self.refresh_btn)

        self.scan_networks()

    def scan_networks(self):
        self.network_list.clear()
        found_networks = ["Home_WiFi_5G", "CoffeeShop_Free", "Office_Net", "Hidden_Network"]
        for net in found_networks:
            item = QListWidgetItem(f"📶 {net}")
            self.network_list.addItem(item)