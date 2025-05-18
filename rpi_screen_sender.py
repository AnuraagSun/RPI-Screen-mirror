#!/usr/bin/env python3
"""
Raspberry Pi USB Screen Sender - RASPBERRY PI APPLICATION

This application runs on your Raspberry Pi to capture and send screen frames
over USB to your PC. It must be run on the Raspberry Pi, not on your PC.

Requirements: pyserial, PIL, mss (optional)
Install with: pip3 install pyserial pillow mss
"""

import os
import sys
import time
import struct
import threading
from io import BytesIO
import serial
from PIL import Image

# Try to import Tkinter for GUI
try:
    if sys.version_info.major >= 3:
        import tkinter as tk
        from tkinter import ttk, messagebox
    else:
        import Tkinter as tk
        import ttkmessagebox
    HAS_TKINTER = True
except ImportError:
    HAS_TKINTER = False

# Try to import mss for screen capture
try:
    import mss
    USE_MSS = True
except ImportError:
    USE_MSS = False
    # Fallback to framebuffer capture
    FB_DEVICE = '/dev/fb0'

# Configuration
SERIAL_PORT = '/dev/ttyGS0'
CAPTURE_WIDTH = 1280
CAPTURE_HEIGHT = 720
JPEG_QUALITY = 60
TARGET_FPS = 15
FRAME_INTERVAL = 1.0 / TARGET_FPS

class ScreenSender:
    """Class for handling screen capture and sending"""
    def __init__(self, gui=None):
        self.running = False
        self.thread = None
        self.gui = gui
        self.frames_sent = 0
        self.start_time = 0
    
    def capture_screen_mss(self):
        """Capture screen using mss library"""
        with mss.mss() as sct:
            monitor = sct.monitors[0]  # Capture the main screen
            sct_img = sct.grab(monitor)
            # Convert to PIL Image
            return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

    def capture_screen_framebuffer(self):
        """Capture screen using direct framebuffer access"""
        with open(FB_DEVICE, 'rb') as fb:
            fb_bytes = fb.read(CAPTURE_WIDTH * CAPTURE_HEIGHT * 4)  # Assuming 32-bit color depth
        
        # Convert framebuffer data to PIL Image
        img = Image.frombytes('RGBA', (CAPTURE_WIDTH, CAPTURE_HEIGHT), fb_bytes)
        return img.convert('RGB')

    def compress_and_send_frame(self, serial_conn, image):
        """Compress image to JPEG and send over serial with length prefix"""
        # Resize image if needed
        if image.width != CAPTURE_WIDTH or image.height != CAPTURE_HEIGHT:
            image = image.resize((CAPTURE_WIDTH, CAPTURE_HEIGHT))
        
        # Compress as JPEG
        buffer = BytesIO()
        image.save(buffer, format='JPEG', quality=JPEG_QUALITY)
        jpeg_bytes = buffer.getvalue()
        
        # Get the size of the JPEG data
        data_size = len(jpeg_bytes)
        
        # Send the size as a 4-byte big-endian integer
        size_bytes = struct.pack('>I', data_size)
        serial_conn.write(size_bytes)
        
        # Send the JPEG data
        serial_conn.write(jpeg_bytes)
        serial_conn.flush()
        
        return data_size

    def sender_loop(self):
        """Main sender loop function"""
        print("Starting Raspberry Pi screen capture and streaming...")
        
        # Initialize serial connection
        try:
            ser = serial.Serial(SERIAL_PORT, baudrate=3000000)  # High baudrate for performance
            print(f"Connected to {SERIAL_PORT}")
        except serial.SerialException as e:
            error_msg = f"Error opening serial port: {e}"
            print(error_msg)
            print("Make sure USB gadget mode is configured properly")
            if self.gui:
                self.gui.update_status(error_msg, "red")
            return
        
        self.frames_sent = 0
        self.start_time = time.time()
        
        try:
            while self.running:
                frame_start = time.time()
                
                # Capture screen
                if USE_MSS:
                    image = self.capture_screen_mss()
                else:
                    image = self.capture_screen_framebuffer()
                
                # Send the frame
                bytes_sent = self.compress_and_send_frame(ser, image)
                
                self.frames_sent += 1
                elapsed = time.time() - self.start_time
                
                if self.frames_sent % 30 == 0:
                    status_msg = f"Sent {self.frames_sent} frames in {elapsed:.2f}s - Avg FPS: {self.frames_sent/elapsed:.2f}"
                    print(status_msg)
                    print(f"Last frame size: {bytes_sent/1024:.2f} KB")
                    if self.gui:
                        self.gui.update_status(status_msg)
                
                # Calculate sleep time to maintain target FPS
                process_time = time.time() - frame_start
                sleep_time = max(0, FRAME_INTERVAL - process_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)
        
        except Exception as e:
            error_msg = f"Error during streaming: {e}"
            print(error_msg)
            if self.gui:
                self.gui.update_status(error_msg, "red")
        finally:
            if 'ser' in locals() and ser.is_open:
                ser.close()
                print("Serial connection closed")
            self.running = False
            if self.gui:
                self.gui.update_button_state()
    
    def start(self):
        """Start the sender thread"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self.sender_loop)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        """Stop the sender thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None

