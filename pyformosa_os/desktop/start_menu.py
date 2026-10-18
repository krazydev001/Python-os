from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from qfluentwidgets import SimpleCardWidget

class StartMenuWidget(SimpleCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(540, 600)
        self.hide()
        
        self.setStyleSheet("""
            StartMenuWidget {
                background-color: rgba(30, 30, 30, 0.92);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(self)
        lbl = QLabel("Pinned Apps", self)
        lbl.setStyleSheet("color: white; font-family: 'Segoe UI'; font-size: 14px;")
        layout.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignTop)

    def animate_slide_up(self, target_x, target_y):
        self.move(target_x, target_y + 40)
        self.show()
        self.raise_()
        
        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(250)
        self.anim.setStartValue(self.pos())
        self.anim.setEndValue(Qt.QPoint(target_x, target_y))
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()