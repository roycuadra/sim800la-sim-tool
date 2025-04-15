import sys
import serial
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QVBoxLayout, QMessageBox
)

class SmsSender(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.port = 'COM4'  # <-- Change this to match your port
        self.ser = serial.Serial(self.port, baudrate=9600, timeout=1)

    def initUI(self):
        self.setWindowTitle("SIM800LA SMS Tool")

        self.label_number = QLabel("Phone Number:")
        self.input_number = QLineEdit()
        self.input_number.setPlaceholderText("+639123456789")

        self.label_message = QLabel("Message:")
        self.input_message = QTextEdit()

        self.btn_send = QPushButton("Send SMS")
        self.btn_send.clicked.connect(self.send_sms)

        self.btn_read = QPushButton("📥 Read SMS")
        self.btn_read.clicked.connect(self.read_sms)

        self.log = QTextEdit()
        self.log.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.label_number)
        layout.addWidget(self.input_number)
        layout.addWidget(self.label_message)
        layout.addWidget(self.input_message)
        layout.addWidget(self.btn_send)
        layout.addWidget(self.btn_read)
        layout.addWidget(self.log)

        self.setLayout(layout)
        self.resize(450, 500)

    def send_at(self, command, delay=1):
        self.ser.write((command + '\r').encode())
        time.sleep(delay)
        reply = self.ser.read_all().decode(errors='ignore')
        self.log.append(f"> {command}\n{reply}")
        return reply

    def send_sms(self):
        number = self.input_number.text().strip()
        message = self.input_message.toPlainText().strip()

        if not number or not message:
            QMessageBox.warning(self, "Input Error", "Please enter both phone number and message.")
            return

        try:
            self.log.append("Sending SMS...\n")
            self.send_at("AT")
            self.send_at("AT+CMGF=1")  # Text mode
            self.send_at(f'AT+CMGS="{number}"')
            time.sleep(2)
            self.ser.write((message + chr(26)).encode())  # Ctrl+Z
            time.sleep(3)
            self.log.append("✅ SMS Sent!\n")
        except Exception as e:
            self.log.append(f"❌ Error: {str(e)}")

    def read_sms(self):
        try:
            self.log.append("📥 Reading all SMS...\n")
            self.send_at("AT")
            self.send_at("AT+CMGF=1")  # Text mode
            response = self.send_at('AT+CMGL="ALL"', delay=3)
            self.log.append("📲 Messages:\n" + response)
        except Exception as e:
            self.log.append(f"❌ Error reading SMS: {str(e)}")

    def closeEvent(self, event):
        try:
            self.ser.close()
        except:
            pass
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SmsSender()
    window.show()
    sys.exit(app.exec_())
