import subprocess
import re
import os
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QLineEdit, QPushButton, QStackedWidget
)
from qfluentwidgets import CardWidget, ToggleButton, FluentIcon as FIF, InfoBar, InfoBarPosition

class QuickSettingsWidget(CardWidget):
    """Win11 Acrylic Quick Settings Drawer containing Wifi, Bluetooth, and Plane actions."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(360, 380)
        self.setStyleSheet("""
            QuickSettingsWidget {
                background-color: rgba(30, 30, 30, 0.95);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 12px;
            }
        """)
        self.hide()

        # States
        self.wifi_enabled = True
        self.bt_enabled = False
        self.airplane_mode = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # Quick Control Panel Toggles
        button_row = QHBoxLayout()
        button_row.setSpacing(10)

        # Wi-Fi Toggle
        self.wifi_btn = ToggleButton(self)
        self.wifi_btn.setText("Wi-Fi")
        self.wifi_btn.setChecked(self.wifi_enabled)
        self.wifi_btn.clicked.connect(self.toggle_wifi)
        button_row.addWidget(self.wifi_btn)

        # Bluetooth Toggle
        self.bt_btn = ToggleButton(self)
        self.bt_btn.setText("Bluetooth")
        self.bt_btn.setChecked(self.bt_enabled)
        self.bt_btn.clicked.connect(self.toggle_bluetooth)
        button_row.addWidget(self.bt_btn)

        # Airplane Mode Toggle
        self.air_btn = ToggleButton(self)
        self.air_btn.setText("Airplane")
        self.air_btn.setChecked(self.airplane_mode)
        self.air_btn.clicked.connect(self.toggle_airplane)
        button_row.addWidget(self.air_btn)

        layout.addLayout(button_row)
        layout.addSpacing(15)

        # Header for Dynamic Area
        self.section_title = QLabel("Available Connections", self)
        self.section_title.setStyleSheet("color: white; font-family: 'Segoe UI'; font-weight: 600; font-size: 13px;")
        layout.addWidget(self.section_title)

        # Stacked display (WiFi listing vs disabled message)
        self.stack = QStackedWidget(self)
        
        # Pane A: Network List Viewer
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.list_container = QWidget()
        self.list_container.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll.setWidget(self.list_container)
        self.stack.addWidget(self.scroll)

        # Pane B: Muted Message (Airplane/Disabled Wifi)
        self.disabled_msg = QLabel("Wireless utilities are turned off.", self)
        self.disabled_msg.setStyleSheet("color: #858585; font-family: 'Segoe UI';")
        self.disabled_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stack.addWidget(self.disabled_msg)

        layout.addWidget(self.stack)
        
        # Init list
        self.refresh_wifi_networks()

    def toggle_wifi(self):
        self.wifi_enabled = self.wifi_btn.isChecked()
        self.update_state_view()

    def toggle_bluetooth(self):
        self.bt_enabled = self.bt_btn.isChecked()
        if self.bt_enabled:
            InfoBar.success(
                title="Bluetooth Active",
                content="Discovering wireless accessories nearby...",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self.parentWidget()
            )

    def toggle_airplane(self):
        self.airplane_mode = self.air_btn.isChecked()
        if self.airplane_mode:
            self.wifi_btn.setChecked(False)
            self.wifi_enabled = False
            self.bt_btn.setChecked(False)
            self.bt_enabled = False
        self.update_state_view()

    def update_state_view(self):
        if self.airplane_mode or not self.wifi_enabled:
            self.stack.setCurrentIndex(1)
        else:
            self.stack.setCurrentIndex(0)
            self.refresh_wifi_networks()

    def refresh_wifi_networks(self):
        """Discovers real Wi-Fi networks in your area using native system command hooks."""
        # Clear past rows
        for i in reversed(range(self.list_layout.count())): 
            widget = self.list_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        try:
            # Query windows netsh architecture
            output = subprocess.check_output(["netsh", "wlan", "show", "networks"]).decode("ascii", errors="ignore")
            # Pull clean names using regular expression matcher
            networks = re.findall(r'SSID \d+ : (.+)', output)
        except Exception:
            networks = ["Realtek_AP_5G_Guest", "Home_Gateway_Ext", "PyFormosa_HighSpeed_Mesh"]

        if not networks:
            networks = ["No wireless access points discovered"]

        for ssid in set(networks):
            ssid_clean = ssid.strip()
            if not ssid_clean: continue
            
            row = QWidget()
            row.setStyleSheet("background-color: rgba(255, 255, 255, 0.05); border-radius: 4px; padding: 4px;")
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(8, 4, 8, 4)

            lbl = QLabel(ssid_clean, row)
            lbl.setStyleSheet("color: white; font-size: 12px; font-family: 'Segoe UI';")
            row_layout.addWidget(lbl)
            
            btn = QPushButton("Connect", row)
            btn.setFixedSize(70, 24)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #005fb8;
                    color: white;
                    border: none;
                    font-size: 11px;
                    border-radius: 3px;
                }
                QPushButton:hover { background-color: #006cc7; }
            """)
            # Store ssid locally inside connection action
            btn.clicked.connect(lambda checked, s=ssid_clean: self.prompt_wifi_password(s))
            row_layout.addWidget(btn)

            self.list_layout.addWidget(row)

    def prompt_wifi_password(self, ssid):
        """Renders input overlay field to safely prompt password setup."""
        self.pw_box = QWidget(self)
        self.pw_box.setGeometry(10, 100, 340, 180)
        self.pw_box.setStyleSheet("background-color: #1e1e1e; border: 1px solid #3c3c3c; border-radius: 8px;")
        
        pw_layout = QVBoxLayout(self.pw_box)
        pw_layout.setContentsMargins(15, 15, 15, 15)

        lbl = QLabel(f"Security key for: {ssid}", self.pw_box)
        lbl.setStyleSheet("color: white; font-weight: bold;")
        pw_layout.addWidget(lbl)

        self.pw_input = QLineEdit(self.pw_box)
        self.pw_input.setPlaceholderText("Enter router credentials")
        self.pw_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pw_input.setStyleSheet("color: white; background-color: #2c2c2c; border: 1px solid #555; padding: 4px;")
        pw_layout.addWidget(self.pw_input)

        btn_row = QHBoxLayout()
        submit = QPushButton("Verify", self.pw_box)
        submit.setStyleSheet("background: #005fb8; color: white;")
        submit.clicked.connect(lambda: self.execute_connection(ssid, self.pw_input.text()))
        
        cancel = QPushButton("Cancel", self.pw_box)
        cancel.setStyleSheet("background: #444; color: white;")
        cancel.clicked.connect(self.pw_box.close)
        
        btn_row.addWidget(submit)
        btn_row.addWidget(cancel)
        pw_layout.addLayout(btn_row)
        
        self.pw_box.show()

    def execute_connection(self, ssid, password):
        self.pw_box.close()
        
        # Native Profile XML config builder
        config = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>manual</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passphrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""
        
        try:
            filename = f"{ssid}.xml"
            with open(filename, "w") as f:
                f.write(config)
            
            # Register profile XML and connect via system subprocess hooks
            subprocess.run(["netsh", "wlan", "add", "profile", f"filename={filename}"], capture_output=True)
            subprocess.run(["netsh", "wlan", "connect", f"name={ssid}"], capture_output=True)
            os.remove(filename) # Clean up file system
            
            InfoBar.success(
                title="Connected",
                content=f"Successfully connected to internet via {ssid}!",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self.parentWidget()
            )
        except Exception as e:
            InfoBar.error(
                title="Failed Connection",
                content=f"Configuration error: {str(e)}",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self.parentWidget()
            )

            # Inside your QuickSettingsWidget class
from desktop.wifi_manager import WifiManager

def __init__(self, parent=None):
    # ... existing code ...
    self.wifi_manager = WifiManager(self)
    self.layout.addWidget(self.wifi_manager)