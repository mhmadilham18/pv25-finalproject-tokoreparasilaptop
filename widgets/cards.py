from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


class CardWidget(QWidget):
    def __init__(self, title, value, icon_path=None):
        super().__init__()
        self.init_ui(title, value, icon_path)

    def init_ui(self, title, value, icon_path):
        main_layout = QHBoxLayout(self)

        container = QWidget()
        container.setObjectName("cardContainer")

        container_layout = QHBoxLayout(container)
        container_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        container_layout.setContentsMargins(25, 25, 25, 25)

        if icon_path:
            icon_label = QLabel()
            pixmap = QPixmap(icon_path).scaled(52, 52, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
            container_layout.addWidget(icon_label)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("cardTitleLabel")
        self.value_label = QLabel(value)
        self.value_label.setObjectName("cardValueLabel")

        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.value_label)

        container_layout.addSpacing(15)
        container_layout.addLayout(text_layout)
        main_layout.addWidget(container)

    def update_value(self, new_value):
        self.value_label.setText(str(new_value))