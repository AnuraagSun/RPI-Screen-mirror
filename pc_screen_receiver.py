#!/usr/bin/env python3
"""
Raspberry Pi USB Screen Viewer - PC APPLICATION

This application runs on your PC to receive and display the Raspberry Pi screen.
It connects to the Raspberry Pi through a USB-A to USB-A cable.

Requirements: PyQt5, pyserial, pillow
Install with: pip install PyQt5 pyserial pillow
"""

import sys
import struct
import time
from io import BytesIO
import serial
import serial.tools.list_ports
from PIL import Image, ImageQt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                           QHBoxLayout, QWidget, QPushButton, QComboBox, 
                           QStatusBar, QAction, QMessageBox, QFileDialog,
                           QFrame, QSplashScreen)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QPixmap, QFont, QIcon

class FrameReceiverThread(QThread):
    """Thread to receive frames from the serial connection"""
    frame_received = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    fps_update = pyqtSignal(float)
    
    def __init__(self, port_name, baud_rate=3000000):
        super().__init__()
        self.port_name = port_name
        self.baud_rate = baud_rate
        self.running = False
        self.serial_port = None
    
    def run(self):
        """Main thread loop to receive frames"""
        try:
            self.serial_port = serial.Serial(self.port_name, self.baud_rate, timeout=1)
            self.running = True
            
            frames_received = 0
            start_time = time.time()
            last_fps_update = start_time
            
            while self.running:
                # Read the 4-byte size header (big-endian)
                size_bytes = self.serial_port.read(4)
                if len(size_bytes) < 4:
                    continue
                
                # Unpack the size
                frame_size = struct.unpack('>I', size_bytes)[0]
                
                # Read the JPEG data
                jpeg_data = bytearray()
                remaining = frame_size
                
                while remaining > 0 and self.running:
                    chunk = self.serial_port.read(min(remaining, 4096))
                    if not chunk:
                        break
                    jpeg_data.extend(chunk)
                    remaining -= len(chunk)
                
                if len(jpeg_data) == frame_size:
                    try:
                        # Convert JPEG data to PIL Image
                        image = Image.open(BytesIO(jpeg_data))
                        self.frame_received.emit(image)
                        
                        # Update stats
                        frames_received += 1
                        current_time = time.time()
                        elapsed = current_time - start_time
                        
                        # Update FPS every second
                        if current_time - last_fps_update >= 1.0:
                            fps = frames_received / elapsed
                            self.fps_update.emit(fps)
                            last_fps_update = current_time
                    
                    except Exception as e:
                        self.error_occurred.emit(f"Error processing frame: {str(e)}")
            
        except serial.SerialException as e:
            self.error_occurred.emit(f"Serial error: {str(e)}")
        except Exception as e:
            self.error_occurred.emit(f"Unexpected error: {str(e)}")
        finally:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
    
    def stop(self):
        """Stop the thread safely"""
        self.running = False
        self.wait()

