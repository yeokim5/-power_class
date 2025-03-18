#!/bin/bash

# Set DISPLAY environment variable
export DISPLAY=:0

# Wait for the X server to be available
until xset q &>/dev/null; do
    echo "Waiting for X server to be ready..."
    sleep 1
done

# Navigate to the script directory
cd /home/orange/Downloads/Power_Class

# Run the Python script with error logging
python3 /home/orange/Downloads/Power_Class/linux_login.py >> /tmp/rdp_app.log 2>&1
