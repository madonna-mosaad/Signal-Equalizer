from PyQt5 import QtCore, QtGui, QtWidgets

# Define color constants for easy customization
BACKGROUND_COLOR = "rgb(111, 166, 195)"
BUTTON_COLOR = "rgb(255, 255, 255)"
TEXT_COLOR = "rgb(42, 66, 79)"
HOVER_COLOR = "rgb(240, 240, 240)"

# Stylesheets for components
BUTTON_STYLESHEET = f"""
QPushButton {{
    border: none;
    padding: 10px;
    color: {TEXT_COLOR};
    background-color: {BUTTON_COLOR};
    border-bottom: 2px solid transparent;
    border-radius: 8px;
}}
QPushButton:hover {{
    background-color: {HOVER_COLOR};
}}
"""
SLIDER_STYLESHEET = """
QSlider::groove:horizontal {
    border: 1px solid #999999;
    height: 2px;
    background: #dddddd;
    margin: 2px 0;
}
QSlider::handle:horizontal {
    background: rgb(42, 66, 79);  /* Handle color */
    border: 1px solid #5c5c5c;
    width: 16px;
    margin: -10px 0;
    border-radius: 3px;
}
QSlider::sub-page:horizontal {
    background: rgb(42, 132, 161);  /* Filled color */
    border: 1px solid #4A708B;
    height: 1px;
    border-radius: 2px;
}
"""


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1280, 800)
        MainWindow.setFont(self.get_font("Times New Roman"))
        MainWindow.setStyleSheet(f"background-color: {BACKGROUND_COLOR}; color: white;")

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Title Bar
        self.setup_title_bar()

        # Top Control Bar
        self.setup_top_control_bar()

        # Graph Display Area
        self.setup_graph_display_area()

        # Right Control Panel
        self.setup_right_control_panel()

        # Playback Controls
        self.setup_playback_controls()

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def get_font(self, family: str, size: int = None) -> QtGui.QFont:
        font = QtGui.QFont()
        font.setFamily(family)
        if size:
            font.setPointSize(size)
        return font

    def create_button(self, parent: QtWidgets.QWidget, text: str) -> QtWidgets.QPushButton:
        button = QtWidgets.QPushButton(text, parent)
        button.setMaximumSize(QtCore.QSize(140, 40))
        button.setFont(self.get_font("Times New Roman"))
        button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        button.setStyleSheet(BUTTON_STYLESHEET)
        return button

    def setup_title_bar(self) -> None:
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(10, 10, 291, 52))

        self.title_layout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.title_layout.setContentsMargins(0, 0, 0, 0)

        self.title_icon = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.title_icon.setMaximumSize(QtCore.QSize(40, 40))
        self.title_icon.setPixmap(QtGui.QPixmap("src/title_icon.png"))
        self.title_icon.setScaledContents(True)
        self.title_layout.addWidget(self.title_icon)

        self.title_name = QtWidgets.QLabel("Signal Equalizer", self.horizontalLayoutWidget_2)
        self.title_name.setMaximumSize(QtCore.QSize(220, 40))
        self.title_name.setFont(self.get_font("Times New Roman", 22))
        self.title_name.setAlignment(QtCore.Qt.AlignCenter)
        self.title_layout.addWidget(self.title_name)

    def setup_top_control_bar(self) -> None:
        self.horizontalLayoutWidget_4 = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget_4.setGeometry(QtCore.QRect(800, 10, 471, 51))

        self.top_control_layout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_4)
        self.top_control_layout.setContentsMargins(0, 0, 0, 0)

        self.toggle_mode_button = self.create_button(self.horizontalLayoutWidget_4, "Uniform Range")
        self.upload_signal_button = self.create_button(self.horizontalLayoutWidget_4, "Upload Signal")
        self.quit_app_button = self.create_button(self.horizontalLayoutWidget_4, "Quit Application")
        self.quit_app_button.clicked.connect(QtWidgets.QApplication.quit)

        for button in [self.toggle_mode_button, self.upload_signal_button, self.quit_app_button]:
            self.top_control_layout.addWidget(button)

    def setup_graph_display_area(self) -> None:
        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 60, 1110, 720))

        self.graphs_container = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.graphs_container.setContentsMargins(0, 0, 0, 0)

        # Creating containers with self variables
        self.input_cine_container = self.add_graph_container("Input Cine", 0, 0)
        self.frequency_domain_container = self.add_graph_container("Frequency Domain", 0, 1)
        self.output_cine_container = self.add_graph_container("Output Cine", 1, 0, colspan=2, width=1100)
        self.input_spectrogram_container = self.add_graph_container("Input Spectrogram", 3, 0)
        self.output_spectrogram_container = self.add_graph_container("Output Spectrogram", 3, 1)

    def add_graph_container(self, title: str, row: int, col: int, colspan: int = 1, width: int = 535,
                            height: int = 165) -> QtWidgets.QGroupBox:
        container = QtWidgets.QGroupBox(title, self.gridLayoutWidget)

        # Create a layout for the container and set it
        container_layout = QtWidgets.QVBoxLayout(container)
        container.setLayout(container_layout)  # Assign the layout to the container

        # Set size based on width and height parameters
        container_widget = QtWidgets.QWidget(container)
        container_widget.setGeometry(QtCore.QRect(5, 30, width, height))
        container_widget.setStyleSheet("background-color:rgba(1, 1, 1, 0);")

        # Add container to the layout
        self.graphs_container.addWidget(container, row, col, 1, colspan)

        return container

    def setup_right_control_panel(self) -> None:
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(1130, 80, 141, 671))

        self.right_control_layout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.right_control_layout.setContentsMargins(0, 0, 0, 0)

        self.button = self.create_button(self.verticalLayoutWidget, f"Adjust Band 5")
        self.right_control_layout.addWidget(self.button)
        self.button.setVisible(False)

        # Equalizer sliders and labels (hidden initially)
        self.equalizer_sliders = []
        self.equalizer_labels = []

        for i in range(10):
            label = QtWidgets.QLabel(f"Slider {i + 1}", self.verticalLayoutWidget)
            label.setFont(self.get_font("Times New Roman"))

            self.right_control_layout.addWidget(label)

            slider = QtWidgets.QSlider(self.verticalLayoutWidget)
            slider.setOrientation(QtCore.Qt.Horizontal)
            slider.setMaximum(100)
            slider.setFixedHeight(25)
            slider.setMinimum(0)
            slider.setValue(100)
            slider.setStyleSheet(SLIDER_STYLESHEET)
            self.right_control_layout.addWidget(slider)

            self.equalizer_sliders.append(slider)
            self.equalizer_labels.append(label)

    def setup_playback_controls(self) -> None:
        self.playback_controls = QtWidgets.QGroupBox("Playback Controls", self.gridLayoutWidget)
        self.playback_controls.setMaximumSize(QtCore.QSize(16777215, 84))

        self.horizontalLayoutWidget = QtWidgets.QWidget(self.playback_controls)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 20, 1071, 61))

        self.playback_layout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.playback_layout.setContentsMargins(0, 0, 0, 0)

        self.play_pause_button = self.create_button(self.horizontalLayoutWidget, "Play")
        self.stop_button = self.create_button(self.horizontalLayoutWidget, "Stop")
        self.reset_button = self.create_button(self.horizontalLayoutWidget, "Reset")
        self.speed_button = self.create_button(self.horizontalLayoutWidget, "1X")
        self.toggle_spectrogram_button = self.create_button(self.horizontalLayoutWidget, "Hide Spectrogram")
        self.toggle_scale_button = self.create_button(self.horizontalLayoutWidget, "Scale Toggle")

        for button in [self.play_pause_button, self.stop_button, self.reset_button, self.speed_button,
                       self.toggle_spectrogram_button, self.toggle_scale_button]:
            self.playback_layout.addWidget(button)

        self.graphs_container.addWidget(self.playback_controls, 2, 0, 1, 2)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("Signal Equalizer")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.showFullScreen()
    sys.exit(app.exec_())