class SenderGUI:
    """GUI for screen sender"""
    def __init__(self, root):
        self.root = root
        self.root.title("Raspberry Pi USB Screen Sender")
        self.root.geometry("500x400")
        
        self.sender = ScreenSender(self)
        
        self.create_widgets()

    def create_widgets(self):
        """Create GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Raspberry Pi USB Screen Sender",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status")
        status_frame.pack(fill=tk.X, pady=10)
        
        self.status_label = ttk.Label(
            status_frame, 
            text="Ready to start sending screen",
            font=("Arial", 10)
        )
        self.status_label.pack(pady=10)
        
        # Device info
        info_frame = ttk.LabelFrame(main_frame, text="Device Information")
        info_frame.pack(fill=tk.X, pady=10)
        
        # Try to get system info
        try:
            import socket
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
        except:
            hostname = "Unknown"
            ip = "Unknown"
        
        info_text = f"Hostname: {hostname}\n"
        info_text += f"USB Serial Device: {SERIAL_PORT}\n"
        info_text += f"Resolution: {CAPTURE_WIDTH}x{CAPTURE_HEIGHT}\n"
        info_text += f"Target FPS: {TARGET_FPS}"
        
        info_label = ttk.Label(info_frame, text=info_text)
        info_label.pack(pady=10)
        
        # Instructions
        instruction_frame = ttk.LabelFrame(main_frame, text="Instructions")
        instruction_frame.pack(fill=tk.X, pady=10)
        
        instructions = (
            "1. Make sure your Raspberry Pi is connected to your PC via USB\n"
            "2. Make sure USB gadget mode is configured correctly\n"
            "3. Run the receiver app on your PC\n"
            "4. Click 'Start Sending' below"
        )
        
        instruction_label = ttk.Label(instruction_frame, text=instructions)
        instruction_label.pack(pady=10)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        style = ttk.Style()
        style.configure("Green.TButton", foreground="white", background="green")
        
        self.start_button = ttk.Button(
            button_frame,
            text="Start Sending",
            command=self.toggle_sending,
            style="Green.TButton",
            width=20
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        exit_button = ttk.Button(
            button_frame,
            text="Exit",
            command=self.on_exit,
            width=10
        )
        exit_button.pack(side=tk.LEFT, padx=5)
    
    def toggle_sending(self):
        """Toggle sending state"""
        if self.sender.running:
            self.sender.stop()
            self.update_status("Stopped sending", "black")
        else:
            self.sender.start()
            self.update_status("Starting sender...", "blue")
    
    def update_button_state(self):
        """Update button text based on sender state"""
        if self.sender.running:
            self.start_button.config(text="Stop Sending")
        else:
            self.start_button.config(text="Start Sending")
    
    def update_status(self, message, color="black"):
        """Update status label"""
        self.status_label.config(text=message, foreground=color)
        self.update_button_state()
    
    def on_exit(self):
        """Handle exit button"""
        if self.sender.running:
            if messagebox.askyesno("Confirm Exit", "Sender is still running. Do you want to exit?"):
                self.sender.stop()
                self.root.destroy()
        else:
            self.root.destroy()

def cli_main():
    """Command-line interface main function"""
    sender = ScreenSender()
    sender.running = True
    
    try:
        sender.sender_loop()
    except KeyboardInterrupt:
        print("\nStopping screen capture...")
    finally:
        sender.stop()

def gui_main():
    """GUI main function"""
    root = tk.Tk()
    app = SenderGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_exit)
    root.mainloop()

if __name__ == "__main__":
    if HAS_TKINTER:
        gui_main()
    else:
        print("Tkinter not available, running in command-line mode")
        cli_main()
