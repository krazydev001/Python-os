import os
import sys
import shutil
from PyQt6.QtCore import Qt, QSize, QFileInfo
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem,
    QListView, QFileIconProvider, QLabel, QPushButton, QFrame, QLineEdit, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView, QInputDialog, QMessageBox, QStackedWidget
)
from qfluentwidgets import FluentIcon as FIF

from desktop.window_frame import DraggableWindowFrame


class FileManagerApp(DraggableWindowFrame):
    def __init__(self, parent=None):
        super().__init__("File Explorer", parent)
        self.resize(1000, 700)

        # Paths & Navigation Tracking
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(self.current_dir)
        self.assets_dir = os.path.join(self.project_root, "assets", "icons")

        self.icon_provider = QFileIconProvider()
        self.home_path = os.path.expanduser("~")
        self.current_path = "Home"
        self.history = []

        self.set_window_custom_icon()

        # Main UI Container
        self.main_container = QWidget()
        self.main_container.setStyleSheet("QWidget { background-color: #FFFFFF; font-family: 'Segoe UI', sans-serif; }")
        self.layout.addWidget(self.main_container, stretch=1)

        self.root_layout = QVBoxLayout(self.main_container)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        # Build UI Components
        self.setup_tab_bar()
        self.setup_command_bar()
        self.setup_address_bar()

        content_split = QHBoxLayout()
        content_split.setContentsMargins(0, 0, 0, 0)
        content_split.setSpacing(0)
        self.root_layout.addLayout(content_split, stretch=1)

        self.setup_sidebar(content_split)
        self.setup_main_content(content_split)
        self.setup_status_bar()

        # Load Home View initially
        self.show_home_view()

    # --- ICON HELPER ---
    def get_custom_icon(self, icon_name: str, fallback_fluent_icon=None) -> QIcon:
        for ext in [".png", ".svg", ".ico", ".jpg"]:
            icon_path = os.path.join(self.assets_dir, f"{icon_name}{ext}")
            if os.path.exists(icon_path):
                return QIcon(icon_path)
        if fallback_fluent_icon:
            return fallback_fluent_icon.qicon()
        return QIcon()

    def set_window_custom_icon(self):
        icon = self.get_custom_icon("file_explorer")
        if not icon.isNull():
            self.setWindowIcon(icon)

    # --- 1. TAB BAR ---
    def setup_tab_bar(self):
        tab_frame = QFrame()
        tab_frame.setStyleSheet("background-color: #E8ECEF; border-bottom: 1px solid #DCDCDC;")
        tab_layout = QHBoxLayout(tab_frame)
        tab_layout.setContentsMargins(10, 4, 10, 0)
        tab_layout.setSpacing(4)

        active_tab = QFrame()
        active_tab.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border: 1px solid #CCCCCC;
                border-bottom: none;
            }
        """)
        active_layout = QHBoxLayout(active_tab)
        active_layout.setContentsMargins(10, 5, 8, 5)

        tab_icon = QLabel()
        tab_icon.setPixmap(self.get_custom_icon("Home", FIF.HOME).pixmap(14, 14))
        active_layout.addWidget(tab_icon)

        self.tab_title = QLabel("Home")
        self.tab_title.setStyleSheet("font-size: 12px; color: #1A1A1A; font-weight: 500;")
        active_layout.addWidget(self.tab_title)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(16, 16)
        close_btn.setStyleSheet("QPushButton { border: none; color: #666; font-size: 10px; } QPushButton:hover { background: #E0E0E0; border-radius: 8px; }")
        active_layout.addWidget(close_btn)

        tab_layout.addWidget(active_tab)

        new_tab_btn = QPushButton("+")
        new_tab_btn.setFixedSize(26, 26)
        new_tab_btn.setStyleSheet("QPushButton { border: none; font-size: 16px; color: #555; } QPushButton:hover { background: #D8DCDC; border-radius: 4px; }")
        tab_layout.addWidget(new_tab_btn)

        tab_layout.addStretch()
        self.root_layout.addWidget(tab_frame)

    # --- 2. COMMAND BAR ---
    def setup_command_bar(self):
        cmd_frame = QFrame()
        cmd_frame.setStyleSheet("background-color: #F9F9F9; border-bottom: 1px solid #E5E5E5;")
        cmd_layout = QHBoxLayout(cmd_frame)
        cmd_layout.setContentsMargins(10, 4, 10, 4)
        cmd_layout.setSpacing(10)

        btn_style = """
            QPushButton {
                background: transparent;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                color: #222222;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #EAEAEA; }
        """

        self.new_btn = QPushButton("⊕ New")
        self.new_btn.setStyleSheet(btn_style)
        self.new_btn.clicked.connect(self.create_new_folder)
        cmd_layout.addWidget(self.new_btn)

        for text in ["✂ Cut", "📋 Copy", "↗ Share"]:
            btn = QPushButton(text)
            btn.setStyleSheet(btn_style)
            cmd_layout.addWidget(btn)

        self.delete_btn = QPushButton("🗑 Delete")
        self.delete_btn.setStyleSheet(btn_style)
        self.delete_btn.clicked.connect(self.delete_selected_item)
        cmd_layout.addWidget(self.delete_btn)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("color: #DDD;")
        cmd_layout.addWidget(sep)

        for text in ["⇅ Sort ∨", "⊞ View ∨", "▽ Filter ∨", "•••"]:
            btn = QPushButton(text)
            btn.setStyleSheet(btn_style)
            cmd_layout.addWidget(btn)

        cmd_layout.addStretch()
        self.root_layout.addWidget(cmd_frame)

    # --- 3. ADDRESS BAR ---
    def setup_address_bar(self):
        addr_frame = QFrame()
        addr_frame.setStyleSheet("background-color: #FFFFFF; border-bottom: 1px solid #E5E5E5;")
        addr_layout = QHBoxLayout(addr_frame)
        addr_layout.setContentsMargins(10, 6, 10, 6)
        addr_layout.setSpacing(8)

        nav_style = "QPushButton { border: none; background: transparent; border-radius: 4px; font-size: 13px; } QPushButton:hover { background: #F0F0F0; }"

        self.back_btn = QPushButton("←")
        self.back_btn.setFixedSize(26, 26)
        self.back_btn.setStyleSheet(nav_style)
        self.back_btn.clicked.connect(self.navigate_back)
        addr_layout.addWidget(self.back_btn)

        self.forward_btn = QPushButton("→")
        self.forward_btn.setFixedSize(26, 26)
        self.forward_btn.setStyleSheet(nav_style)
        addr_layout.addWidget(self.forward_btn)

        self.up_btn = QPushButton("↑")
        self.up_btn.setFixedSize(26, 26)
        self.up_btn.setStyleSheet(nav_style)
        self.up_btn.clicked.connect(self.navigate_up)
        addr_layout.addWidget(self.up_btn)

        # Breadcrumb
        path_box = QFrame()
        path_box.setStyleSheet("background-color: #F3F3F3; border: 1px solid #E0E0E0; border-radius: 4px;")
        path_layout = QHBoxLayout(path_box)
        path_layout.setContentsMargins(8, 2, 8, 2)

        home_icon = QLabel()
        home_icon.setPixmap(self.get_custom_icon("Home", FIF.HOME).pixmap(14, 14))
        path_layout.addWidget(home_icon)

        self.path_label = QLabel("Home ›")
        self.path_label.setStyleSheet("border: none; color: #222; font-size: 12px;")
        path_layout.addWidget(self.path_label)
        path_layout.addStretch()

        addr_layout.addWidget(path_box, stretch=3)

        # Search Bar
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search Home")
        self.search_box.setStyleSheet("QLineEdit { background-color: #F3F3F3; border: 1px solid #E0E0E0; border-radius: 4px; padding: 4px 8px; font-size: 12px; }")
        self.search_box.textChanged.connect(self.filter_files)
        addr_layout.addWidget(self.search_box, stretch=1)

        self.root_layout.addWidget(addr_frame)

    # --- 4a. SIDEBAR ---
    def setup_sidebar(self, layout):
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setIconSize(QSize(18, 18))
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #F3F3F3;
                border: none;
                border-right: 1px solid #E5E5E5;
                color: #202020;
                font-size: 12px;
                padding-top: 8px;
            }
            QListWidget::item { padding: 6px 12px; border-radius: 4px; margin: 1px 6px; }
            QListWidget::item:hover { background-color: #E5E5E5; }
            QListWidget::item:selected { background-color: #CCE4F7; color: #000; font-weight: 500; }
        """)
        layout.addWidget(self.sidebar)
        self.sidebar.currentRowChanged.connect(self.sidebar_changed)

        sidebar_items = [
            ("Home", "Home", "home", FIF.HOME),
            ("OneDrive", "onedrive", "onedrive", FIF.CLOUD),
            ("Desktop", "desktop", "desktop", FIF.APPLICATION),
            ("Documents", "Documents", "documents", FIF.DOCUMENT),
            ("Downloads", "Downloads", "downloads", FIF.DOWNLOAD),
            ("Pictures", "Pictures", "pictures", FIF.PHOTO),
            ("Music", "music", "music", FIF.MUSIC),
            ("Videos", "videos", "videos", FIF.VIDEO),
            ("This PC", "computer", "this_pc", FIF.INFO),
            ("Local Disk (C:)", "hdd", "disk_c", FIF.FOLDER)
        ]

        for text, icon_name, key, fallback in sidebar_items:
            icon = self.get_custom_icon(icon_name, fallback)
            item = QListWidgetItem(icon, text)
            item.setData(Qt.ItemDataRole.UserRole, key)
            self.sidebar.addItem(item)

    # --- 4b. MAIN CONTENT AREA ---
    def setup_main_content(self, layout):
        # QStackedWidget prevents Qt from deleting pages when switching views
        self.view_stack = QStackedWidget()

        # PAGE 0: Home View (Scrollable Quick Access + Favorites)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: #FFFFFF; }")

        self.home_widget = QWidget()
        vbox = QVBoxLayout(self.home_widget)
        vbox.setContentsMargins(20, 15, 20, 15)
        vbox.setSpacing(15)

        # Quick access
        qa_label = QLabel("∨ Quick access")
        qa_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #005A9E;")
        vbox.addWidget(qa_label)

        self.qa_grid = QListWidget()
        self.qa_grid.setViewMode(QListView.ViewMode.IconMode)
        self.qa_grid.setIconSize(QSize(36, 36))
        self.qa_grid.setGridSize(QSize(180, 65))
        self.qa_grid.setFixedHeight(150)
        self.qa_grid.setStyleSheet("""
            QListWidget { border: none; background: transparent; }
            QListWidget::item {
                background-color: #F9F9F9;
                border: 1px solid #E8E8E8;
                border-radius: 6px;
                padding: 6px;
                color: #222;
            }
            QListWidget::item:hover { background-color: #F0F4F8; border-color: #C0D8F0; }
        """)
        vbox.addWidget(self.qa_grid)

        qa_folders = [
            ("Desktop", "desktop", "Desktop"),
            ("Documents", "Documents", "Documents"),
            ("Downloads", "Downloads", "Downloads"),
            ("Pictures", "Pictures", "Pictures"),
            ("Music", "music", "Music"),
            ("Videos", "videos", "Videos")
        ]
        for title, icon_name, subpath in qa_folders:
            icon = self.get_custom_icon(icon_name, FIF.FOLDER)
            item = QListWidgetItem(icon, f"{title}\nStored locally")
            item.setData(Qt.ItemDataRole.UserRole, os.path.join(self.home_path, subpath))
            self.qa_grid.addItem(item)

        self.qa_grid.itemDoubleClicked.connect(self.folder_double_clicked)

        # Favorites
        fav_label = QLabel("∨ Favorites")
        fav_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #005A9E;")
        vbox.addWidget(fav_label)

        self.fav_table = QTableWidget(3, 3)
        self.fav_table.setHorizontalHeaderLabels(["Name", "Date modified", "Location"])
        self.fav_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.fav_table.verticalHeader().setVisible(False)
        self.fav_table.setShowGrid(False)
        self.fav_table.setStyleSheet("QTableWidget { border: none; background: transparent; font-size: 12px; color: #222; }")

        fav_files = [
            ("Methodologies_white_paper.pdf", "6/25/2026 9:56 PM", "OneDrive"),
            ("DSC_0071.jpg", "6/25/2026 9:54 PM", "OneDrive"),
            ("Class Notes.docx", "6/25/2026 9:34 PM", "OneDrive")
        ]
        for row, (name, date, loc) in enumerate(fav_files):
            self.fav_table.setItem(row, 0, QTableWidgetItem(name))
            self.fav_table.setItem(row, 1, QTableWidgetItem(date))
            self.fav_table.setItem(row, 2, QTableWidgetItem(loc))

        vbox.addWidget(self.fav_table)
        scroll_area.setWidget(self.home_widget)
        self.view_stack.addWidget(scroll_area) # Index 0

        # PAGE 1: Directory File Grid
        self.dir_file_grid = QListWidget()
        self.dir_file_grid.setViewMode(QListView.ViewMode.IconMode)
        self.dir_file_grid.setIconSize(QSize(48, 48))
        self.dir_file_grid.setGridSize(QSize(110, 100))
        self.dir_file_grid.setStyleSheet("""
            QListWidget { border: none; background-color: #FFFFFF; padding: 10px; }
            QListWidget::item { border-radius: 6px; padding: 8px; color: #222; font-size: 11px; }
            QListWidget::item:hover { background-color: #F0F4F8; }
            QListWidget::item:selected { background-color: #CCE4F7; color: #000; }
        """)
        self.dir_file_grid.itemDoubleClicked.connect(self.folder_double_clicked)
        self.view_stack.addWidget(self.dir_file_grid) # Index 1

        layout.addWidget(self.view_stack, stretch=1)

    # --- 5. STATUS BAR ---
    def setup_status_bar(self):
        status_frame = QFrame()
        status_frame.setStyleSheet("background-color: #F3F3F3; border-top: 1px solid #E5E5E5;")
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(15, 3, 15, 3)

        self.items_count = QLabel("0 items")
        self.items_count.setStyleSheet("font-size: 11px; color: #555;")
        status_layout.addWidget(self.items_count)
        status_layout.addStretch()

        self.root_layout.addWidget(status_frame)

    # --- CORE FILE SYSTEM LOGIC ---
    def show_home_view(self):
        self.current_path = "Home"
        self.path_label.setText("Home ›")
        self.tab_title.setText("Home")
        self.search_box.setPlaceholderText("🔍 Search Home")
        self.view_stack.setCurrentIndex(0) # Safely switch to Page 0
        self.items_count.setText("9 items")

    def load_directory(self, path, add_to_history=True):
        if not os.path.exists(path):
            return

        if add_to_history and self.current_path != path:
            self.history.append(self.current_path)

        self.current_path = path
        folder_name = os.path.basename(path) or path
        self.path_label.setText(f"{path} ›")
        self.tab_title.setText(folder_name)
        self.search_box.setPlaceholderText(f"🔍 Search {folder_name}")

        self.dir_file_grid.clear()

        try:
            entries = list(os.scandir(path))
            visible_entries = [e for e in entries if not e.name.startswith('.')]
            
            for entry in visible_entries:
                file_info = QFileInfo(entry.path)
                icon = self.icon_provider.icon(file_info)
                
                item = QListWidgetItem(icon, entry.name)
                item.setData(Qt.ItemDataRole.UserRole, entry.path)
                self.dir_file_grid.addItem(item)

            self.items_count.setText(f"{len(visible_entries)} items")
        except Exception:
            self.items_count.setText("Access Denied")

        self.view_stack.setCurrentIndex(1) # Safely switch to Page 1

    def folder_double_clicked(self, item):
        target_path = item.data(Qt.ItemDataRole.UserRole)
        if target_path and os.path.isdir(target_path):
            self.load_directory(target_path)

    def sidebar_changed(self, row):
        item = self.sidebar.item(row)
        if not item: return
        key = item.data(Qt.ItemDataRole.UserRole)

        paths_map = {
            "home": "Home",
            "desktop": os.path.join(self.home_path, "Desktop"),
            "downloads": os.path.join(self.home_path, "Downloads"),
            "documents": os.path.join(self.home_path, "Documents"),
            "pictures": os.path.join(self.home_path, "Pictures"),
            "music": os.path.join(self.home_path, "Music"),
            "videos": os.path.join(self.home_path, "Videos"),
            "this_pc": self.home_path,
            "disk_c": "C:\\" if os.name == 'nt' else "/"
        }

        target = paths_map.get(key)
        if target == "Home":
            self.show_home_view()
        elif target and os.path.exists(target):
            self.load_directory(target)

    def navigate_up(self):
        if self.current_path != "Home" and os.path.isdir(self.current_path):
            parent = os.path.dirname(self.current_path)
            if parent and parent != self.current_path:
                self.load_directory(parent)
            else:
                self.show_home_view()

    def navigate_back(self):
        if self.history:
            prev_path = self.history.pop()
            if prev_path == "Home":
                self.show_home_view()
            else:
                self.load_directory(prev_path, add_to_history=False)

    def create_new_folder(self):
        if self.current_path == "Home" or not os.path.isdir(self.current_path):
            return

        folder_name, ok = QInputDialog.getText(self, "New Folder", "Enter folder name:")
        if ok and folder_name:
            new_path = os.path.join(self.current_path, folder_name)
            try:
                os.makedirs(new_path, exist_ok=True)
                self.load_directory(self.current_path, add_to_history=False)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not create folder: {e}")

    def delete_selected_item(self):
        if self.current_path == "Home":
            return

        current_item = self.dir_file_grid.currentItem()
        if not current_item:
            return

        target_path = current_item.data(Qt.ItemDataRole.UserRole)
        confirm = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete '{os.path.basename(target_path)}'?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                if os.path.isdir(target_path):
                    shutil.rmtree(target_path)
                else:
                    os.remove(target_path)
                self.load_directory(self.current_path, add_to_history=False)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not delete item: {e}")

    def filter_files(self, text):
        if self.current_path == "Home":
            return

        for i in range(self.dir_file_grid.count()):
            item = self.dir_file_grid.item(i)
            item.setHidden(text.lower() not in item.text().lower())