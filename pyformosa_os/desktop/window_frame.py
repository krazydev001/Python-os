from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

class DraggableWindowFrame(QWidget):
    """Base window frame component that supports custom frameless dragging and title bars."""
    def __init__(self, title="Application", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        
        self._drag_pos = QPoint()

        # Layout Setup
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Custom Title Bar
        self.title_bar = QWidget(self)
        self.title_bar.setFixedHeight(35)
        self.title_bar.setStyleSheet("background-color: #E8ECEF; border-bottom: 1px solid #DCDCDC;")
        
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)

        self.title_label = QLabel(title, self.title_bar)
        self.title_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #1A1A1A;")
        title_layout.addWidget(self.title_label)

        title_layout.addStretch()

        # Close Button
        close_btn = QPushButton("✕", self.title_bar)
        close_btn.setFixedSize(28, 28)
        close_btn.setStyleSheet("""
            QPushButton { border: none; color: #555; background: transparent; font-size: 12px; }
            QPushButton:hover { background: #E81123; color: white; border-radius: 4px; }
        """)
        close_btn.clicked.connect(self.close)
        title_layout.addWidget(close_btn)

        self.layout.addWidget(self.title_bar)

    # --- DRAG & MOVE LOGIC ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and not self._drag_pos.isNull():
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = QPoint()
        event.accept()