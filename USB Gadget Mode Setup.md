## USB Gadget Mode Setup Instructions

To set up the Raspberry Pi in USB gadget mode:

1. **Edit `/boot/config.txt`**:
   ```
   sudo nano /boot/config.txt
   ```
   
   Add this line at the end:
   ```
   dtoverlay=dwc2
   ```

2. **Edit `/boot/cmdline.txt`**:
   ```
   sudo nano /boot/cmdline.txt
   ```
   
   Add this after `rootwait` (keep everything on one line):
   ```
   modules-load=dwc2,g_serial
   ```

3. **Reboot the Raspberry Pi**:
   ```
   sudo reboot
   ```

4. **Install required packages**:
   ```
   sudo apt update
   sudo apt install python3-pip python3-pil
   pip3 install pyserial mss
   ```

5. **On your PC, install**:
   ```
   pip install PyQt5 pyserial pillow
   ```

6. **Connect devices with USB-A to USB-A cable**

7. **Run the sender script on Raspberry Pi**:
   ```
   python3 rpi_screen_sender.py
   ```

8. **Run the receiver app on your PC**:
   ```
   python3 pc_screen_receiver.py
   ```

9. **In the PC app**:
   - Select the correct COM port (Windows) or /dev/ttyUSB0 (Linux)
   - Click "Connect"
   - You should see the Raspberry Pi screen appear in the window
