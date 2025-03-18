import tkinter as tk
from tkinter import messagebox
import subprocess
import os
from PIL import Image, ImageTk
import time
import configparser
import threading
import socket

class RemminaRDPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PowerClient RDP")
        self.root.configure(bg="#f0f0f0")  # Warm light beige background

        # New natural, muted color scheme
        self.primary_color = "#3a3a3a"    # Muted olive green
        self.secondary_color = "#707070"  # Lighter muted green for hover
        self.text_color = "#1a1a1a"       # Dark warm gray for text
        self.error_color = "#b30000"      # Soft muted red
        self.success_color = "#4d4d4d"    # Earthy green

        # Initialize escape key counter
        self.esc_counter = 0
        self.last_esc_time = 0
        self.shortcuts_disabled = False

        # Disable keyboard shortcuts at startup
        threading.Thread(target=self.disable_keyboard_shortcuts, daemon=True).start()

        # Setup key bindings for escape key restoration
        self.root.bind("<Shift-Escape>", self.handle_escape_key)

        self.setup_ui()

    def setup_ui(self):
        self.root.attributes('-fullscreen', True)
        self.load_background_image()
        self.create_login_frame()
        self.create_message_label()
        self.create_settings_gear()

    def load_background_image(self):
        try:
            bg_image_path = "new_image/background_image.png"  # Updated path
            bg_image = Image.open(bg_image_path)
            bg_image = bg_image.resize((self.root.winfo_screenwidth(),
                                      self.root.winfo_screenheight()), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            bg_label = tk.Label(self.root, image=self.bg_photo, bg="#f5f6f5")
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Background image loading error: {e}")
            # 이미지 로드 실패 시 대체 그라데이션
            bg_label = tk.Label(self.root, bg="#f5f6f5")
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    def create_login_frame(self):
        # Add subtle shadow and rounded corners to the card
        login_frame = tk.Frame(self.root, bg="white", padx=40, pady=40)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Configure custom rounded corners with drop shadow effect
        login_frame.configure(bd=0, highlightthickness=1,
                              highlightbackground="#e0e0e0", highlightcolor="#e0e0e0")
        
        # Add inner padding frame to create more aesthetic spacing
        inner_frame = tk.Frame(login_frame, bg="white")
        inner_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Load and display logo image with improved error handling and scaling
        try:
            logo_path = "new_image/powerclient_logo.png"
            logo_image = Image.open(logo_path)
            
            # Calculate appropriate scaling based on screen size
            screen_width = self.root.winfo_screenwidth()
            scale_factor = min(1.3, screen_width / 1920 * 1.5)  # Responsive scaling
            
            original_width, original_height = logo_image.size
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            
            logo_image = logo_image.resize((new_width, new_height), Image.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(inner_frame, image=self.logo_photo, bg="white")
            logo_label.pack(pady=(0, 30))
        except Exception as e:
            print(f"Logo image loading error: {e}")
            # Improved fallback with gradient effect text
            title_label = tk.Label(inner_frame,
                                 text="PowerClient RDP",
                                 bg="white",
                                 fg=self.text_color,
                                 font=("Segoe UI", 28, "bold"))
            title_label.pack(pady=(0, 30))

        # Create input fields with improved visual styling
        self.create_entry(inner_frame, "사용자 이름", "username_entry")
        self.create_entry(inner_frame, "비밀번호", "password_entry", show="●")

        # Connect button with enhanced hover and focus effects
        connect_button = tk.Button(inner_frame,
                                 text="연결",
                                 command=self.connect_rdp,
                                 font=("Segoe UI", 12, "bold"),
                                 bg=self.primary_color,
                                 fg="white",
                                 bd=0,
                                 padx=30,
                                 pady=10,
                                 relief=tk.FLAT,
                                 activebackground=self.secondary_color,
                                 cursor="hand2")
        connect_button.pack(pady=(30, 0))
        
        # Enhanced hover effects
        connect_button.bind("<Enter>", lambda e: connect_button.config(bg=self.secondary_color))
        connect_button.bind("<Leave>", lambda e: connect_button.config(bg=self.primary_color))
        
        # Add focus indicator
        connect_button.bind("<FocusIn>", lambda e: connect_button.config(
            highlightbackground=self.secondary_color, highlightthickness=2))
        connect_button.bind("<FocusOut>", lambda e: connect_button.config(highlightthickness=0))

    def create_entry(self, parent, label_text, entry_var, show=""):
        entry_frame = tk.Frame(parent, bg="white")
        entry_frame.pack(fill="x", pady=12)

        label = tk.Label(entry_frame,
                        text=label_text,
                        bg="white",
                        fg=self.text_color,
                        font=("Segoe UI", 11, "bold"))
        label.pack(anchor="w", pady=(0, 5))  # Increased spacing below label

        # Improved container styling with subtle rounded corners
        input_container = tk.Frame(entry_frame, bg="#f8f9fa", 
                                  highlightthickness=1, 
                                  highlightbackground="#ced4da", 
                                  highlightcolor=self.secondary_color,
                                  bd=0)
        input_container.pack(fill="x", pady=(0, 0))

        # Add slight padding to entry for better text alignment
        entry = tk.Entry(input_container,
                        font=("Segoe UI", 12),
                        bg="#f8f9fa",
                        fg=self.text_color,
                        bd=0,
                        highlightthickness=0,
                        relief=tk.FLAT,
                        show=show)
        entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(12, 0))  # Increased padding

        # Enhanced password visibility toggle
        if entry_var == "password_entry":
            self.password_visible = False
            try:
                # Load both eye icons for toggle states
                eye_open_path = "new_image/eye_open.png"
                eye_closed_path = "new_image/eye_closed.png"
                
                # Create both icon states
                eye_open = Image.open(eye_open_path)
                eye_closed = Image.open(eye_closed_path) if os.path.exists(eye_closed_path) else eye_open
                
                # Resize icons to appropriate size
                icon_size = (20, 20)
                eye_open = eye_open.resize(icon_size, Image.LANCZOS)
                eye_closed = eye_closed.resize(icon_size, Image.LANCZOS)
                
                # Store as PhotoImage objects
                self.eye_open_icon = ImageTk.PhotoImage(eye_open)
                self.eye_closed_icon = ImageTk.PhotoImage(eye_closed)
                
                # Create toggle button with initial closed eye state
                self.toggle_btn = tk.Button(input_container,
                                          image=self.eye_closed_icon,
                                          command=lambda: self.toggle_password_visibility(entry),
                                          bg="#f8f9fa",
                                          activebackground="#f8f9fa",  # Match background color to prevent visible click effect
                                          bd=0,
                                          relief=tk.FLAT,
                                          cursor="hand2",
                                          highlightthickness=0)
            except Exception as e:
                print(f"Eye icon loading error: {e}")
                # Fallback to using a text symbol with improved styling
                self.toggle_btn = tk.Button(input_container,
                                          text="👁️",
                                          command=lambda: self.toggle_password_visibility(entry),
                                          bg="#f8f9fa",
                                          activebackground="#f0f0f0",
                                          bd=0,
                                          relief=tk.FLAT,
                                          cursor="hand2",
                                          highlightthickness=0,
                                          font=("Segoe UI", 11))
            
            # Better alignment for the toggle button inside the container
            self.toggle_btn.pack(side="right", padx=(0, 12), fill="y")

        setattr(self, entry_var, entry)
        
        # Improved focus effects
        entry.bind("<FocusIn>", lambda e: input_container.config(
            highlightbackground=self.primary_color, highlightcolor=self.primary_color))
        entry.bind("<FocusOut>", lambda e: input_container.config(
            highlightbackground="#ced4da", highlightcolor="#ced4da"))
        
        entry.bind("<Key>", self.clear_message)
        entry.bind("<Return>", lambda event: self.connect_rdp())

    def toggle_password_visibility(self, entry):
        """Toggle the visibility of the password entry field with icon change"""
        if self.password_visible:
            # Hide password
            entry.config(show="●")
            if hasattr(self, 'eye_closed_icon'):
                self.toggle_btn.config(image=self.eye_closed_icon)
            else:
                self.toggle_btn.config(relief=tk.FLAT)
            self.password_visible = False
        else:
            # Show password
            entry.config(show="")
            if hasattr(self, 'eye_open_icon'):
                self.toggle_btn.config(image=self.eye_open_icon)
            else:
                self.toggle_btn.config(relief=tk.SUNKEN)
            self.password_visible = True

    def create_message_label(self):
        # Create a frame to hold the message for better styling
        self.message_frame = tk.Frame(self.root, bg="white", bd=1, relief="flat",
                                    highlightthickness=1, highlightbackground="#e0e0e0")
        
        self.message_icon_label = tk.Label(self.message_frame, bg="white", padx=10)
        self.message_icon_label.pack(side="left")
        
        self.message_label = tk.Label(self.message_frame,
                                    font=("Segoe UI", 11),
                                    bg="white",
                                    fg=self.text_color,
                                    wraplength=600,
                                    pady=10,
                                    padx=5,
                                    bd=0,
                                    relief="flat")
        self.message_label.pack(side="left", fill="both", expand=True)
        
        # Load message icons
        try:
            # Error icon
            error_icon_path = "new_image/error_icon.png"
            if os.path.exists(error_icon_path):
                error_icon = Image.open(error_icon_path)
                error_icon = error_icon.resize((20, 20), Image.LANCZOS)
                self.error_icon = ImageTk.PhotoImage(error_icon)
            
            # Success icon
            success_icon_path = "new_image/success_icon.png"
            if os.path.exists(success_icon_path):
                success_icon = Image.open(success_icon_path)
                success_icon = success_icon.resize((20, 20), Image.LANCZOS)
                self.success_icon = ImageTk.PhotoImage(success_icon)
            
            # Info icon
            info_icon_path = "new_image/info_icon.png"
            if os.path.exists(info_icon_path):
                info_icon = Image.open(info_icon_path)
                info_icon = info_icon.resize((20, 20), Image.LANCZOS)
                self.info_icon = ImageTk.PhotoImage(info_icon)
        except Exception as e:
            print(f"Message icon loading error: {e}")

    def create_settings_gear(self):
        try:
            settings_icon_path = "new_image/settings_logo_login_window.png"
            settings_icon = Image.open(settings_icon_path)
            settings_icon = settings_icon.resize((32, 32), Image.LANCZOS)
            self.settings_icon_photo = ImageTk.PhotoImage(settings_icon)
            
            settings_button = tk.Button(self.root,
                                        image=self.settings_icon_photo,
                                        command=self.toggle_settings_panel,
                                        bg="#142457",
                                        bd=0,
                                        relief=tk.FLAT,
                                        activebackground="#142457",
                                        cursor="hand2",  # Changed to hand cursor for better UX
                                        highlightthickness=0,
                                        activeforeground="#142457")
        except Exception as e:
            print(f"Settings icon loading error: {e}")
            settings_button = tk.Button(self.root,
                                        text="⚙️",
                                        command=self.toggle_settings_panel,
                                        font=("Segoe UI", 14),  # Slightly larger
                                        bg="#142457",
                                        fg=self.text_color,
                                        bd=0,
                                        padx=10,
                                        pady=5,
                                        relief=tk.FLAT,
                                        activebackground="#142457",
                                        cursor="hand2",  # Changed to hand cursor
                                        highlightthickness=0,
                                        activeforeground=self.text_color)
        
        # Add a subtle hover effect
        settings_button.bind("<Enter>", lambda e: settings_button.config(bg="#1a2e6a"))
        settings_button.bind("<Leave>", lambda e: settings_button.config(bg="#142457"))
        
        settings_button.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=20)

    def connect_rdp(self):
        if not self.is_connected():
            self.show_error("네트워크 연결이 감지되지 않음")
            return

        ip_address = self.load_ip()
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not all([ip_address, username, password]):
            self.show_error("모든 필드를 작성해주세요")
            return

        try:
            connection_file = self.create_remmina_file(ip_address, username, password)
            threading.Thread(target=self.run_remmina, args=(connection_file,), daemon=True).start()
            self.show_message("연결 중...", "#666666")
            self.root.after(2000, self.clear_message)  # 2초 후 메시지 숨기기
        except Exception as e:
            self.show_error(f"연결 실패: {str(e)}")

    def run_remmina(self, connection_file):
        start_time = time.time()
        result = subprocess.run(["remmina", "-c", connection_file], capture_output=True, text=True)
        end_time = time.time()

        os.remove(connection_file)

        if result.returncode != 0:
            self.root.after(0, self.show_error, f"연결 실패: {result.stderr}")
        else:
            connection_time = end_time - start_time
            self.root.after(0, self.show_message,
                          f"성공적으로 연결됨 ({connection_time:.2f}초)",
                          self.success_color)
            self.monitor_connection()

    def create_remmina_file(self, ip_address, username, password):
        config = configparser.ConfigParser()
        config['remmina'] = {
            'name': f'RDP 연결 - {ip_address}',
            'server': ip_address,
            'username': username,
            'password': password,
            'protocol': 'RDP',
            'hide_toolbar': 'true',
            'viewmode': '4',
            'fullscreen': '1',
            'quality': '0',  # 0 = Poor (fastest), 1 = Medium, 2 = Good, 9 = Best (adjust as needed)
            # Performance optimizations
            #'disable_menu_animations': '1',  # Disable menu animations
            #'disable_themes': '1',  # Disable visual themes
            #'disable_cursor_shadow': '1',  # Disable cursor shadow
            #'disable_fontsmoothing': '1',  # Disable font smoothing
            #'enable_compression': '1',  # Enable data compression
            #'gfx': '1',  # Enable Graphics Extensions (RemoteFX or similar)
            #'gfx_h264': '1',  # Enable H.264 encoding (requires FreeRDP support)
            #'resolution': f'{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}'  # Match client resolution
        }

        temp_file = os.path.expanduser('~/.local/share/remmina/temp.remmina')
        os.makedirs(os.path.dirname(temp_file), exist_ok=True)
        with open(temp_file, 'w') as configfile:
            config.write(configfile)

        return temp_file

    def show_error(self, message):
        self.message_frame.config(highlightbackground=self.error_color)
        self.message_label.config(text=message, fg=self.error_color)
        
        if hasattr(self, 'error_icon'):
            self.message_icon_label.config(image=self.error_icon)
        else:
            self.message_icon_label.config(text="❌", fg=self.error_color, font=("Segoe UI", 11))
        
        self.message_frame.place(relx=0.5, rely=0.85, anchor="center")

    def show_message(self, message, color="#666666"):
        self.message_frame.config(highlightbackground="#d0d0d0")
        self.message_label.config(text=message, fg=color)
        
        if color == self.success_color and hasattr(self, 'success_icon'):
            self.message_icon_label.config(image=self.success_icon)
        elif hasattr(self, 'info_icon'):
            self.message_icon_label.config(image=self.info_icon)
        else:
            self.message_icon_label.config(text="ℹ️", fg=color, font=("Segoe UI", 11))
        
        self.message_frame.place(relx=0.5, rely=0.85, anchor="center")

    def clear_message(self, *args):
        self.message_frame.place_forget()

    def open_settings(self):
        """This method is replaced by toggle_settings_panel"""
        pass

    def save_ip(self, ip, window):
        with open("ip_address.txt", "w") as f:
            f.write(ip.strip())
        self.show_message("설정이 저장되었습니다", self.success_color)
        if window and window.winfo_exists():
            window.destroy()

    def load_ip(self):
        try:
            with open("ip_address.txt", "r") as f:
                return f.read().strip()
        except:
            return ""

    def monitor_connection(self):
        def check_connection():
            while True:
                try:
                    result = subprocess.run(["pgrep", "remmina"], capture_output=True)
                    if result.returncode != 0:
                        self.root.after(0, self.show_error, "연결이 종료되었습니다")
                        break
                except:
                    self.root.after(0, self.show_error, "모니터링 실패")
                    break
                time.sleep(5)
        threading.Thread(target=check_connection, daemon=True).start()

    def is_connected(self):
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False

    def open_wifi_settings(self):
        subprocess.run(["gnome-control-center", "wifi"])

    def show_power_options(self):
        power_window = tk.Toplevel(self.root)
        power_window.title("전원 옵션")
        power_window.configure(bg="white")

        width, height = 300, 200
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        power_window.geometry(f"{width}x{height}+{x}+{y}")

        tk.Label(power_window,
                text="전원 옵션",
                bg="white",
                fg=self.text_color,
                font=("Segoe UI", 14, "bold")).pack(pady=(20, 20))

        for text, cmd in [("전원 재시작", self.restart_system),
                         ("전원 종료", self.power_off_system)]:
            btn = tk.Button(power_window,
                          text=text,
                          command=cmd,
                          bg=self.primary_color,
                          fg="white",
                          font=("Segoe UI", 11),
                          bd=0,
                          padx=20,
                          pady=8,
                          relief=tk.FLAT,
                          activebackground=self.secondary_color,
                          cursor="hand2")
            btn.pack(fill="x", padx=40, pady=6)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.secondary_color))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.primary_color))

    def restart_system(self):
        self.show_power_confirmation("재시작", "시스템을 재시작하시겠습니까?", 
                                   lambda: subprocess.run(["systemctl", "reboot"]))

    def power_off_system(self):
        self.show_power_confirmation("종료", "시스템을 종료하시겠습니까?", 
                                   lambda: subprocess.run(["systemctl", "poweroff"]))

    def show_power_confirmation(self, action_type, message, action_command):
        confirm_window = tk.Toplevel(self.root)
        confirm_window.title(f"{action_type} 확인")
        confirm_window.configure(bg="white")
        
        # Set size and position - reduced height
        width, height = 360, 115  # Reduced height from 220 to 180
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        confirm_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Make the window border look nicer
        confirm_window.config(highlightbackground="#e0e0e0", highlightthickness=1)
        
        # Try to load appropriate icon with reduced vertical padding
        icon_label = tk.Label(confirm_window, bg="white")
        try:
            # Try loading a warning icon
            icon_path = "new_image/warning_icon.png"
            if os.path.exists(icon_path):
                icon = Image.open(icon_path)
                icon = icon.resize((48, 48), Image.LANCZOS)
                self.warning_icon = ImageTk.PhotoImage(icon)
                icon_label.config(image=self.warning_icon)
                icon_label.pack(pady=(15, 10))  # Reduced padding
        except Exception as e:
            print(f"Warning icon loading error: {e}")
        
        # Add message with improved styling and reduced padding
        tk.Label(confirm_window,
               text=message,
               bg="white",
               fg=self.text_color,
               font=("Segoe UI", 12, "bold")).pack(pady=(5, 15))  # Reduced bottom padding
        
        # Buttons frame with adjusted spacing
        buttons_frame = tk.Frame(confirm_window, bg="white")
        buttons_frame.pack(fill="x", padx=40, pady=(0, 15))  # Reduced bottom padding
        
        # No button (cancel) - put first for safety
        no_btn = tk.Button(buttons_frame,
                         text="취소",
                         command=confirm_window.destroy,
                         bg="#f0f0f0",
                         fg=self.text_color,
                         font=("Segoe UI", 11),
                         bd=0,
                         padx=10,
                         pady=8,
                         relief=tk.FLAT,
                         activebackground="#e0e0e0",
                         cursor="hand2")
        no_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Yes button (confirm action)
        yes_btn = tk.Button(buttons_frame,
                          text=f"{action_type}",
                          command=lambda: [confirm_window.destroy(), action_command()],
                          bg=self.primary_color,
                          fg="white",
                          font=("Segoe UI", 11),
                          bd=0,
                          padx=10,
                          pady=8,
                          relief=tk.FLAT,
                          activebackground=self.secondary_color,
                          cursor="hand2")
        yes_btn.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # Add hover effects
        no_btn.bind("<Enter>", lambda e: no_btn.config(bg="#e0e0e0"))
        no_btn.bind("<Leave>", lambda e: no_btn.config(bg="#f0f0f0"))
        yes_btn.bind("<Enter>", lambda e: yes_btn.config(bg=self.secondary_color))
        yes_btn.bind("<Leave>", lambda e: yes_btn.config(bg=self.primary_color))
        
        # Make dialog modal
        confirm_window.transient(self.root)
        confirm_window.grab_set()
        confirm_window.focus_set()

    # New methods for keyboard shortcuts management
    def disable_keyboard_shortcuts(self):
        """Disable all system keyboard shortcuts at startup"""
        try:
            # Create script file for disabling shortcuts
            script_content = """#!/bin/bash
# Create a backup directory
mkdir -p ~/gnome-settings-backup
# Backup ALL keyboard shortcuts and relevant settings
gsettings list-recursively org.gnome.desktop.wm.keybindings > ~/gnome-settings-backup/wm-keybindings.txt
gsettings list-recursively org.gnome.mutter.keybindings > ~/gnome-settings-backup/mutter-keybindings.txt
gsettings list-recursively org.gnome.mutter.wayland.keybindings > ~/gnome-settings-backup/mutter-wayland-keybindings.txt
gsettings list-recursively org.gnome.shell.keybindings > ~/gnome-settings-backup/shell-keybindings.txt
gsettings get org.gnome.mutter overlay-key > ~/gnome-settings-backup/overlay-key.txt
gsettings get org.gnome.desktop.wm.preferences mouse-button-modifier > ~/gnome-settings-backup/mouse-modifier.txt
# Disable all keybindings in these schemas
gsettings list-keys org.gnome.desktop.wm.keybindings | while read key; do
  gsettings set org.gnome.desktop.wm.keybindings $key "[]"
done
gsettings list-keys org.gnome.mutter.keybindings | while read key; do
  gsettings set org.gnome.mutter.keybindings $key "[]"
done
gsettings list-keys org.gnome.mutter.wayland.keybindings 2>/dev/null | while read key; do
  gsettings set org.gnome.mutter.wayland.keybindings $key "[]"
done
gsettings list-keys org.gnome.shell.keybindings | while read key; do
  gsettings set org.gnome.shell.keybindings $key "[]"
done
# Disable the Super key (overlay-key)
gsettings set org.gnome.mutter overlay-key ""
# Disable window movement with Alt
gsettings set org.gnome.desktop.wm.preferences mouse-button-modifier "<Super>"
"""
            disable_script_path = os.path.expanduser("~/disable_shortcuts.sh")
            with open(disable_script_path, "w") as f:
                f.write(script_content)
            os.chmod(disable_script_path, 0o755)

            # Execute the script
            result = subprocess.run([disable_script_path], capture_output=True, text=True)
            if result.returncode == 0:
                
                self.root.after(3000, self.clear_message)
                self.shortcuts_disabled = True
            else:
                self.root.after(0, self.show_error, f"단축키 비활성화 실패: {result.stderr}")
        except Exception as e:
            self.root.after(0, self.show_error, f"단축키 비활성화 오류: {str(e)}")

    def restore_keyboard_shortcuts(self):
        """Restore all system keyboard shortcuts"""
        try:
            # Create script file for restoring shortcuts
            script_content = """#!/bin/bash
# Restore all keybindings
cat ~/gnome-settings-backup/wm-keybindings.txt | while read schema key value; do
  gsettings set $schema $key "$value"
done
cat ~/gnome-settings-backup/mutter-keybindings.txt | while read schema key value; do
  gsettings set $schema $key "$value"
done
cat ~/gnome-settings-backup/mutter-wayland-keybindings.txt 2>/dev/null | while read schema key value; do
  gsettings set $schema $key "$value"
done
cat ~/gnome-settings-backup/shell-keybindings.txt | while read schema key value; do
  gsettings set $schema $key "$value"
done
# Restore overlay key (Super key)
gsettings set org.gnome.mutter overlay-key "$(cat ~/gnome-settings-backup/overlay-key.txt)"
# Restore mouse modifier
gsettings set org.gnome.desktop.wm.preferences mouse-button-modifier "$(cat ~/gnome-settings-backup/mouse-modifier.txt)"
"""
            restore_script_path = os.path.expanduser("~/restore_shortcuts.sh")
            with open(restore_script_path, "w") as f:
                f.write(script_content)
            os.chmod(restore_script_path, 0o755)

            # Execute the script
            result = subprocess.run([restore_script_path], capture_output=True, text=True)
            if result.returncode == 0:
                self.root.after(0, self.show_message, "시스템 단축키가 복원되었습니다", self.success_color)
                self.root.after(3000, self.clear_message)
                self.shortcuts_disabled = False
            else:
                self.root.after(0, self.show_error, f"단축키 복원 실패: {result.stderr}")
        except Exception as e:
            self.root.after(0, self.show_error, f"단축키 복원 오류: {str(e)}")

    def handle_escape_key(self, event):
        """Handle escape key presses with left shift to toggle shortcut restoration"""
        # Check if left shift is pressed (state=1 means shift is pressed)
        if event.state != 1:  # 1 represents left shift
            return
        
        current_time = time.time()

        # Reset counter if more than 2 seconds between presses
        if current_time - self.last_esc_time > 2:
            self.esc_counter = 1
        else:
            self.esc_counter += 1

        self.last_esc_time = current_time

        # If shift+escape pressed three times in a row, toggle keyboard shortcuts
        if self.esc_counter >= 3:
            self.esc_counter = 0
            if self.shortcuts_disabled:
                threading.Thread(target=self.restore_keyboard_shortcuts, daemon=True).start()
                self.show_message("시스템 단축키 복원 중...", self.primary_color)
            else:
                threading.Thread(target=self.disable_keyboard_shortcuts, daemon=True).start()
                self.show_message("시스템 단축키 비활성화 중...", self.primary_color)
            
            # Make the window smaller instead of minimizing
            self.root.attributes('-fullscreen', False)  # Disable fullscreen
            
            # Set window to 800x600 and center it on screen
            window_width = 800
            window_height = 600
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Calculate position for center of screen
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            
            # Set new geometry
            self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def toggle_settings_panel(self):
        # Check if panel already exists
        if hasattr(self, 'settings_panel') and self.settings_panel.winfo_exists():
            # Add slide-out animation when closing
            panel_width = 330  # Slightly wider panel
            screen_width = self.root.winfo_screenwidth()
            
            # Slide out animation
            for i in range(screen_width - panel_width, screen_width + 5, 20):
                self.settings_panel.place(x=i)
                self.settings_panel.update()
                time.sleep(0.01)
            
            self.settings_panel.destroy()
            return

        # Create the sliding panel - now positioned on the right side
        panel_width = 330  # Slightly wider panel
        screen_width = self.root.winfo_screenwidth()
        self.settings_panel = tk.Frame(self.root, bg="white", width=panel_width)
        self.settings_panel.place(x=screen_width, y=0, width=panel_width, height=self.root.winfo_screenheight())
        
        # Improved styling with subtle shadow
        self.settings_panel.config(highlightbackground="#d0d0d0", highlightcolor="#d0d0d0", highlightthickness=1)
        
        # Header with title and icons - improved styling with more space
        header_frame = tk.Frame(self.settings_panel, bg="#f0f2f5", height=70)  # Changed color and height
        header_frame.pack(fill="x")
        
        # Add settings icon and title with better error handling
        try:
            settings_icon_path = "new_image/settings_logo_toggle_settings_window.png"
            settings_icon = Image.open(settings_icon_path)
            settings_icon = settings_icon.resize((26, 26), Image.LANCZOS)  # Slightly larger icon
            # Create transparent background
            settings_icon = settings_icon.convert("RGBA")
            data = settings_icon.getdata()
            new_data = []
            for item in data:
                # Change all white (or nearly white) pixels to transparent
                if item[0] > 240 and item[1] > 240 and item[2] > 240:
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)
            settings_icon.putdata(new_data)
            self.settings_header_icon = ImageTk.PhotoImage(settings_icon)
            
            settings_icon_label = tk.Label(header_frame, image=self.settings_header_icon, bg="#f0f2f5")
            settings_icon_label.pack(side="left", padx=(18, 5), pady=20)
        except Exception as e:
            print(f"Settings header icon loading error: {e}")
        
        title_label = tk.Label(header_frame, text="설정", font=("Segoe UI", 14, "bold"), bg="#f0f2f5", fg=self.text_color)
        title_label.pack(side="left", pady=20)
        
        # Add divider under header
        divider = tk.Frame(self.settings_panel, height=1, bg="#e0e0e0")
        divider.pack(fill="x")
        
        # Add scrollable content area for settings
        content_canvas = tk.Canvas(self.settings_panel, bg="white", highlightthickness=0)
        content_canvas.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Add scrollbar for long content but keep it hidden
        scrollbar = tk.Scrollbar(content_canvas, orient="vertical", command=content_canvas.yview)
        # Don't pack the scrollbar to hide it, but keep its functionality
        content_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create frame for settings content
        content_frame = tk.Frame(content_canvas, bg="white")
        content_canvas.create_window((0, 0), window=content_frame, anchor="nw", width=panel_width-20)
        
        # Add a close button with improved styling
        try:
            close_icon_path = "new_image/close_logo.png"
            close_icon = Image.open(close_icon_path)
            close_icon = close_icon.resize((22, 22), Image.LANCZOS)  # Slightly larger
            close_icon = close_icon.convert("RGBA")
            data = close_icon.getdata()
            new_data = []
            for item in data:
                if item[0] > 240 and item[1] > 240 and item[2] > 240:
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)
            close_icon.putdata(new_data)
            self.close_icon_photo = ImageTk.PhotoImage(close_icon)
            
            close_button = tk.Button(header_frame,
                                   image=self.close_icon_photo,
                                   command=self.toggle_settings_panel,
                                   bg="#f0f2f5",
                                   activebackground="#e0e2e5",  # Light hover effect
                                   bd=0,
                                   relief=tk.FLAT,
                                   cursor="hand2",  # Changed to hand cursor
                                   highlightthickness=0)
        except Exception as e:
            print(f"Close icon loading error: {e}")
            close_button = tk.Button(header_frame,
                                   text="✕",
                                   command=self.toggle_settings_panel,
                                   font=("Segoe UI", 14),
                                   bg="#f0f2f5",
                                   fg=self.text_color,
                                   bd=0,
                                   relief=tk.FLAT,
                                   activebackground="#e0e2e5",
                                   cursor="hand2",
                                   highlightthickness=0)
                                   
        close_button.pack(side="right", padx=20, pady=20)
        
        # Add settings sections with improved styling
        self.add_ip_settings_section(content_frame)
        self.add_power_options_section(content_frame)
        
        # Add soft11 logo to bottom center of the settings panel
        self.add_soft11_logo(self.settings_panel, panel_width)
        
        # Configure scrolling behavior
        content_frame.bind("<Configure>", lambda e: content_canvas.configure(scrollregion=content_canvas.bbox("all")))
        content_canvas.bind_all("<MouseWheel>", lambda e: content_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # Ensure the panel slides in smoothly
        for i in range(screen_width, screen_width - panel_width - 5, -20):
            pos = max(i, screen_width - panel_width)
            self.settings_panel.place(x=pos)
            self.settings_panel.update()
            time.sleep(0.01)

    def add_soft11_logo(self, parent, panel_width):
        """Add the soft11 logo to the bottom center of the settings panel"""
        try:
            logo_path = "new_image/soft11_logo.png"
            logo_image = Image.open(logo_path)
            
            # Determine appropriate size for the logo (adjust as needed)
            logo_height = 40  # Fixed height
            aspect_ratio = logo_image.width / logo_image.height
            logo_width = int(logo_height * aspect_ratio)
            
            # Resize the logo
            logo_image = logo_image.resize((logo_width, logo_height), Image.LANCZOS)
            self.soft11_logo = ImageTk.PhotoImage(logo_image)
            
            # Create a label for the logo
            logo_label = tk.Label(parent, image=self.soft11_logo, bg="white")
            
            # Position at bottom center with some padding
            # Calculate center position based on panel width and logo width
            center_x = (panel_width - logo_width) // 2
            logo_label.place(x=center_x, y=self.root.winfo_screenheight()-logo_height-15, 
                           width=logo_width, height=logo_height)
            
        except Exception as e:
            print(f"Soft11 logo loading error: {e}")
            # If logo loading fails, don't show anything
            pass

    def add_ip_settings_section(self, parent):
        """Add IP settings section to the settings panel"""
        # Section container with improved styling
        section = tk.Frame(parent, bg="white", padx=20, pady=15)
        section.pack(fill="x", pady=(20, 10))
        
        # Section heading with icon
        heading_frame = tk.Frame(section, bg="white")
        heading_frame.pack(fill="x", pady=(0, 15))
        
        try:
            # Try to load network icon
            icon_path = "new_image/network_icon.png"
            if os.path.exists(icon_path):
                icon = Image.open(icon_path)
                icon = icon.resize((22, 22), Image.LANCZOS)
                self.network_icon = ImageTk.PhotoImage(icon)
                
                icon_label = tk.Label(heading_frame, image=self.network_icon, bg="white")
                icon_label.pack(side="left", padx=(0, 10))
        except Exception as e:
            print(f"Network icon loading error: {e}")
        
        heading = tk.Label(heading_frame, text="IP 설정", font=("Segoe UI", 12, "bold"), bg="white", fg=self.text_color)
        heading.pack(side="left")
        
        # IP address input with improved styling
        ip_frame = tk.Frame(section, bg="white")
        ip_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(ip_frame,
                text="IP 주소",
                bg="white",
                fg=self.text_color,
                font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 5))
        
        # Improved input container
        ip_container = tk.Frame(ip_frame, bg="#f8f9fa", highlightthickness=1, highlightbackground="#ced4da")
        ip_container.pack(fill="x", pady=(0, 15))
        
        ip_input = tk.Entry(ip_container,
                          font=("Segoe UI", 12),
                          bg="#f8f9fa",
                          fg=self.text_color,
                          bd=0,
                          highlightthickness=0,
                          relief=tk.FLAT)
        ip_input.pack(fill="x", expand=True, ipady=8, padx=10)
        ip_input.insert(0, self.load_ip())
        
        # Focus effects for IP input
        ip_input.bind("<FocusIn>", lambda e: ip_container.config(highlightbackground=self.primary_color))
        ip_input.bind("<FocusOut>", lambda e: ip_container.config(highlightbackground="#ced4da"))
        
        # Action buttons with improved styling
        button_frame = tk.Frame(section, bg="white")
        button_frame.pack(fill="x")
        
        # Create buttons with consistent styling
        save_btn = self.create_settings_button(button_frame, "설정 저장", lambda: self.save_ip(ip_input.get(), None))
        save_btn.pack(fill="x", pady=(0, 10))
        
        network_btn = self.create_settings_button(button_frame, "네트워크 설정", self.open_wifi_settings)
        network_btn.pack(fill="x")
        
        # Add a separator line
        separator = tk.Frame(parent, height=1, bg="#e0e0e0")
        separator.pack(fill="x", padx=15)

    def add_power_options_section(self, parent):
        """Add power options section to the settings panel"""
        section = tk.Frame(parent, bg="white", padx=20, pady=15)
        section.pack(fill="x", pady=(10, 20))
        
        # Section heading with icon
        heading_frame = tk.Frame(section, bg="white")
        heading_frame.pack(fill="x", pady=(0, 15))
        
        try:
            # Try to load power icon
            icon_path = "new_image/power_icon.png"
            if os.path.exists(icon_path):
                icon = Image.open(icon_path)
                icon = icon.resize((22, 22), Image.LANCZOS)
                self.power_icon = ImageTk.PhotoImage(icon)
                
                icon_label = tk.Label(heading_frame, image=self.power_icon, bg="white")
                icon_label.pack(side="left", padx=(0, 10))
        except Exception as e:
            print(f"Power icon loading error: {e}")
        
        heading = tk.Label(heading_frame, text="전원 옵션", font=("Segoe UI", 12, "bold"), bg="white", fg=self.text_color)
        heading.pack(side="left")
        
        # Power buttons with improved styling
        button_frame = tk.Frame(section, bg="white")
        button_frame.pack(fill="x")
        
        restart_btn = self.create_settings_button(button_frame, "전원 재시작", self.restart_system)
        restart_btn.pack(fill="x", pady=(0, 10))
        
        power_off_btn = self.create_settings_button(button_frame, "전원 종료", self.power_off_system)
        power_off_btn.pack(fill="x")

    def create_settings_button(self, parent, text, command):
        """Create a consistently styled button for settings panel"""
        button = tk.Button(parent,
                          text=text,
                          command=command,
                          bg=self.primary_color,
                          fg="white",
                          font=("Segoe UI", 11),
                          bd=0,
                          padx=10,
                          pady=8,  # Slightly increased padding
                          relief=tk.FLAT,
                          activebackground=self.secondary_color,
                          cursor="hand2",
                          highlightthickness=0)
        
        # Add hover effects
        button.bind("<Enter>", lambda e: button.config(bg=self.secondary_color))
        button.bind("<Leave>", lambda e: button.config(bg=self.primary_color))
        
        return button

if __name__ == "__main__":
    root = tk.Tk()
    app = RemminaRDPApp(root)
    root.mainloop()
