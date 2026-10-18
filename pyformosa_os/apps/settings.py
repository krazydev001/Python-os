import os
import sys
import ctypes
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QCheckBox, QRadioButton, QButtonGroup, QPushButton, QFileDialog, 
    QScrollArea, QListWidget, QListWidgetItem, QStackedWidget, QFrame, QMessageBox
)
from qfluentwidgets import FluentIcon as FIF
from desktop.window_frame import DraggableWindowFrame

# Force Windows Host process model isolation
try:
    myappid = 'pyformoso.os.settings.app'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass


class SettingsApp(DraggableWindowFrame):
    """Modern Settings App for PyFormoso OS inspired by modern desktop UX."""
    def __init__(self, parent=None):
        super().__init__("System Settings", parent)
        self.resize(900, 620)
        
        self.app_name = "Settings"
        self.icon_name = "settings"
        
        # Absolute Paths Setup
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(self.current_dir)
        self.assets_dir = os.path.normpath(os.path.join(self.project_root, "assets", "icons"))
        
        self.set_custom_window_icon()
        
        # Content Root Container
        self.content_area = QWidget(self)
        self.content_area.setStyleSheet("background-color: #181818; font-family: 'Segoe UI', sans-serif;")
        self.layout.addWidget(self.content_area, stretch=1)
        
        main_layout = QHBoxLayout(self.content_area)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. Left Navigation Sidebar
        self.setup_sidebar(main_layout)
        
        # 2. Right Page Stack View
        self.setup_pages_stack(main_layout)
        
        # Default view page
        self.sidebar.setCurrentRow(0)

    def get_custom_icon(self, icon_name: str, fallback_fluent=None) -> QIcon:
        for ext in [".png", ".ico", ".svg", ".jpg"]:
            icon_path = os.path.normpath(os.path.join(self.assets_dir, f"{icon_name}{ext}"))
            if os.path.exists(icon_path):
                return QIcon(icon_path)
        if fallback_fluent:
            return fallback_fluent.qicon()
        return QIcon()

    def set_custom_window_icon(self):
        icon = self.get_custom_icon("settings", FIF.SETTING)
        if not icon.isNull():
            self.setWindowIcon(icon)

    # ==========================================
    # --- 1. LEFT SIDEBAR NAVIGATION ---
    # ==========================================
    def setup_sidebar(self, parent_layout):
        sidebar_frame = QFrame()
        sidebar_frame.setFixedWidth(230)
        sidebar_frame.setStyleSheet("""
            QFrame {
                background-color: #202020;
                border-right: 1px solid rgba(255, 255, 255, 0.05);
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setContentsMargins(10, 20, 10, 15)
        sidebar_layout.setSpacing(10)

        # Navigation Menu List
        self.sidebar = QListWidget()
        self.sidebar.setIconSize(QSize(18, 18))
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                color: #CCCCCC;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 10px 12px;
                border-radius: 6px;
                margin-bottom: 2px;
            }
            QListWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.05);
            }
            QListWidget::item:selected {
                background-color: rgba(255, 255, 255, 0.1);
                color: #FFFFFF;
                font-weight: 600;
            }
        """)
        
        # Strictly using 100% standard attributes: SETTING, PALETTE, INFO
        nav_items = [
            ("System", FIF.SETTING, 0),
            ("Personalization", FIF.PALETTE, 1),
            ("Boot & Security", FIF.SETTING, 2), 
            ("About PyFormoso", FIF.INFO, 3)
        ]

        for text, fluent_icon, page_idx in nav_items:
            item = QListWidgetItem(fluent_icon.qicon(), text)
            item.setData(Qt.ItemDataRole.UserRole, page_idx)
            self.sidebar.addItem(item)

        self.sidebar.currentRowChanged.connect(self.change_page)
        sidebar_layout.addWidget(self.sidebar)
        sidebar_layout.addStretch()

        parent_layout.addWidget(sidebar_frame)

    # ==========================================
    # --- 2. RIGHT CONTENT STACK ---
    # ==========================================
    def setup_pages_stack(self, parent_layout):
        self.pages_stack = QStackedWidget()
        self.pages_stack.setStyleSheet("background-color: #181818;")

        # Adding Pages
        self.pages_stack.addWidget(self.create_system_page())         # Index 0
        self.pages_stack.addWidget(self.create_personalization_page())# Index 1
        self.pages_stack.addWidget(self.create_security_page())       # Index 2
        self.pages_stack.addWidget(self.create_about_page())          # Index 3

        parent_layout.addWidget(self.pages_stack, stretch=1)

    def change_page(self, row):
        item = self.sidebar.item(row)
        if item:
            page_idx = item.data(Qt.ItemDataRole.UserRole)
            self.pages_stack.setCurrentIndex(page_idx)

    # --- CARD WIDGET HELPER ---
    def create_setting_card(self, title, description, widget_control=None):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #202020;
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 8px;
            }
            QFrame:hover {
                border: 1px solid rgba(255, 255, 255, 0.12);
            }
        """)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)

        info_vbox = QVBoxLayout()
        info_vbox.setSpacing(2)
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: white; font-size: 13px; font-weight: 600; border: none;")
        lbl_desc = QLabel(description)
        lbl_desc.setStyleSheet("color: #888888; font-size: 11px; border: none;")
        info_vbox.addWidget(lbl_title)
        info_vbox.addWidget(lbl_desc)

        layout.addLayout(info_vbox, stretch=1)

        if widget_control:
            layout.addWidget(widget_control)

        return card

    # ==========================================
    # --- PAGE 1: SYSTEM PAGE ---
    # ==========================================
    def create_system_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        banner = QFrame()
        banner.setStyleSheet("background-color: #202020; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05);")
        b_layout = QHBoxLayout(banner)
        b_layout.setContentsMargins(15, 15, 15, 15)

        banner_icon = QLabel("💻")
        banner_icon.setStyleSheet("font-size: 40px;")
        b_layout.addWidget(banner_icon)

        pc_info = QVBoxLayout()
        pc_title = QLabel("PyFormoso Workstation")
        pc_title.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        pc_sub = QLabel("PyFormoso OS Kernel v1.0 • x64 Desktop Platform")
        pc_sub.setStyleSheet("color: #888888; font-size: 12px;")
        pc_info.addWidget(pc_title)
        pc_info.addWidget(pc_sub)
        b_layout.addLayout(pc_info, stretch=1)

        layout.addWidget(banner)

        layout.addWidget(QLabel("System Options", styleSheet="color: white; font-size: 14px; font-weight: bold; margin-top: 10px;"))
        layout.addWidget(self.create_setting_card("Display & Monitors", "Resolution, scale, brightness, and display profiles"))
        layout.addWidget(self.create_setting_card("Sound & Audio", "Volume levels, output devices, and sound effects"))
        layout.addWidget(self.create_setting_card("Storage Manager", "Disk space utilization and directory configuration"))
        layout.addStretch()
        return page

    # ==========================================
    # --- PAGE 2: PERSONALIZATION PAGE ---
    # ==========================================
    def create_personalization_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        layout.addWidget(QLabel("Personalization", styleSheet="color: white; font-size: 18px; font-weight: bold;"))

        theme_controls = QWidget()
        tc_layout = QHBoxLayout(theme_controls)
        tc_layout.setContentsMargins(0, 0, 0, 0)

        self.btn_dark = QRadioButton("Dark Mode")
        self.btn_dark.setChecked(True)
        self.btn_light = QRadioButton("Light Mode")
        
        radio_style = "QRadioButton { color: white; font-size: 12px; margin-left: 8px; } QRadioButton::indicator { width: 14px; height: 14px; }"
        self.btn_dark.setStyleSheet(radio_style)
        self.btn_light.setStyleSheet(radio_style)

        tc_layout.addWidget(self.btn_dark)
        tc_layout.addWidget(self.btn_light)
        layout.addWidget(self.create_setting_card("Color Theme", "Select dark or light interface modes", theme_controls))

        wp_picker_widget = QWidget()
        wp_layout = QHBoxLayout(wp_picker_widget)
        wp_layout.setContentsMargins(0, 0, 0, 0)
        wp_layout.setSpacing(8)

        self.wallpaper_input = QLineEdit()
        self.wallpaper_input.setFixedWidth(220)
        self.wallpaper_input.setStyleSheet("QLineEdit { background-color: #181818; border: 1px solid rgba(255,255,255,0.2); border-radius: 4px; color: white; padding: 4px 8px; font-size: 11px; }")
        
        default_wp = os.path.normpath(os.path.join(self.project_root, "assets", "wallpapers", "wallpaper1.jpg"))
        if os.path.exists(default_wp):
            self.wallpaper_input.setText(default_wp)

        browse_btn = QPushButton("Browse...")
        browse_btn.setStyleSheet("QPushButton { background-color: #333333; border: none; border-radius: 4px; color: white; padding: 6px 12px; font-size: 11px; } QPushButton:hover { background-color: #444444; }")
        browse_btn.clicked.connect(self.browse_wallpaper)

        wp_layout.addWidget(self.wallpaper_input)
        wp_layout.addWidget(browse_btn)

        layout.addWidget(self.create_setting_card("Desktop Background", "Set custom image path for desktop wallpaper", wp_picker_widget))

        save_btn = QPushButton("Apply Personalization Changes")
        save_btn.setFixedHeight(36)
        save_btn.setStyleSheet("QPushButton { background-color: #0078D4; border: none; border-radius: 6px; color: white; font-weight: 600; font-size: 12px; } QPushButton:hover { background-color: #106EBE; }")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        layout.addStretch()
        return page

    # ==========================================
    # --- PAGE 3: BOOT & SECURITY PAGE ---
    # ==========================================
    def create_security_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        layout.addWidget(QLabel("Boot & Security", styleSheet="color: white; font-size: 18px; font-weight: bold;"))

        self.chk_boot_clip = QCheckBox()
        self.chk_boot_clip.setChecked(True)
        layout.addWidget(self.create_setting_card("Startup Boot Animation", "Play splash video clip on OS startup", self.chk_boot_clip))

        pwd_widget = QWidget()
        pwd_layout = QHBoxLayout(pwd_widget)
        pwd_layout.setContentsMargins(0, 0, 0, 0)

        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setText("")
        self.pwd_input.setPlaceholderText("Enter new password...")
        self.pwd_input.setFixedWidth(160)
        self.pwd_input.setStyleSheet("QLineEdit { background-color: #181818; border: 1px solid rgba(255,255,255,0.2); border-radius: 4px; color: white; padding: 4px 8px; font-size: 11px; }")
        pwd_layout.addWidget(self.pwd_input)
    
        layout.addWidget(self.create_setting_card("Lock Screen Password", "Set startup and screen lock authentication code", pwd_widget))

        self.chk_req_pwd = QCheckBox()
        self.chk_req_pwd.setChecked(False)
        layout.addWidget(self.create_setting_card("Require Password on Startup", "Prompt for authentication when launching desktop", self.chk_req_pwd))

        sec_save_btn = QPushButton("Save Security Settings")
        sec_save_btn.setFixedHeight(36)
        sec_save_btn.setStyleSheet("QPushButton { background-color: #0078D4; border: none; border-radius: 6px; color: white; font-weight: 600; font-size: 12px; } QPushButton:hover { background-color: #106EBE; }")
        sec_save_btn.clicked.connect(self.save_settings)
        layout.addWidget(sec_save_btn)

        layout.addStretch()
        return page

    # ==========================================
    # --- PAGE 4: ABOUT PAGE ---
    # ==========================================
    def create_about_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        layout.addWidget(QLabel("About PyFormoso OS", styleSheet="color: white; font-size: 18px; font-weight: bold;"))
        layout.addWidget(self.create_setting_card("PyFormoso OS Environment", "Custom Python & PyQt6 Desktop Shell Platform"))
        layout.addStretch()
        return page

    # ==========================================
    # --- ACTIONS & LOGIC ---
    # ==========================================
    def browse_wallpaper(self):
        file_path, _ = QFileDialog.getOpenFileName(
            None, "Select Wallpaper Image", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.wallpaper_input.setText(os.path.normpath(file_path))

    def save_settings(self):
        parent_os = self.window()
        
        selected_wallpaper = self.wallpaper_input.text()
        if os.path.exists(selected_wallpaper) and hasattr(parent_os, 'current_wallpaper'):
            parent_os.current_wallpaper = selected_wallpaper
            if hasattr(parent_os, 'update_wallpaper'):
                parent_os.update_wallpaper()

        is_dark = self.btn_dark.isChecked()
        if hasattr(parent_os, 'taskbar'):
            if is_dark:
                parent_os.taskbar.setStyleSheet("background-color: rgba(30, 30, 30, 0.85); border-top: 1px solid rgba(255,255,255,0.05);")
            else:
                parent_os.taskbar.setStyleSheet("background-color: rgba(243, 243, 243, 0.85); border-top: 1px solid rgba(0,0,0,0.05);")

        QMessageBox.information(self, "Settings Saved", "System settings applied successfully!")

    def closeEvent(self, event):
        parent_os = self.window()
        if hasattr(parent_os, 'running_apps') and self in parent_os.running_apps:
            parent_os.running_apps.remove(self)
        if hasattr(parent_os, 'taskbar') and hasattr(parent_os.taskbar, 'update_taskbar_buttons'):
            parent_os.taskbar.update_taskbar_buttons()
        elif hasattr(parent_os, 'update_taskbar'):
            parent_os.update_taskbar()
        super().closeEvent(event)