class MainWindow(QMainWindow):
    """Main application window"""
    def __init__(self):
        super().__init__()
        
        self.receiver_thread = None
        self.current_image = None
        self.setWindowTitle("Raspberry Pi USB Screen Viewer")
        self.resize(1280, 720)
        
        # Create UI
        self.init_ui()
        
        # Update available ports
        self.update_port_list()
        
        # Start a timer to periodically refresh ports
        self.port_refresh_timer = QTimer()
        self.port_refresh_timer.timeout.connect(self.update_port_list)
        self.port_refresh_timer.start(5000)  # Refresh every 5 seconds
    
    def init_ui(self):
        """Initialize the user interface"""
        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Create a welcome message when no connection is active
        self.welcome_frame = QFrame()
        welcome_layout = QVBoxLayout(self.welcome_frame)
        
        welcome_label = QLabel("Raspberry Pi USB Screen Viewer")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setFont(QFont("Arial", 20, QFont.Bold))
        
        instructions_label = QLabel(
            "1. Connect your Raspberry Pi to this PC using a USB-A to USB-A cable\n"
            "2. Make sure the Raspberry Pi is running the sender script\n"
            "3. Select the correct USB port below and click 'Start Receiving'"
        )
        instructions_label.setAlignment(Qt.AlignCenter)
        instructions_label.setFont(QFont("Arial", 12))
        
        welcome_layout.addStretch(1)
        welcome_layout.addWidget(welcome_label)
        welcome_layout.addSpacing(20)
        welcome_layout.addWidget(instructions_label)
        welcome_layout.addStretch(1)
        
        # Create display label for the video frames
        self.display_label = QLabel()
        self.display_label.setAlignment(Qt.AlignCenter)
        self.display_label.setMinimumSize(640, 480)
        self.display_label.setStyleSheet("background-color: black;")
        self.display_label.hide()  # Initially hidden
        
        # Add both to the main layout
        main_layout.addWidget(self.welcome_frame)
        main_layout.addWidget(self.display_label)
        
        # Controls frame
        controls_frame = QFrame()
        controls_frame.setFrameShape(QFrame.StyledPanel)
        controls_frame.setFrameShadow(QFrame.Raised)
        controls_layout = QHBoxLayout(controls_frame)
        
        # Port selection dropdown
        port_label = QLabel("USB Port:")
        controls_layout.addWidget(port_label)
        
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(150)
        controls_layout.addWidget(self.port_combo)
        
        # Refresh ports button
        refresh_button = QPushButton("Refresh Ports")
        refresh_button.clicked.connect(self.update_port_list)
        controls_layout.addWidget(refresh_button)
        
        # Start receiving button (renamed from Connect)
        self.connect_button = QPushButton("Start Receiving")
        self.connect_button.setFont(QFont("Arial", 10, QFont.Bold))
        self.connect_button.setMinimumHeight(40)
        self.connect_button.setStyleSheet("background-color: #4CAF50; color: white;")
        self.connect_button.clicked.connect(self.toggle_connection)
        controls_layout.addWidget(self.connect_button)
        
        # Screenshot button
        screenshot_button = QPushButton("Take Screenshot")
        screenshot_button.clicked.connect(self.take_screenshot)
        screenshot_button.setEnabled(False)
        self.screenshot_button = screenshot_button
        controls_layout.addWidget(screenshot_button)
        
        main_layout.addWidget(controls_frame)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add fps label to status bar
        self.fps_label = QLabel("FPS: --")
        self.status_bar.addPermanentWidget(self.fps_label)
        
        # Add connection status to status bar
        self.connection_label = QLabel("Disconnected")
        self.status_bar.addWidget(self.connection_label)
        
        # Create menu bar
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("Help")
        
        # About action
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def update_port_list(self):
        """Update the list of available serial ports"""
        current_port = self.port_combo.currentText()
        
        self.port_combo.clear()
        ports = [port.device for port in serial.tools.list_ports.comports()]
        
        if not ports:
            self.port_combo.addItem("No ports available")
            self.connect_button.setEnabled(False)
        else:
            for port in ports:
                self.port_combo.addItem(port)
            
            # Try to restore the previous selection
            index = self.port_combo.findText(current_port)
            if index >= 0:
                self.port_combo.setCurrentIndex(index)
            
            self.connect_button.setEnabled(True)
    
    def toggle_connection(self):
        """Connect to or disconnect from the selected port"""
        if self.receiver_thread and self.receiver_thread.running:
            self.disconnect_port()
        else:
            self.connect_to_port()
    
    def connect_to_port(self):
        """Connect to the selected serial port"""
        port = self.port_combo.currentText()
        
        if not port or port == "No ports available":
            QMessageBox.warning(self, "Connection Error", "No valid port selected.")
            return
        
        # Create and start receiver thread
        self.receiver_thread = FrameReceiverThread(port)
        self.receiver_thread.frame_received.connect(self.update_frame)
        self.receiver_thread.error_occurred.connect(self.handle_error)
        self.receiver_thread.fps_update.connect(self.update_fps)
        self.receiver_thread.start()
        
        # Update UI
        self.connect_button.setText("Stop Receiving")
        self.connect_button.setStyleSheet("background-color: #F44336; color: white;")
        self.connection_label.setText(f"Connected to {port}")
        self.screenshot_button.setEnabled(True)
        
        # Switch from welcome screen to display
        self.welcome_frame.hide()
        self.display_label.show()
    
    def disconnect_port(self):
        """Disconnect from the serial port"""
        if self.receiver_thread:
            self.receiver_thread.stop()
            self.receiver_thread = None
        
        # Update UI
        self.connect_button.setText("Start Receiving")
        self.connect_button.setStyleSheet("background-color: #4CAF50; color: white;")
        self.connection_label.setText("Disconnected")
        self.fps_label.setText("FPS: --")
        self.screenshot_button.setEnabled(False)
        
        # Switch back to welcome screen
        self.display_label.hide()
        self.welcome_frame.show()
    
    def update_frame(self, image):
        """Update the display with a new frame"""
        self.current_image = image
        
        # Convert PIL image to QPixmap
        qt_image = ImageQt.ImageQt(image)
        pixmap = QPixmap.fromImage(qt_image)
        
        # Scale pixmap to fit the label while maintaining aspect ratio
        pixmap = pixmap.scaled(self.display_label.size(), 
                              Qt.AspectRatioMode.KeepAspectRatio,
                              Qt.TransformationMode.SmoothTransformation)
        
        # Update label
        self.display_label.setPixmap(pixmap)
    
    def update_fps(self, fps):
        """Update the FPS display"""
        self.fps_label.setText(f"FPS: {fps:.1f}")
    
    def handle_error(self, error_message):
        """Handle errors from the receiver thread"""
        self.status_bar.showMessage(error_message, 5000)
        
        # If this is a connection error, disconnect
        if "Serial error" in error_message:
            self.disconnect_port()
    
    def take_screenshot(self):
        """Save the current frame as an image file"""
        if not self.current_image:
            QMessageBox.information(self, "Screenshot", "No image to save.")
            return
        
        # Ask for save location
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Screenshot", "", 
            "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
        )
        
        if file_path:
            try:
                self.current_image.save(file_path)
                self.status_bar.showMessage(f"Screenshot saved to {file_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save screenshot: {str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, 
            "About Raspberry Pi USB Screen Viewer",
            "Raspberry Pi USB Screen Viewer\n\n"
            "This application displays the screen of a Raspberry Pi 4 "
            "over a direct USB connection without using network protocols.\n\n"
            "Connect your Raspberry Pi 4 with a USB-A to USB-A cable "
            "after configuring it in USB gadget mode."
        )
    
    def resizeEvent(self, event):
        """Handle window resize events to maintain aspect ratio"""
        super().resizeEvent(event)
        
        if hasattr(self, 'display_label') and self.display_label.pixmap():
            current_pixmap = self.display_label.pixmap()
            
            scaled_pixmap = current_pixmap.scaled(
                self.display_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            self.display_label.setPixmap(scaled_pixmap)
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.disconnect_port()
        
        if hasattr(self, 'port_refresh_timer'):
            self.port_refresh_timer.stop()
        
        super().closeEvent(event)

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
