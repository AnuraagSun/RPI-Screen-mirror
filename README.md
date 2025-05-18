# Raspberry Pi USB Screen Mirror

A cross-platform solution to display your Raspberry Pi screen on a Windows/Linux PC via a direct USB-A to USB-A cable connection, without requiring HDMI capture devices, network connections, or VNC.

![Project Banner](https://github.com/username/rpi-usb-screen-mirror/raw/main/images/banner.png)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Setup](#setup)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)
- [FAQ](#faq)
- [License](#license)

## 🔍 Overview

Raspberry Pi USB Screen Mirror lets you view your Raspberry Pi's screen on your PC using only a USB cable. It works by:

1. Configuring the Raspberry Pi in USB gadget mode to create a virtual serial connection
2. Capturing the Pi screen and sending compressed frames over the USB connection
3. Receiving and displaying these frames in real-time on the PC

This is perfect for headless Raspberry Pi setups or when you need to interact with your Pi without additional hardware or network configuration.

## ✨ Features

- **Direct USB Connection**: No network, HDMI capture device, or additional hardware needed
- **Cross-Platform Compatible**: Works on Windows and Linux PCs
- **Easy Setup**: Automated configuration script for Raspberry Pi
- **User-Friendly Interfaces**: GUI applications on both Raspberry Pi and PC
- **Real-Time Display**: 10-20 FPS screen mirroring at configurable resolutions
- **Screenshot Capability**: Capture and save screenshots of the Raspberry Pi screen
- **Status Monitoring**: Real-time FPS and connection status information
- **USB Hotplug Support**: Automatically detects port connections/disconnections

## 🛠️ Requirements

### Hardware

- Raspberry Pi 4 (may work on Pi Zero W and Pi 3 with modifications)
- USB-A to USB-A cable (sometimes called a "data transfer cable")
- Windows 10/11 or Linux Ubuntu/Debian PC

### Software

#### On Raspberry Pi:
- Raspberry Pi OS (Bullseye or newer recommended)
- Python 3.6+
- Required Python packages (installed by setup script):
  - `pyserial`
  - `pillow` (Python Imaging Library)
  - `mss` (optional, for improved screen capture)
  - `python3-tk` (for GUI)

#### On PC:
- Python 3.6+
- Required Python packages:
  - `PyQt5`
  - `pyserial`
  - `pillow` (Python Imaging Library)

## 📥 Installation

### 1. Download the Files

Clone the repository or download the individual files:

```bash
git clone https://github.com/username/rpi-usb-screen-mirror.git
```

Or download these three files individually:
- `setup_usb_gadget.sh` - Configuration script for Raspberry Pi
- `rpi_screen_sender.py` - Application for Raspberry Pi
- `pc_screen_receiver.py` - Application for PC

### 2. Install Required Packages on PC

```bash
# Windows
pip install PyQt5 pyserial pillow

# Linux
pip3 install PyQt5 pyserial pillow
```

### 3. Transfer Files to Raspberry Pi

Transfer `setup_usb_gadget.sh` and `rpi_screen_sender.py` to your Raspberry Pi using SCP, USB drive, or any file transfer method.

Example using SCP from Linux/Mac:
```bash
scp setup_usb_gadget.sh rpi_screen_sender.py pi@raspberrypi.local:~
```

## 🔧 Setup

### Configure Raspberry Pi for USB Gadget Mode

1. Connect to your Raspberry Pi via SSH or direct terminal access
2. Navigate to the directory containing the setup script
3. Make the script executable and run it:

```bash
chmod +x setup_usb_gadget.sh
sudo ./setup_usb_gadget.sh
```

4. The script will:
   - Configure USB gadget mode by modifying `/boot/config.txt` and `/boot/cmdline.txt`
   - Enable SSH service
   - Install required Python packages
   - Prompt for restart (choose 'y' to restart immediately)

5. After the Raspberry Pi reboots, it's configured for USB gadget mode

## 🚀 Usage

### Connection Setup

1. Connect your Raspberry Pi to your PC using a USB-A to USB-A cable
   - Connect to any USB port on the PC
   - On the Raspberry Pi, connect to the USB port (not the power port)

### Starting the Sender on Raspberry Pi

1. Log into your Raspberry Pi via SSH or terminal
2. Navigate to the directory containing `rpi_screen_sender.py`
3. Run the sender application:

```bash
python3 rpi_screen_sender.py
```

4. A GUI window will appear:

![RPi Sender GUI](https://github.com/username/rpi-usb-screen-mirror/raw/main/images/sender_gui.png)

5. Click the "Start Sending" button to begin streaming the screen

### Starting the Receiver on PC

1. Navigate to the directory containing `pc_screen_receiver.py`
2. Run the receiver application:

```bash
# Windows
python pc_screen_receiver.py

# Linux
python3 pc_screen_receiver.py
```

3. The PC application will open:

![PC Receiver GUI](https://github.com/username/rpi-usb-screen-mirror/raw/main/images/receiver_gui.png)

4. Select the correct USB port from the dropdown menu:
   - On Windows, it will appear as `COM3`, `COM4`, etc.
   - On Linux, it will appear as `/dev/ttyUSB0`, `/dev/ttyACM0`, etc.
   
5. Click "Start Receiving" to begin displaying the Raspberry Pi screen

6. The screen will appear in the application window:

![Screen Display](https://github.com/username/rpi-usb-screen-mirror/raw/main/images/screen_display.png)

### Taking Screenshots

1. While connected and receiving screen frames, click the "Take Screenshot" button
2. Choose a location and filename to save the current frame as an image file

### Disconnecting

1. On the PC, click "Stop Receiving" to close the connection
2. On the Raspberry Pi, click "Stop Sending" to halt screen capture
3. The USB cable can now be safely disconnected

## ❓ Troubleshooting

### No USB Serial Port Detected on PC

**Problem**: The PC application doesn't show any COM ports or ttyUSB devices.

**Solutions**:
1. Confirm the Raspberry Pi has been properly configured for USB gadget mode
2. Try a different USB cable (must be USB-A to USB-A data transfer cable)
3. Try different USB ports on both devices
4. Reboot both the Raspberry Pi and PC
5. Check if the serial device is recognized by the operating system:
   - Windows: Check Device Manager under "Ports (COM & LPT)"
   - Linux: Run `ls /dev/ttyUSB*` or `ls /dev/ttyACM*`

### Low FPS or Laggy Display

**Problem**: The screen refresh rate is very low or laggy.

**Solutions**:
1. Reduce the capture resolution by modifying `CAPTURE_WIDTH` and `CAPTURE_HEIGHT` in `rpi_screen_sender.py`
2. Reduce JPEG quality by lowering `JPEG_QUALITY` (30-50 is good for speed)
3. Make sure you're using USB 3.0 ports if available
4. Close other applications on the Raspberry Pi to free up CPU resources

### Installation Errors on Raspberry Pi

**Problem**: Errors when installing required packages.

**Solutions**:
1. Update your Raspberry Pi OS:
   ```bash
   sudo apt update
   sudo apt upgrade
   ```
2. Install packages manually:
   ```bash
   sudo apt install python3-pip python3-pil python3-tk
   pip3 install pyserial mss
   ```

### "Permission Denied" Error for Serial Port

**Problem**: The application shows "Permission denied" when accessing the serial port.

**Solutions**:
- Windows: Run the receiver application as Administrator
- Linux: Add your user to the `dialout` group:
  ```bash
  sudo usermod -a -G dialout $USER
  ```
  Then log out and log back in

## 🔄 Advanced Configuration

### Modifying Frame Rate and Quality

You can customize the performance by editing these variables in `rpi_screen_sender.py`:

```python
# Configuration
CAPTURE_WIDTH = 1280    # Decrease for better performance (e.g., 800)
CAPTURE_HEIGHT = 720    # Decrease for better performance (e.g., 600)
JPEG_QUALITY = 60       # Lower for better performance (e.g., 40)
TARGET_FPS = 15         # Lower for less CPU usage (e.g., 10)
```

### Running in CLI Mode on Raspberry Pi

If you're running the Raspberry Pi in headless mode with no display manager, you can run the sender in CLI mode:

```bash
python3 -c "
import sys
sys.modules['tkinter'] = None
import rpi_screen_sender
"
```

### Running the Sender at Startup

To automatically start the screen sender when your Raspberry Pi boots:

1. Create a systemd service file:

```bash
sudo nano /etc/systemd/system/screen-sender.service
```

2. Add the following content:

```
[Unit]
Description=Raspberry Pi USB Screen Sender
After=multi-user.target

[Service]
User=pi
WorkingDirectory=/home/pi
ExecStart=/usr/bin/python3 /home/pi/rpi_screen_sender.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:

```bash
sudo systemctl enable screen-sender.service
sudo systemctl start screen-sender.service
```

## ❔ FAQ

### Q: Will this work with Raspberry Pi Zero/Zero W/3B+?

**A:** Yes, but it requires additional configuration. For Pi Zero, you'll need to modify the USB gadget module to `g_serial` and potentially change the device path. The performance might also be slower due to CPU limitations.

### Q: Does this provide interactive control of the Raspberry Pi?

**A:** No, this is a one-way screen mirroring solution. It doesn't transmit mouse or keyboard input to the Raspberry Pi. For interactive control, you would need to combine this with SSH or similar remote access methods.

### Q: Can I use a regular USB-A to micro-USB/USB-C cable?

**A:** No, this solution specifically requires a USB-A to USB-A data transfer cable. Regular charging cables won't work for this purpose.

### Q: What's the maximum resolution and FPS possible?

**A:** This depends on your Raspberry Pi model and PC specifications. On a Raspberry Pi 4 with a reasonably powerful PC, you can achieve 1280x720 at 15-20 FPS. Higher resolutions are possible but may reduce the frame rate.

### Q: Why not just use VNC?

**A:** VNC requires network connectivity and configuration. This solution works without any network, making it ideal for:
- Initial setup of a new Raspberry Pi
- Field deployments without network access
- Secure environments where network connections are restricted
- Simpler configuration for beginners

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---
