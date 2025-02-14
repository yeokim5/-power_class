import tkinter as tk
from tkinter import messagebox
import subprocess
import os
from PIL import Image, ImageTk
import time
import configparser
import threading

def connect_rdp():
    ip_address = load_ip()
    username = username_entry.get()
    password = password_entry.get()

    if not ip_address or not username or not password:
        show_error("Please fill in all fields and set IP in settings")
        return

    try:
        # Create a temporary Remmina connection file
        connection_file = create_remmina_file(ip_address, username, password)

        # Launch Remmina with the connection file in a separate thread
        threading.Thread(target=run_remmina, args=(connection_file,), daemon=True).start()

    except Exception as e:
        show_error(f"Unexpected error: {str(e)}")

def run_remmina(connection_file):
    start_time = time.time()
    result = subprocess.run(["remmina", "-c", connection_file], capture_output=True, text=True)
    end_time = time.time()

    # Clean up the temporary file
    os.remove(connection_file)

    if result.returncode != 0:
        show_error(f"Error: Cannot Connect\n\nDetails: {result.stderr}")
    else:
        connection_time = end_time - start_time
        show_message(f"Connection successful\nTime taken: {connection_time:.2f} seconds", "#4CAF50")
        monitor_connection()

def create_remmina_file(ip_address, username, password):
    config = configparser.ConfigParser()
    config['remmina'] = {
        'name': f'Connection to {ip_address}',
        'server': ip_address,
        'username': username,
        'password': password,
        'protocol': 'RDP',
        'hide_toolbar': 'true',
        'viewmode':'4',
        'fullscreen':'1',
    }

    # Create temporary connection file
    temp_file = os.path.expanduser('~/.local/share/remmina/temp.remmina')
    os.makedirs(os.path.dirname(temp_file), exist_ok=True)

    with open(temp_file, 'w') as configfile:
        config.write(configfile)

    return temp_file

def show_error(message):
    message_label.config(text=message, fg="#F44336")
    message_label.place(relx=0.5, rely=0.9, anchor="center")

def show_message(message, color="#000000"):
    message_label.config(text=message, fg=color)
    message_label.place(relx=0.5, rely=0.9, anchor="center")

def clear_message(*args):
    message_label.place_forget()

def open_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")

    width = 300
    height = 200
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    settings_window.geometry(f"{width}x{height}+{x}+{y}")
    settings_window.configure(bg="white")

    ip_label = tk.Label(settings_window, text="IP Address:", bg="white", font=("Helvetica", 12))
    ip_label.pack(pady=(20, 5))

    ip_input = tk.Entry(settings_window, font=("Helvetica", 12), bg="white", bd=0, highlightthickness=1, highlightcolor="#4CAF50")
    ip_input.pack(pady=5, padx=20, ipady=5, ipadx=5)
    ip_input.insert(0, load_ip())

    ip_input.bind("<Return>", lambda event: save_ip(ip_input.get(), settings_window))

    save_button = tk.Button(settings_window, text="Save", command=lambda: save_ip(ip_input.get(), settings_window),
                            bg="#7a6a6a", fg="white", font=("Helvetica", 12), bd=0, padx=20, pady=5)
    save_button.pack(pady=20)

def save_ip(ip, window):
    with open("ip_address.txt", "w") as f:
        f.write(ip)
    window.destroy()

def load_ip():
    if os.path.exists("ip_address.txt"):
        with open("ip_address.txt", "r") as f:
            return f.read().strip()
    return ""

def monitor_connection():
    def check_connection():
        while True:
            try:
                # Check if the Remmina process is still running
                result = subprocess.run(["pgrep", "remmina"], capture_output=True, text=True)
                if result.returncode != 0:
                    root.after(0, show_error, "Connection lost. Please reconnect.")
                    break
            except Exception as e:
                root.after(0, show_error, f"Error monitoring connection: {str(e)}")
                break
            time.sleep(5)

    threading.Thread(target=check_connection, daemon=True).start()

# Create the main window
root = tk.Tk()
root.title("Remmina RDP Login")

# Set window size to match screen resolution
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}")

# Load background image
bg_image_path = "/home/orange/Downloads/Power_Class/image/background_image.jpg"
bg_image = Image.open(bg_image_path)
bg_image = bg_image.resize((screen_width, screen_height), Image.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

root.after(500, lambda: root.attributes('-fullscreen', True))

# Load logos
sims_logo_path = "/home/orange/Downloads/Power_Class/image/sims_logo.png"
sims_logo = Image.open(sims_logo_path)
sims_logo = sims_logo.resize((150, 150), Image.LANCZOS)
sims_logo_photo = ImageTk.PhotoImage(sims_logo)

soft11_logo_path = "/home/orange/Downloads/Power_Class/image/soft11_logo.png"
soft11_logo = Image.open(soft11_logo_path)
soft11_logo = soft11_logo.resize((150, 150), Image.LANCZOS)
soft11_logo_photo = ImageTk.PhotoImage(soft11_logo)

# Create login frame
login_frame = tk.Frame(root, bg="white", bd=2, relief=tk.SOLID)
login_frame.place(relx=0.5, rely=0.5, anchor="center")

# Place logos side by side
logo_frame = tk.Frame(login_frame, bg="white")
logo_frame.pack(pady=(30, 20))

sims_logo_label = tk.Label(logo_frame, image=sims_logo_photo, bg="white")
sims_logo_label.image = sims_logo_photo
sims_logo_label.pack(side="left", padx=10)

soft11_logo_label = tk.Label(logo_frame, image=soft11_logo_photo, bg="white")
soft11_logo_label.image = soft11_logo_photo
soft11_logo_label.pack(side="left", padx=10)

# Username entry
username_label = tk.Label(login_frame, text="Username", bg="white", fg="#1E3F66", font=("Helvetica", 14))
username_label.pack(anchor="w", padx=30, pady=(0, 5))
username_entry = tk.Entry(login_frame, font=("Helvetica", 16), bg="white", bd=0, highlightthickness=1, highlightcolor="#1E3F66")
username_entry.pack(ipady=8, ipadx=8, padx=30, pady=(0, 15))
username_entry.config(width=25)

# Password entry
password_label = tk.Label(login_frame, text="Password", bg="white", fg="#1E3F66", font=("Helvetica", 14))
password_label.pack(anchor="w", padx=30, pady=(0, 5))
password_entry = tk.Entry(login_frame, font=("Helvetica", 16), bg="white", bd=0, highlightthickness=1, highlightcolor="#1E3F66", show="•")
password_entry.pack(ipady=8, ipadx=8, padx=30, pady=(0, 20))
password_entry.config(width=25)

# Connect button
connect_button = tk.Button(login_frame, text="LOGIN", command=connect_rdp,
                           font=("Helvetica", 16, "bold"), bg="#7a6a6a", fg="white", bd=0, padx=30, pady=10)
connect_button.pack(pady=(0, 30))

# Settings button
settings_button = tk.Button(root, text="⚙️", command=open_settings, font=("Helvetica", 16), bg="white", fg="#1E3F66", bd=0)
settings_button.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=20)

# Message label
message_label = tk.Label(root, font=("Helvetica", 12), bg="white", wraplength=500)

# Bind events
for entry in (username_entry, password_entry):
    entry.bind("<FocusIn>", clear_message)
    entry.bind("<Key>", clear_message)

username_entry.bind("<Return>", lambda event: connect_rdp())
password_entry.bind("<Return>", lambda event: connect_rdp())

# Start the GUI
root.mainloop()

