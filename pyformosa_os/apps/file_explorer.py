import os
import sys
from PyQt6.QtCore import Qt, QSize, QFileInfo
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem,
    QListView, QFileIconProvider, QLabel, QPushButton, QFrame, QLineEdit, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from qfluentwidgets import FluentIcon as FIF, IconWidget

try:
    from desktop.window_frame import DraggableWindowFrame
except ImportError:
    from PyQt6.QtWidgets import QMainWindow as DraggableWindowFrame


class FileExplorerApp(DraggableWindowFrame):
    def __init__(self, parent=None):
        super().__init__("File Explorer", parent)

        # Paths
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(self.current_dir)
        self.assets_dir = os.path.join(self.project_root, "assets", "icons")

        self.icon_provider = QFileIconProvider()
        self.current_path = os.path.expanduser("~")

        self.set_window_custom_icon()

        # Build Main UI Structure
        self.init_ui()

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

    # --- UI INITIALIZATION ---
    def init_ui(self):
        # Base container
        self.main_container = QWidget()
        self.main_container.setStyleSheet("background-color: #FFFFFF; font-family: 'Segoe UI', sans-serif;")
        
        if hasattr(self, 'layout') and self.layout is not None:
            self.layout.addWidget(self.main_container, stretch=1)
        
        self.root_layout = QVBoxLayout(self.main_container)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        # 1. Tab Bar
        self.setup_tab_bar()

        # 2. Command Bar (New, Cut, Copy, Sort, View, etc.)
        self.setup_command_bar()

        # 3. Address Bar & Search Bar
        self.setup_address_bar()

        # 4. Central Split (Sidebar + Content View)
        content_split = QHBoxLayout()
        content_split.setContentsMargins(0, 0, 0, 0)
        content_split.setSpacing(0)
        self.root_layout.addLayout(content_split, stretch=1)

        # 4a. Left Sidebar Navigation
        self.setup_sidebar(content_split)

        # 4b. Right Main Content Area (Quick Access + Favorites + File View)
        self.setup_main_content(content_split)

        # 5. Status Bar
        self.setup_status_bar()

    # --- 1. TAB BAR ---
    def setup_tab_bar(self):
        tab_frame = QFrame()
        tab_frame.setStyleSheet("background-color: #E8ECEF; border-bottom: 1px solid #E0E0E0;")
        tab_layout = QHBoxLayout(tab_frame)
        tab_layout.setContentsMargins(10, 5, 10, 0)
        tab_layout.setSpacing(5)

        # Active "Home" Tab
        active_tab = QFrame()
        active_tab.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border: 1px solid #D0D0D0;
                border-bottom: none;
            }
        """)
        active_tab_layout = QHBoxLayout(active_tab)
        active_tab_layout.setContentsMargins(10, 6, 8, 6)
        
        tab_icon = QLabel()
        tab_icon.setPixmap(self.get_custom_icon("Home", FIF.HOME).pixmap(16, 16))
        active_tab_layout.addWidget(tab_icon)

        tab_title = QLabel("Home")
        tab_title.setStyleSheet("font-size: 12px; color: #1A1A1A; font-weight: 500;")
        active_tab_layout.addWidget(tab_title)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(16, 16)
        close_btn.setStyleSheet("QPushButton { border: none; color: #666; font-size: 10px; } QPushButton:hover { background: #E0E0E0; border-radius: 8px; }")
        active_tab_layout.addWidget(close_btn)

        tab_layout.addWidget(active_tab)

        # New Tab Button
        new_tab_btn = QPushButton("+")
        new_tab_btn.setFixedSize(28, 28)
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
        cmd_layout.setSpacing(12)

        btn_style = """
            QPushButton {
                background: transparent;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                color: #333333;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #EAEAEA; }
        """

        # Action items from reference image
        actions = [
            ("⊕ New", FIF.ADD),
            ("✂", FIF.CUT),
            ("📋", FIF.COPY),
            ("↗", FIF.SHARE),
            ("🗑", FIF.DELETE),
        ]

        for text, fluent_icon in actions:
            btn = QPushButton(text)
            btn.setStyleSheet(btn_style)
            cmd_layout.addWidget(btn)

        # Separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.VLine)
        sep1.setStyleSheet("color: #DDD;")
        cmd_layout.addWidget(sep1)

        # Dropdown Actions
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

        nav_btn_style = "QPushButton { border: none; background: transparent; border-radius: 4px; } QPushButton:hover { background: #F0F0F0; }"

        # Navigation Arrows
        back_btn = QPushButton(FIF.LEFT_ARROW.qicon(), "")
        back_btn.setFixedSize(26, 26)
        back_btn.setStyleSheet(nav_btn_style)
        
        forward_btn = QPushButton(FIF.RIGHT_ARROW.qicon(), "")
        forward_btn.setFixedSize(26, 26)
        forward_btn.setStyleSheet(nav_btn_style)

        up_btn = QPushButton(FIF.UP.qicon(), "")
        up_btn.setFixedSize(26, 26)
        up_btn.setStyleSheet(nav_btn_style)
        up_btn.clicked.connect(self.navigate_up)

        addr_layout.addWidget(back_btn)
        addr_layout.addWidget(forward_btn)
        addr_layout.addWidget(up_btn)

        # Breadcrumb Address Pill
        self.path_box = QFrame()
        self.path_box.setStyleSheet("QFrame { background-color: #F3F3F3; border: 1px solid #E0E0E0; border-radius: 4px; }")
        path_layout = QHBoxLayout(self.path_box)
        path_layout.setContentsMargins(8, 2, 8, 2)

        home_icon = QLabel()
        home_icon.setPixmap(self.get_custom_icon("Home", FIF.HOME).pixmap(14, 14))
        path_layout.addWidget(home_icon)

        self.path_label = QLabel("Home ›")
        self.path_label.setStyleSheet("border: none; color: #222; font-size: 12px;")
        path_layout.addWidget(self.path_label)
        path_layout.addStretch()

        reload_btn = QPushButton(FIF.SYNC.qicon(), "")
        reload_btn.setFixedSize(20, 20)
        reload_btn.setStyleSheet("border: none;")
        path_layout.addWidget(reload_btn)

        addr_layout.addWidget(self.path_box, stretch=3)

        # Search Box
        search_box = QLineEdit()
        search_box.setPlaceholderText("🔍 Search Home")
        search_box.setStyleSheet("""
            QLineEdit {
                background-color: #F3F3F3;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
            }
        """)
        addr_layout.addWidget(search_box, stretch=1)

        self.root_layout.addWidget(addr_frame)

    # --- 4a. LEFT SIDEBAR ---
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
            QListWidget::item {
                padding: 6px 12px;
                border-radius: 4px;
                margin: 1px 6px;
            }
            QListWidget::item:hover {
                background-color: #E5E5E5;
            }
            QListWidget::item:selected {
                background-color: #CCE4F7;
                color: #000000;
                font-weight: 500;
            }
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
            ("This PC", "computer", "this_pc", FIF.IMPORTANT),
            ("Local Disk (C:)", "hdd", "disk_c", FIF.FOLDER)
        ]

        for text, icon_name, key, fallback in sidebar_items:
            icon = self.get_custom_icon(icon_name, fallback)
            item = QListWidgetItem(icon, text)
            item.setData(Qt.ItemDataRole.UserRole, key)
            self.sidebar.addItem(item)

    # --- 4b. MAIN CONTENT AREA ---
    def setup_main_content(self, layout):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: #FFFFFF; }")

        content_widget = QWidget()
        self.content_vbox = QVBoxLayout(content_widget)
        self.content_vbox.setContentsMargins(20, 15, 20, 15)
        self.content_vbox.setSpacing(20)

        # 1. Quick Access Section Header
        qa_label = QLabel("∨ Quick access")
        qa_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #005A9E;")
        self.content_vbox.addWidget(qa_label)

        # Quick Access Grid Panel
        self.qa_grid = QListWidget()
        self.qa_grid.setViewMode(QListView.ViewMode.IconMode)
        self.qa_grid.setIconSize(QSize(40, 40))
        self.qa_grid.setGridSize(QSize(180, 70))
        self.qa_grid.setMovement(QListView.Movement.Static)
        self.qa_grid.setFixedHeight(160)
        self.qa_grid.setStyleSheet("""
            QListWidget { border: none; background: transparent; }
            QListWidget::item {
                background-color: #F9F9F9;
                border: 1px solid #E8E8E8;
                border-radius: 6px;
                padding: 6px;
            }
            QListWidget::item:hover { background-color: #F0F4F8; border-color: #C0D8F0; }
        """)
        self.content_vbox.addWidget(self.qa_grid)

        # Populate Quick Access Folders matching image
        qa_folders = [
            ("Desktop", "desktop", "Desktop"),
            ("Documents", "Documents", "Documents"),
            ("Downloads", "Downloads", "Downloads"),
            ("Pictures", "Pictures", "Pictures"),
            ("Music", "music", "Music"),
            ("Videos", "videos", "Videos")
        ]
        user_home = os.path.expanduser("~")
        for title, icon_name, subpath in qa_folders:
            icon = self.get_custom_icon(icon_name, FIF.FOLDER)
            item = QListWidgetItem(icon, f"{title}\nStored locally")
            item.setData(Qt.ItemDataRole.UserRole, os.path.join(user_home, subpath))
            self.qa_grid.addItem(item)
            
        self.qa_grid.itemDoubleClicked.connect(self.folder_double_clicked)

        # 2. Favorites Section Header
        fav_label = QLabel("∨ Favorites")
        fav_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #005A9E;")
        self.content_vbox.addWidget(fav_label)

        # Favorites File Table matching image
        self.fav_table = QTableWidget(3, 3)
        self.fav_table.setHorizontalHeaderLabels(["Name", "Date modified", "Location"])
        self.fav_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.fav_table.verticalHeader().setVisible(False)
        self.fav_table.setShowGrid(False)
        self.fav_table.setStyleSheet("""
            QTableWidget { border: none; background: transparent; font-size: 12px; }
            QTableWidget::item { padding: 4px; }
        """)
        
        # Sample Favorites matching image
        fav_files = [
            ("Methodologies_white_paper.pdf", "6/25/2026 9:56 PM", "OneDrive"),
            ("DSC_0071.jpg", "6/25/2026 9:54 PM", "OneDrive"),
            ("Class Notes.docx", "6/25/2026 9:34 PM", "OneDrive")
        ]
        for row, (name, date, loc) in enumerate(fav_files):
            self.fav_table.setItem(row, 0, QTableWidgetItem(name))
            self.fav_table.setItem(row, 1, QTableWidgetItem(date))
            self.fav_table.setItem(row, 2, QTableWidgetItem(loc))

        self.content_vbox.addWidget(self.fav_table)

        # 3. Recent Section Header
        recent_label = QLabel("∨ Recent")
        recent_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #555;")
        self.content_vbox.addWidget(recent_label)

        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area, stretch=1)

    # --- 5. STATUS BAR ---
    def setup_status_bar(self):
        status_frame = QFrame()
        status_frame.setStyleSheet("background-color: #F3F3F3; border-top: 1px solid #E5E5E5;")
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(15, 3, 15, 3)

        items_count = QLabel("9 items")
        items_count.setStyleSheet("font-size: 11px; color: #555;")
        status_layout.addWidget(items_count)

        status_layout.addStretch()

        # View mode toggle icons on far right
        grid_view_btn = QPushButton("⊞")
        list_view_btn = QPushButton("☰")
        for btn in [grid_view_btn, list_view_btn]:
            btn.setFixedSize(22, 22)
            btn.setStyleSheet("QPushButton { border: none; color: #555; } QPushButton:hover { background: #E0E0E0; }")
            status_layout.addWidget(btn)

        self.root_layout.addWidget(status_frame)

    # --- ACTIONS & NAVIGATION ---
    def navigate_up(self):
        parent_dir = os.path.dirname(self.current_path)
        if parent_dir != self.current_path:
            self.load_directory(parent_dir)

    def sidebar_changed(self, row):
        item = self.sidebar.item(row)
        if not item: return
        key = item.data(Qt.ItemDataRole.UserRole)

        user_home = os.path.expanduser("~")
        paths_map = {
            "home": user_home,
            "desktop": os.path.join(user_home, "Desktop"),
            "downloads": os.path.join(user_home, "Downloads"),
            "documents": os.path.join(user_home, "Documents"),
            "pictures": os.path.join(user_home, "Pictures"),
            "music": os.path.join(user_home, "Music"),
            "videos": os.path.join(user_home, "Videos"),
            "this_pc": user_home,
            "disk_c": "C:\\" if os.name == 'nt' else "/"
        }

        target_path = paths_map.get(key)
        if target_path and os.path.exists(target_path):
            self.load_directory(target_path)

    def load_directory(self, path):
        self.current_path = path
        self.path_label.setText(f"{os.path.basename(path) or path} ›")

    def folder_double_clicked(self, item):
        target = item.data(Qt.ItemDataRole.UserRole)
        if target and os.path.isdir(target):
            self.load_directory(target)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileExplorerApp()
    window.resize(950, 650)
    window.show()
    sys.exit(app.exec())