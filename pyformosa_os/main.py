import os
import sys
import ctypes
from PyQt6.QtCore import Qt, QSize, QUrl
from PyQt6.QtGui import QIcon, QFont, QPixmap, QBrush, QPalette
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QPushButton, QFrame, QLabel, QLineEdit, QStackedWidget
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

# Prevent icon clustering inside native OS environments
try:
    myappid = 'pyformoso.os.shell.core'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

# Safe App Router Imports
try:
    from apps.settings import SettingsApp
except ImportError:
    SettingsApp = None

class PyFormosoOS(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyFormoso OS")
        self.resize(1280, 800)
        
        # System State Tracking Arrays
        self.running_apps = []      
        self.taskbar_buttons = []   
        self.wifi_connected = True
        
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.assets_dir = os.path.normpath(os.path.join(self.project_root, "assets"))
        
        # Central Engine Stack Layer Management
        self.central_stack = QStackedWidget(self)
        self.setCentralWidget(self.central_stack)
        
        # Setup the Core Widgets First
        self.desktop_area = QWidget(self)
        
        # Now safely build out the system sequence interfaces
        self.build_boot_screen()
        self.build_sign_in_screen()
        self.build_main_desktop_shell()
        
        # Kickoff with cinematic video boot sequence
        self.trigger_system_boot()

    # -------------------------------------------------------------
    # PHASE 1: BOOT ANIMATION VIDEO SCREEN
    # -------------------------------------------------------------
    def build_boot_screen(self):
        self.boot_widget = QWidget()
        self.boot_widget.setStyleSheet("background-color: #000000;")
        boot_layout = QVBoxLayout(self.boot_widget)
        boot_layout.setContentsMargins(0, 0, 0, 0)
        
        self.video_widget = QVideoWidget(self.boot_widget)
        boot_layout.addWidget(self.video_widget)
        
        # Instantiate Media Engine
        self.media_player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)
        
        # Route to boot animation asset
        boot_video_path = os.path.normpath(os.path.join(self.assets_dir, "Clips", "Boot_Screen.mp4"))
        self.media_player.setSource(QUrl.fromLocalFile(boot_video_path))
        self.media_player.mediaStatusChanged.connect(self.handle_boot_status)
        
        self.central_stack.addWidget(self.boot_widget)

    def trigger_system_boot(self):
        self.central_stack.setCurrentWidget(self.boot_widget)
        self.media_player.play()

    def handle_boot_status(self, status):
        # Once the video asset finishes playing, automatically advance
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.media_player.stop()
            self.transition_to_sign_in()

    # -------------------------------------------------------------
    # PHASE 2: SIGN-IN SECURE PORTAL
    # -------------------------------------------------------------
    def build_sign_in_screen(self):
        self.signin_widget = QWidget()
        self.signin_widget.setStyleSheet("background-color: #151515;")
        
        layout = QVBoxLayout(self.signin_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)
        
        # Profile Picture Avatar Placeholder
        avatar = QLabel()
        avatar.setFixedSize(100, 100)
        avatar_path = os.path.join(self.assets_dir, "icons", "user_avatar.png")
        if os.path.exists(avatar_path):
            avatar.setPixmap(QPixmap(avatar_path).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            avatar.setText("👤")
            avatar.setFont(QFont("Segoe UI", 36))
            avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            avatar.setStyleSheet("color: white; background-color: #333; border-radius: 50px;")
        layout.addWidget(avatar, alignment=Qt.AlignmentFlag.AlignCenter)
        
        username_lbl = QLabel("Welcome Back, User")
        username_lbl.setStyleSheet("color: #FFFFFF; font-family: 'Segoe UI'; font-size: 18px; font-weight: bold;")
        layout.addWidget(username_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.password_field = QLineEdit()
        self.password_field.setPlaceholderText("Enter Lock Screen Password")
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_field.setFixedSize(260, 36)
        self.password_field.setStyleSheet("""
            QLineEdit {
                background-color: #222222;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 4px;
                color: white;
                padding-left: 10px;
                font-family: 'Segoe UI';
            }
            QLineEdit:focus { border: 1px solid #FF6B57; }
        """)
        self.password_field.returnPressed.connect(self.authenticate_user)
        layout.addWidget(self.password_field, alignment=Qt.AlignmentFlag.AlignCenter)
        
        btn_login = QPushButton("SIGN IN")
        btn_login.setFixedSize(260, 36)
        btn_login.setStyleSheet("""
            QPushButton {
                background-color: #FF6B57;
                border: none;
                border-radius: 4px;
                color: white;
                font-family: 'Segoe UI';
                font-weight: bold;
            }
            QPushButton:hover { background-color: #ff8170; }
        """)
        btn_login.clicked.connect(self.authenticate_user)
        layout.addWidget(btn_login, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.central_stack.addWidget(self.signin_widget)

    def transition_to_sign_in(self):
        self.central_stack.setCurrentWidget(self.signin_widget)
        self.password_field.setFocus()

    def authenticate_user(self):
        # Verification bypass layer for simple local dev testing
        self.central_stack.setCurrentWidget(self.desktop_area)
        self.setup_background_wallpaper()

    # -------------------------------------------------------------
    # PHASE 3: PRIMARY WORKSPACE DESKTOP SHELL
    # -------------------------------------------------------------
    def build_main_desktop_shell(self):
        self.desktop_layout = QVBoxLayout(self.desktop_area)
        self.desktop_layout.setContentsMargins(0, 0, 0, 0)
        self.desktop_layout.setSpacing(0)
        
        # Workspace Canvas Layout manages Dock panels and windows
        self.workspace_layer = QHBoxLayout()
        self.workspace_layer.setContentsMargins(0, 0, 0, 0)
        self.workspace_layer.setSpacing(0)
        
        # Left Application Side Deck Launcher Navigation Menu
        self.app_launcher_dock = QFrame(self.desktop_area)
        self.app_launcher_dock.setFixedWidth(70)
        self.app_launcher_dock.setStyleSheet("background-color: rgba(20, 20, 20, 0.85); border-right: 1px solid rgba(255,255,255,0.08);")
        
        self.dock_layout = QVBoxLayout(self.app_launcher_dock)
        self.dock_layout.setContentsMargins(10, 20, 10, 20)
        self.dock_layout.setSpacing(15)
        self.dock_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Setup application mount links
        self.add_dock_launcher("file_manager", "📁", "File Explorer", self.launch_file_manager)
        self.add_dock_launcher("settings", "⚙️", "System Settings", self.launch_settings)
        
        # Canvas space where app windows float inside boundaries
        self.window_canvas = QWidget(self.desktop_area)
        self.window_canvas.setStyleSheet("background: transparent;")
        
        self.workspace_layer.addWidget(self.app_launcher_dock)
        self.workspace_layer.addWidget(self.window_canvas, stretch=1)
        self.desktop_layout.addLayout(self.workspace_layer, stretch=1)
        
        # SYSTEM TASKBAR PANEL
        self.taskbar = QFrame(self.desktop_area)
        self.taskbar.setFixedHeight(50)
        self.taskbar.setStyleSheet("background-color: rgba(25, 25, 25, 0.95); border-top: 1px solid rgba(255,255,255,0.06);")
        
        self.taskbar_layout = QHBoxLayout(self.taskbar)
        self.taskbar_layout.setContentsMargins(15, 0, 15, 0)
        
        # Left side panel button collection tracking open frame windows
        self.running_layout = QHBoxLayout()
        self.running_layout.setSpacing(8)
        self.running_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.taskbar_layout.addLayout(self.running_layout, stretch=1)
        
        # Right side System Tray status tracking layout widgets
        self.sys_tray_layout = QHBoxLayout()
        self.sys_tray_layout.setSpacing(12)
        self.sys_tray_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Wi-Fi Controller Module Button
        self.btn_wifi = QPushButton()
        self.btn_wifi.setFixedSize(36, 36)
        self.update_wifi_icon()
        self.btn_wifi.setStyleSheet("QPushButton { background: transparent; border: none; color: white; font-size: 16px; }")
        self.btn_wifi.clicked.connect(self.toggle_wifi_network)
        self.sys_tray_layout.addWidget(self.btn_wifi)
        
        self.taskbar_layout.addLayout(self.sys_tray_layout)
        self.desktop_layout.addWidget(self.taskbar)
        
        self.central_stack.addWidget(self.desktop_area)

    def add_dock_launcher(self, icon_file, fallback_emoji, tool_tip, trigger_func):
        btn = QPushButton(self.app_launcher_dock)
        btn.setFixedSize(50, 50)
        btn.setToolTip(tool_tip)
        
        icon_path = os.path.normpath(os.path.join(self.assets_dir, "icons", f"{icon_file}.png"))
        if os.path.exists(icon_path):
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(28, 28))
        else:
            btn.setText(fallback_emoji)
            btn.setFont(QFont("Segoe UI", 16))
            
        btn.setStyleSheet("""
            QPushButton { background-color: #2c2c2c; border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; color: white; }
            QPushButton:hover { background-color: #FF6B57; border-color: #FF6B57; }
        """)
        btn.clicked.connect(trigger_func)
        self.dock_layout.addWidget(btn)

    # -------------------------------------------------------------
    # FACTORY LIFECYCLE MANAGEMENT HOOKS
    # -------------------------------------------------------------
    def launch_settings(self):
        if not SettingsApp:
            return
        app_instance = SettingsApp(self.window_canvas)
        self.mount_application_frame(app_instance)

    def launch_file_manager(self):
        try:
            from apps.explorer import FileManagerApp
            app_instance = FileManagerApp(self.window_canvas)
            self.mount_application_frame(app_instance)
        except ImportError:
            # Dropdown generic layout container fallback structure
            from desktop.window_frame import DraggableWindowFrame
            fallback = DraggableWindowFrame("File Explorer", self.window_canvas)
            fallback.app_name = "Explorer"
            fallback.icon_name = "file_manager"
            fallback.resize(600, 450)
            self.mount_application_frame(fallback)

    def mount_application_frame(self, app):
        """Standardized lifecycle setup routing application widgets directly onto viewport layers."""
        x = int((self.window_canvas.width() - app.width()) / 2)
        y = int((self.window_canvas.height() - app.height()) / 2)
        app.move(max(15, x), max(15, y))
        
        app.show()
        app.raise_()
        app.activateWindow()
        
        self.running_apps.append(app)
        self.update_taskbar_buttons()

    def update_taskbar_buttons(self):
        """Refreshes and re-renders layout targets based on current operational processes."""
        while self.running_layout.count():
            item = self.running_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.taskbar_buttons.clear()
        
        for app in self.running_apps:
            name = getattr(app, 'app_name', 'Window Core')
            icon_name = getattr(app, 'icon_name', 'default')
            
            btn = QPushButton(self.taskbar)
            btn.setFixedSize(40, 40)
            btn.setToolTip(name)
            
            icon_path = os.path.normpath(os.path.join(self.assets_dir, "icons", f"{icon_name}.png"))
            if os.path.exists(icon_path):
                btn.setIcon(QIcon(icon_path))
                btn.setIconSize(QSize(22, 22))
                btn.setStyleSheet("QPushButton { background-color: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; } QPushButton:hover { border-color: #FF6B57; background-color: rgba(255,255,255,0.12); }")
            else:
                btn.setText(name[0].upper())
                btn.setStyleSheet("QPushButton { color: white; font-weight: bold; background-color: #333333; border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; } QPushButton:hover { border-color: #FF6B57; }")
                
            btn.clicked.connect(lambda checked, target=app: self.handle_window_focus_toggle(target))
            self.running_layout.addWidget(btn)
            self.taskbar_buttons.append(btn)

    def handle_window_focus_toggle(self, app):
        if app.isMinimized():
            app.showNormal()
            app.raise_()
            app.activateWindow()
        else:
            if QApplication.activeWindow() == app or app.isActiveWindow():
                app.showMinimized()
            else:
                app.raise_()
                app.activateWindow()

    # -------------------------------------------------------------
    # SYSTEM TRAY CONTROLLERS
    # -------------------------------------------------------------
    def toggle_wifi_network(self):
        self.wifi_connected = not self.wifi_connected
        self.update_wifi_icon()

    def update_wifi_icon(self):
        wifi_state = "wifi_on" if self.wifi_connected else "wifi_off"
        path = os.path.normpath(os.path.join(self.assets_dir, "icons", f"{wifi_state}.png"))
        if os.path.exists(path):
            self.btn_wifi.setIcon(QIcon(path))
            self.btn_wifi.setIconSize(QSize(22, 22))
            self.btn_wifi.setText("")
        else:
            self.btn_wifi.setIcon(QIcon())
            self.btn_wifi.setText("📶" if self.wifi_connected else "❌")

    def setup_background_wallpaper(self):
        wp_path = os.path.normpath(os.path.join(self.assets_dir, "wallpapers", "wallpaper1.jpg"))
        if os.path.exists(wp_path):
            pixmap = QPixmap(wp_path).scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            palette = QPalette()
            palette.setBrush(QPalette.ColorRole.Window, QBrush(pixmap))
            self.desktop_area.setPalette(palette)
            self.desktop_area.setAutoFillBackground(True)
        else:
            self.desktop_area.setStyleSheet("background-color: #111111;")

    def resizeEvent(self, event):
        if self.central_stack.currentWidget() == self.desktop_area:
            self.setup_background_wallpaper()
        super().resizeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    os_shell = PyFormosoOS()
    os_shell.show()
    sys.exit(app.exec())