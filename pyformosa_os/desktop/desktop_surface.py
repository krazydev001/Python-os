import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QWidget, QMenu, QToolButton, QFileDialog, QMessageBox

class DesktopSurfaceWidget(QWidget):
    def __init__(self, parent=None, os_parent=None):
        super().__init__(parent)
        self.os_parent = os_parent
        
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_desktop_context_menu)
        self.setup_desktop_icons()

    def setup_desktop_icons(self):
        self.recycle_bin = QToolButton(self)
        self.recycle_bin.setText("Recycle Bin")
        self.recycle_bin.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.recycle_bin.setFixedSize(80, 80)
        
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons", "recycle_bin.png")
        if os.path.exists(icon_path):
            self.recycle_bin.setIcon(QIcon(icon_path))
            self.recycle_bin.setIconSize(self.recycle_bin.size() * 0.6)
        else:
            self.recycle_bin.setText("🗑️\nRecycle Bin")
            
        self.recycle_bin.setStyleSheet("""
            QToolButton {
                color: white;
                background: transparent;
                border: none;
                font-family: 'Segoe UI';
                font-size: 11px;
            }
            QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.15);
                border-radius: 4px;
            }
        """)
        self.recycle_bin.move(20, 20)
        self.recycle_bin.clicked.connect(self.open_recycle_bin)

    def open_recycle_bin(self):
        QMessageBox.information(self, "Recycle Bin", "Recycle Bin is empty.")

    def show_desktop_context_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: rgba(32, 32, 32, 0.95);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 4px;
                color: white;
                font-family: 'Segoe UI';
            }
            QMenu::item { padding: 6px 24px; border-radius: 4px; }
            QMenu::item:selected { background-color: rgba(255, 255, 255, 0.1); }
            QMenu::separator { height: 1px; background: rgba(255, 255, 255, 0.1); margin: 4px 0px; }
        """)

        refresh_action = QAction("🔄 Refresh", self)
        refresh_action.triggered.connect(self.handle_refresh)
        menu.addAction(refresh_action)
        menu.addSeparator()

        new_menu = QMenu("➕ New", menu)
        new_menu.setStyleSheet(menu.styleSheet())
        new_folder = QAction("Folder", self)
        new_text = QAction("Text Document", self)
        new_menu.addAction(new_folder)
        new_menu.addAction(new_text)
        menu.addMenu(new_menu)

        menu.addSeparator()
        change_bg_action = QAction("🖼️ Change Background", self)
        change_bg_action.triggered.connect(self.handle_change_background)
        menu.addAction(change_bg_action)

        menu.exec(self.mapToGlobal(pos))

    def handle_refresh(self):
        if self.os_parent and hasattr(self.os_parent, 'update_wallpaper'):
            self.os_parent.update_wallpaper()

    def handle_change_background(self):
        if not self.os_parent: return
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Wallpaper Image", "", "Images (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.os_parent.current_wallpaper = file_path
            self.os_parent.update_wallpaper()