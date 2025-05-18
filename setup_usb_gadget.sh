#!/bin/bash

# Raspberry Pi USB Gadget Mode & SSH Setup Script
#
# This script:
# 1. Configures the Raspberry Pi in USB gadget mode
# 2. Enables SSH
# 3. Installs required dependencies for screen mirroring
#
# Usage: sudo bash setup_usb_gadget.sh

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root. Please use sudo."
    exit 1
fi

echo "=== Raspberry Pi USB Gadget Mode & SSH Setup ==="
echo ""

# 1. Configure USB gadget mode
echo "Configuring USB gadget mode..."

# Check if dtoverlay=dwc2 is already in config.txt
if grep -q "dtoverlay=dwc2" /boot/config.txt; then
    echo "dtoverlay=dwc2 already enabled in /boot/config.txt"
else
    echo "Adding dtoverlay=dwc2 to /boot/config.txt"
    echo "dtoverlay=dwc2" >> /boot/config.txt
fi

# Check if modules-load=dwc2,g_serial is already in cmdline.txt
if grep -q "modules-load=dwc2,g_serial" /boot/cmdline.txt; then
    echo "USB gadget modules already enabled in /boot/cmdline.txt"
else
    echo "Adding modules-load=dwc2,g_serial to /boot/cmdline.txt"
    # Insert after rootwait
    sed -i 's/rootwait/rootwait modules-load=dwc2,g_serial/g' /boot/cmdline.txt
fi

# 2. Enable SSH
echo ""
echo "Enabling SSH..."
touch /boot/ssh
echo "SSH has been enabled."

# 3. Install required dependencies
echo ""
echo "Installing required dependencies..."
apt update
apt install -y python3-pip python3-pil
pip3 install pyserial mss

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Your Raspberry Pi has been configured for USB gadget mode and SSH is enabled."
echo "The system needs to restart for changes to take effect."
echo ""
echo "After restart:"
echo "1. Connect the Raspberry Pi to your PC with a USB-A to USB-A cable"
echo "2. Run the screen mirroring script: python3 usb_screen_mirror.py --sender"
echo ""
echo "Do you want to reboot now? (y/n)"
read -r answer

if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
    echo "Rebooting..."
    reboot
else
    echo "Please reboot manually when ready with: sudo reboot"
fi
