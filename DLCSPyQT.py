import sys
import sqlite3
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QDesktopWidget, QPushButton, QTableWidget, QTableWidgetItem, QSizePolicy, QComboBox
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PIL import Image, ImageTk
import numpy as np
from pyzbar.pyzbar import decode

# Common function to establish a database connection and return the connection and cursor
def connect_to_database():
    conn = sqlite3.connect("ilcst.db")
    cursor = conn.cursor()
    return conn, cursor

class UserWindow(QWidget):
    # Define a custom closed signal
    closed = pyqtSignal()

    def __init__(self, data):
        super().__init__()

        self.setWindowTitle("Contact Us")
        self.setGeometry(100, 100, 800, 600)

        # Disable the minimize button
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)

        # Create a vertical layout for the user window
        user_layout = QVBoxLayout()

        # Create a container widget for the table
        table_container = QWidget()
        table_layout = QVBoxLayout()
        table_container.setLayout(table_layout)

        # Create a table widget to display user data
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["CPF No", "Name", "Phone Number"])
        table.setRowCount(len(data))

        for row, item in enumerate(data):
            for col, value in enumerate(item):
                table.setItem(row, col, QTableWidgetItem(str(value)))

        # Add the table widget to the container layout
        table_layout.addWidget(table)

        # Add the container widget to the user layout
        user_layout.addWidget(table_container)

        # Create a close button at the bottom
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        user_layout.addWidget(close_button, alignment=Qt.AlignCenter)

        self.setLayout(user_layout)

    def closeEvent(self, event):
        self.closed.emit()  # Emit the custom closed signal when the window is closed

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Line Clearance System")

        # Set window size to fit the maximum size of any screen
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, screen.width(), screen.height())

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a vertical layout for the central widget
        central_layout = QVBoxLayout()
        central_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins

        # Set background color of the header to blue
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: blue;")

        # First row (header)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins

        # Add logo to the left side
        logo_label = QLabel(self)
        pixmap = QPixmap("nlclogo.png")
        logo_height = 100
        logo_label.setPixmap(pixmap.scaledToHeight(logo_height))
        logo_label.setAlignment(Qt.AlignLeft)  # Align the logo to the left
        header_layout.addWidget(logo_label)

        # Create a spacer to push the title to the center
        title_spacer = QWidget()
        title_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        header_layout.addWidget(title_spacer)

        # Create a vertical layout for the title and center it
        title_layout = QVBoxLayout()
        title_layout.setAlignment(Qt.AlignCenter)

        # Add header title with an increased font size
        heading_label = QLabel("DIGITALIZED LINE CLEARANCE SYSTEM")
        header_font = QFont("Arial", 27)
        header_font.setBold(True)
        heading_label.setFont(header_font)
        heading_label.setStyleSheet("color: white;")
        title_layout.addWidget(heading_label)

        # Set the title layout as the central layout for the title spacer
        title_spacer.setLayout(title_layout)

        # Add the first row (header) to the central layout
        header_widget.setLayout(header_layout)
        central_layout.addWidget(header_widget)

        # Second row (subtitle)
        subtitle_label = QLabel("M-1A Substation")
        subtitle_font = QFont("Arial", 20)
        subtitle_font.setBold(True)
        subtitle_label.setFont(subtitle_font) # Set font size for the subtitle
        subtitle_label.setAlignment(Qt.AlignCenter)  # Center align the subtitle
        subtitle_label.setStyleSheet("color: white;")
        title_layout.addWidget(subtitle_label, alignment=Qt.AlignCenter)  # Center align the subtitle

        # Create a button to open the user window
        self.user_window = None  # Store the UserWindow as an instance variable
        contact_button = QPushButton("Contact Us")
        contact_button.setStyleSheet("background-color: white; padding: 5px 8px; font-size: 14px;")
        contact_button.clicked.connect(self.show_user_window)
        header_layout.addWidget(contact_button, alignment=Qt.AlignCenter)

        # Add the "SELECT FEEDER" subtitle
        feeder_label = QLabel("SELECT FEEDER")
        feeder_font = QFont("Arial", 14)
        feeder_font.setBold(True)
        feeder_label.setFont(feeder_font)
        feeder_label.setAlignment(Qt.AlignCenter)
        feeder_label.setStyleSheet("color: Red;")
        central_layout.addWidget(feeder_label)

        # Add a ComboBox for feeders populated from the database
        feeder_combo = QComboBox()
        feeder_combo.setStyleSheet("font-size: 14px;")

        # Connect to the SQLite database
        conn, cursor = connect_to_database()

        # Execute the query to fetch feeder numbers from the database
        data = ("MINE-1A",)
        cursor.execute("SELECT number FROM feeders WHERE unit=?", data)
        row = cursor.fetchone()
        feederCount = row[0]

        for i in range(feederCount):
            feeder_combo.addItem("Feeder-" + str(i + 1))

        # Close the database connection
        conn.close()
        central_layout.addWidget(feeder_combo, alignment=Qt.AlignCenter)
        # Set the central layout for the central widget
        central_widget.setLayout(central_layout)

        # Create a label for displaying the camera feed
        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignCenter)
        central_layout.addWidget(self.camera_label)

        # Create a QTimer for updating the camera feed
        self.camera_timer = QTimer(self)
        self.camera_timer.timeout.connect(self.update_camera_feed)

        submit_button = QPushButton("Submit")
        submit_button.setStyleSheet("background-color: blue; padding: 5px 8px; font-size: 14px;")
        submit_button.clicked.connect(self.start_camera_feed)
        central_layout.addWidget(submit_button, alignment=Qt.AlignCenter)

        # Create a table to display feeder data
        self.feeder_table = QTableWidget()
        self.feeder_table.setColumnCount(2)
        self.feeder_table.setHorizontalHeaderLabels(["Feeder No", "Names"])

        # Adjust the alignment of the table to top-right
        table_widget = QWidget()
        table_layout = QVBoxLayout()
        table_layout.addWidget(self.feeder_table, alignment=Qt.AlignTop | Qt.AlignRight)
        table_widget.setLayout(table_layout)
        central_layout.addWidget(table_widget, alignment=Qt.AlignTop | Qt.AlignRight)

        # Connect the ComboBox's currentIndexChanged signal to a function that loads feeder data
        feeder_combo.currentIndexChanged.connect(self.load_feeder_data)

        # Add a stretch to push the second row to the bottom
        central_layout.addStretch(1)

    def load_feeder_data(self):
        feeder_number = self.sender().currentText()

        # Connect to the SQLite database
        conn, cursor = connect_to_database()

        # Execute the query to fetch feeder data based on the selected feeder number
        cursor.execute("SELECT feeder_no, names FROM feeder_data WHERE feeder_no=?", (feeder_number,))
        data = cursor.fetchall()

        # Close the database connection
        conn.close()

        # Clear existing table data
        self.feeder_table.setRowCount(0)

        # Populate the table with the fetched data
        for row_num, (feeder_no, names) in enumerate(data):
            self.feeder_table.insertRow(row_num)
            self.feeder_table.setItem(row_num, 0, QTableWidgetItem(str(feeder_no)))
            self.feeder_table.setItem(row_num, 1, QTableWidgetItem(names))

    def show_user_window(self):
        if self.user_window is None or not self.user_window.isVisible():
            # Connect to the SQLite database
            conn, cursor = connect_to_database()

            # Execute the query to fetch user data
            query = "SELECT cpf_no, name, phone_no FROM users"
            cursor.execute(query)

            # Fetch all rows from the query result
            data = cursor.fetchall()

            # Close the database connection
            conn.close()

            # Create and show the user window with the fetched data
            self.user_window = UserWindow(data)
            self.user_window.show()
            self.user_window.closed.connect(self.on_user_window_closed)  # Connect to a custom signal
            
    def show_frames(label, selectedFeeder):
        global camera_running, cap
        cap = cv2.VideoCapture(0)


    def detect_and_display_qr_codes():
        ret, frame = cap.read()
        if not ret:
            return
        # Convert the frame to grayscale for QR code detection
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect QR codes
        decoded_objects = decode(frame)
        for obj in decoded_objects:
            qr_data = obj.data.decode('utf-8')
            points = obj.polygon
            if len(points) >= 4:
                # Draw a border around the QR code
                cv2.polylines(frame, [np.array(points)], True, (0, 255, 0), 2)

                # Display QR code data
                cv2.putText(frame, qr_data, (points[0][0], points[0][1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    def on_user_window_closed(self):
        self.user_window = None  # Set user_window to None when the window is closed

    def start_camera_feed(self):
        self.camera = cv2.VideoCapture(0)  # Open the default camera (0)
        # Start the camera feed timer (update at 30 frames per second)
        self.camera_timer.start(33)  # 1000 ms / 30 fps = 33 ms per frame

    def update_camera_feed(self):
        ret, frame = self.camera.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            self.camera_label.setPixmap(pixmap)
            self.camera_label.setScaledContents(True)

    def closeEvent(self, event):
        # Release the camera and stop the timer when closing the application
        if hasattr(self, 'camera'):
            self.camera.release()
        self.camera_timer.stop()
        super().closeEvent(event)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
