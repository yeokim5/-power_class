import tkinter as tk
from tkinter import messagebox
import subprocess
import os
from PIL import Image, ImageTk
import time
import configparser
import threading
import socket
import evdev
from evdev import ecodes, InputDevice, UInput
import glob
import sys
import select

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

        self.keyboard_blocked = False
        self.keyboard_blocker_thread = None
        self.keyboard_devices = []
        self.setup_ui()

    def setup_ui(self):
        self.root.attributes('-fullscreen', True)
        self.load_background_image()
        self.create_login_frame()
        self.create_message_label()
        self.create_settings_button()

    def load_background_image(self):
        try:
            bg_image_path = "image/background.jpg"
            bg_image = Image.open(bg_image_path)
            bg_image = bg_image.resize((self.root.winfo_screenwidth(),
                                      self.root.winfo_screenheight()), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            bg_label = tk.Label(self.root, image=self.bg_photo, bg="#f5f6f5")
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except:
            # 이미지 로드 실패 시 대체 그라데이션
            bg_label = tk.Label(self.root, bg="#f5f6f5")
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    def create_login_frame(self):
        # 미묘한 그림자와 둥근 모서리가 있는 카드
        login_frame = tk.Frame(self.root, bg="white", padx=40, pady=40)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")
        login_frame.configure(bd=0, highlightthickness=0)
        # 그림자 효과 추가
        login_frame.config(highlightbackground="#dcdcdc", highlightcolor="#dcdcdc",
                          highlightthickness=1)

        # Load and display logo image
        try:
            logo_path = "image/power_client_logo.png"
            logo_image = Image.open(logo_path)
            
            # Get original dimensions
            original_width, original_height = logo_image.size
            
            # Calculate new dimensions maintaining aspect ratio
            # Let's scale it to 50% of original size (you can adjust this factor)
            scale_factor = 1.5
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            
            logo_image = logo_image.resize((new_width, new_height), Image.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(login_frame, image=self.logo_photo, bg="white")
            logo_label.pack(pady=(0, 40))
        except Exception as e:
            # Fallback to text if image loading fails
            title_label = tk.Label(login_frame,
                                 text="PowerClient RDP",
                                 bg="white",
                                 fg=self.text_color,
                                 font=("Segoe UI", 26, "bold"))
            title_label.pack(pady=(0, 40))

        # 입력 필드
        self.create_entry(login_frame, "사용자 이름", "username_entry")
        self.create_entry(login_frame, "비밀번호", "password_entry", show="●")

        # 호버 효과가 있는 연결 버튼
        connect_button = tk.Button(login_frame,
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
        # 호버 효과 추가
        connect_button.bind("<Enter>", lambda e:	 	connect_button.config(bg=self.secondary_color))
        connect_button.bind("<Leave>", lambda e: connect_button.config(bg=self.primary_color))
        
    def create_entry(self, parent, label_text, entry_var, show=""):
        entry_frame = tk.Frame(parent, bg="white")
        entry_frame.pack(fill="x", pady=12)

        label = tk.Label(entry_frame,
                        text=label_text,
                        bg="white",
                        fg=self.text_color,
                        font=("Segoe UI", 11, "bold"))
        label.pack(anchor="w")

        entry = tk.Entry(entry_frame,
                        font=("Segoe UI", 12),
                        bg="#f8f9fa",
                        fg=self.text_color,
                        bd=0,
                        highlightthickness=1,
                        highlightcolor=self.secondary_color,
                        highlightbackground="#ced4da",
                        relief=tk.FLAT,
                        show=show)
        entry.pack(fill="x", pady=(4, 0), ipady=8)

        setattr(self, entry_var, entry)
        entry.bind("<FocusIn>", lambda e: entry.config(highlightcolor=self.primary_color))
        entry.bind("<FocusOut>", lambda e: entry.config(highlightcolor="#ced4da"))
        entry.bind("<Key>", self.clear_message)
        entry.bind("<Return>", lambda event: self.connect_rdp())

    def create_message_label(self):
        self.message_label = tk.Label(self.root,
                                    font=("Segoe UI", 11),
                                    bg="white",
                                    fg=self.text_color,
                                    wraplength=600,
                                    pady=10,
                                    bd=1,
                                    relief="flat")

    def create_settings_button(self):
        settings_button = tk.Button(self.root,
                                  text="⚙️",
                                  command=self.open_settings,
                                  font=("Segoe UI", 12),  # 폰트 크기 증가
                                  bg="#ffffff",
                                  fg=self.text_color,
                                  bd=0,
                                  padx=10,
                                  pady=5,
                                  relief=tk.FLAT,
                                  activebackground="#e9ecef",
                                  cursor="hand2")
        settings_button.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=20)
        settings_button.config(highlightbackground="#dcdcdc", highlightthickness=1)

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
        
        # Start keyboard blocking before launching Remmina
        self.start_keyboard_blocking()
        
        # Add a small delay to ensure keyboard blocking is in effect
        time.sleep(1)
        
        # Launch Remmina with special parameters to help with keyboard grabbing
        env = os.environ.copy()
        env["REMMINA_DISABLE_SHORTCUTS"] = "1"  # Custom env var that some Remmina builds recognize
        
        # Create a wrapper script to launch Remmina with the right parameters
        wrapper_script = "/tmp/launch_remmina.sh"
        with open(wrapper_script, "w") as f:
            f.write(f"""#!/bin/bash
# Launch Remmina with keyboard grabbing enabled
export REMMINA_DISABLE_SHORTCUTS=1
export REMMINA_KEYBOARD_GRAB=1

# For Wayland, set some environment variables that might help
if [ "$XDG_SESSION_TYPE" = "wayland" ]; then
    export GDK_BACKEND=x11
fi

# Launch Remmina
remmina -c "{connection_file}"
""")
        os.chmod(wrapper_script, 0o755)
        
        # Run the wrapper script
        result = subprocess.run([wrapper_script], env=env, capture_output=True, text=True)
        
        # Stop keyboard blocking after Remmina closes
        self.stop_keyboard_blocking()
        
        end_time = time.time()

        os.remove(connection_file)
        os.remove(wrapper_script)

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
            'quality': '9',
            'grab_keyboard': '1',
            'keyboard_grab': '1',  # Additional setting for newer Remmina versions
            'keyboard_grab_policy': '2',  # Force grab
            'hostkey': '65508'
        }

        temp_file = os.path.expanduser('~/.local/share/remmina/temp.remmina')
        os.makedirs(os.path.dirname(temp_file), exist_ok=True)
        with open(temp_file, 'w') as configfile:
            config.write(configfile)
        
        return temp_file

        
    def show_error(self, message):
        self.message_label.config(text=message, fg=self.error_color)
        self.message_label.place(relx=0.5, rely=0.85, anchor="center")

    def show_message(self, message, color="#666666"):
        self.message_label.config(text=message, fg=color)
        self.message_label.place(relx=0.5, rely=0.85, anchor="center")

    def clear_message(self, *args):
        self.message_label.place_forget()

    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("설정")
        settings_window.configure(bg="white")

        width, height = 400, 400
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        settings_window.geometry(f"{width}x{height}+{x}+{y}")

        tk.Label(settings_window,
                text="설정",
                bg="white",
                fg=self.text_color,
                font=("Segoe UI", 16, "bold")).pack(pady=(20, 20))

        # IP 주소 입력 필드
        ip_frame = tk.Frame(settings_window, bg="white")
        ip_frame.pack(fill="x", padx=40, pady=10)

        tk.Label(ip_frame,
                text="IP 주소",
                bg="white",
                fg=self.text_color,
                font=("Segoe UI", 11, "bold")).pack(anchor="w")

        ip_input = tk.Entry(ip_frame,
                          font=("Segoe UI", 12),
                          bg="#f8f9fa",
                          fg=self.text_color,
                          bd=0,
                          highlightthickness=1,
                          highlightcolor=self.secondary_color,
                          highlightbackground="#ced4da",
                          relief=tk.FLAT)
        ip_input.pack(fill="x", pady=(4, 0), ipady=8)
        ip_input.insert(0, self.load_ip())

        # 버튼
        buttons_frame = tk.Frame(settings_window, bg="white")
        buttons_frame.pack(fill="x", padx=40, pady=20)

        for text, cmd in [("설정 저장", lambda: self.save_ip(ip_input.get(), settings_window)),
                         ("네트워크 설정", self.open_wifi_settings),
                         ("전원 옵션", self.show_power_options)]:
            btn = tk.Button(buttons_frame,
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
            btn.pack(fill="x", pady=6)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.secondary_color))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.primary_color))

    def save_ip(self, ip, window):
        with open("ip_address.txt", "w") as f:
            f.write(ip.strip())
        self.show_message("설정이 저장되었습니다", self.success_color)
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
                        self.stop_keyboard_blocking()  # Ensure keyboard is unblocked when connection ends
                        break
                except:
                    self.root.after(0, self.show_error, "모니터링 실패")
                    self.stop_keyboard_blocking()  # Ensure keyboard is unblocked on error
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
        subprocess.run(["systemctl", "reboot"])

    def power_off_system(self):
        subprocess.run(["systemctl", "poweroff"])

    def find_keyboard_devices(self):
        """Find all keyboard input devices using multiple methods to ensure success"""
        keyboards = []
        
        try:
            # Method 1: Use evdev
            try:
                devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
                for device in devices:
                    capabilities = device.capabilities()
                    # Check if device has keys (is a keyboard)
                    if ecodes.EV_KEY in capabilities:
                        # Check if it has typical keyboard keys
                        if any(key in capabilities[ecodes.EV_KEY] for key in 
                              [ecodes.KEY_A, ecodes.KEY_SPACE, ecodes.KEY_1]):
                            keyboards.append(device)
            except Exception as e:
                self.show_message(f"evdev 검색 실패, 대체 방법 시도 중...", "#666666")
            
            # Method 2: Use /proc/bus/input/devices if evdev failed
            if not keyboards:
                try:
                    result = subprocess.run(
                        ["grep", "-l", "Handlers\\|EV=", "/proc/bus/input/devices"], 
                        capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        device_info = result.stdout
                        
                        # Find lines with keyboard indicators
                        keyboard_lines = subprocess.run(
                            ["grep", "-l", "EV=.*120013", "/proc/bus/input/devices"],
                            capture_output=True, text=True
                        ).stdout
                        
                        # Extract event device numbers
                        event_devices = subprocess.run(
                            ["grep", "-o", "event[0-9]\\+", keyboard_lines],
                            capture_output=True, text=True
                        ).stdout.strip().split('\n')
                        
                        # Create InputDevice objects for each keyboard
                        for event in event_devices:
                            if event:
                                try:
                                    device = evdev.InputDevice(f"/dev/input/{event}")
                                    keyboards.append(device)
                                except:
                                    pass
                except Exception as e:
                    self.show_message(f"/proc 검색 실패, 다른 방법 시도 중...", "#666666")
            
            # Method 3: Use xinput as a last resort
            if not keyboards:
                try:
                    result = subprocess.run(
                        ["xinput", "list", "--name-only"], 
                        capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        devices = result.stdout.strip().split('\n')
                        for device_name in devices:
                            if "keyboard" in device_name.lower() or "keypad" in device_name.lower():
                                # We can't directly use these with evdev, but we'll handle them differently
                                keyboards.append({"name": device_name, "xinput": True})
                except Exception as e:
                    self.show_message(f"xinput 검색 실패", "#666666")
            
            # If we still don't have keyboards, try a direct approach
            if not keyboards:
                # Just look for any input device that might be a keyboard
                for path in glob.glob("/dev/input/event*"):
                    try:
                        device = evdev.InputDevice(path)
                        capabilities = device.capabilities()
                        if ecodes.EV_KEY in capabilities:
                            keyboards.append(device)
                    except:
                        pass
        
        except Exception as e:
            self.show_error(f"키보드 장치 검색 실패: {str(e)}")
        
        return keyboards

    def start_keyboard_blocking(self):
        """Start blocking keyboard input on the local machine using a simpler, more reliable approach"""
        if self.keyboard_blocked:
            return
            
        try:
            # Create a script that will disable system keys using multiple methods
            disable_script = "/tmp/disable_system_keys.sh"
            with open(disable_script, "w") as f:
                f.write("""#!/bin/bash
# This script disables system keys using multiple methods for maximum compatibility

# 1. Disable GNOME keyboard shortcuts (works in both X11 and Wayland)
gsettings set org.gnome.desktop.wm.keybindings switch-applications "[]"
gsettings set org.gnome.desktop.wm.keybindings switch-applications-backward "[]"
gsettings set org.gnome.desktop.wm.keybindings panel-main-menu "[]"
gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-left "[]"
gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-right "[]"
gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-up "[]"
gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-down "[]"
gsettings set org.gnome.mutter overlay-key ""

# 2. For Wayland, set XWayland grab access rules
if [ "$XDG_SESSION_TYPE" = "wayland" ]; then
    gsettings set org.gnome.mutter.wayland xwayland-grab-access-rules "['Remmina', 'remmina']"
fi

# 3. For X11, use xmodmap to disable Super key
if [ "$XDG_SESSION_TYPE" = "x11" ]; then
    # Create an xmodmap file to disable Super key
    cat > /tmp/disable_super.xmodmap << EOL
clear mod4
keycode 133 = NoSymbol
keycode 134 = NoSymbol
EOL
    xmodmap /tmp/disable_super.xmodmap
fi

# 4. Use dconf directly (more reliable in some Wayland environments)
dconf write /org/gnome/desktop/wm/keybindings/switch-applications "[]"
dconf write /org/gnome/desktop/wm/keybindings/switch-applications-backward "[]"
dconf write /org/gnome/mutter/overlay-key "''"

# 5. Create a simple daemon to intercept Alt+Tab and Super key
cat > /tmp/key_interceptor.py << 'EOL'
#!/usr/bin/env python3
import subprocess
import time
import os
import signal
import sys

def run_command(cmd):
    try:
        subprocess.run(cmd, shell=True, check=False)
    except:
        pass

# Function to continuously disable problematic shortcuts
def disable_shortcuts():
    while True:
        # Check if Remmina is still running
        result = subprocess.run(["pgrep", "remmina"], capture_output=True)
        if result.returncode != 0:
            # Remmina is not running, exit
            sys.exit(0)
            
        # Disable Super key and Alt+Tab
        run_command("gsettings set org.gnome.mutter overlay-key \"\"")
        run_command("gsettings set org.gnome.desktop.wm.keybindings switch-applications \"[]\"")
        run_command("gsettings set org.gnome.desktop.wm.keybindings switch-applications-backward \"[]\"")
        
        # Sleep for a short time
        time.sleep(1)

# Handle termination gracefully
def handle_signal(sig, frame):
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)

# Start the main loop
disable_shortcuts()
EOL

chmod +x /tmp/key_interceptor.py
python3 /tmp/key_interceptor.py &
echo $! > /tmp/key_interceptor.pid

echo "System keys disabled"
""")
            os.chmod(disable_script, 0o755)
            
            # Run the script to disable system keys
            subprocess.run(["pkexec", disable_script], capture_output=True)
            
            # Create a script to restore keys
            restore_script = "/tmp/restore_system_keys.sh"
            with open(restore_script, "w") as f:
                f.write("""#!/bin/bash
# Restore normal keyboard functionality

# Kill the key interceptor process
if [ -f /tmp/key_interceptor.pid ]; then
    kill $(cat /tmp/key_interceptor.pid) 2>/dev/null || true
    rm /tmp/key_interceptor.pid
fi

# Reset GNOME settings
gsettings reset org.gnome.desktop.wm.keybindings switch-applications
gsettings reset org.gnome.desktop.wm.keybindings switch-applications-backward
gsettings reset org.gnome.desktop.wm.keybindings panel-main-menu
gsettings reset org.gnome.desktop.wm.keybindings switch-to-workspace-left
gsettings reset org.gnome.desktop.wm.keybindings switch-to-workspace-right
gsettings reset org.gnome.desktop.wm.keybindings switch-to-workspace-up
gsettings reset org.gnome.desktop.wm.keybindings switch-to-workspace-down
gsettings reset org.gnome.mutter overlay-key

# Reset Wayland settings
if [ "$XDG_SESSION_TYPE" = "wayland" ]; then
    gsettings reset org.gnome.mutter.wayland xwayland-grab-access-rules
fi

# Reset X11 settings
if [ "$XDG_SESSION_TYPE" = "x11" ]; then
    setxkbmap -layout us
fi

# Reset dconf settings
dconf reset /org/gnome/desktop/wm/keybindings/switch-applications
dconf reset /org/gnome/desktop/wm/keybindings/switch-applications-backward
dconf reset /org/gnome/mutter/overlay-key

echo "System keys restored"
""")
            os.chmod(restore_script, 0o755)
            
            # Save the path to the restore script for later
            self.restore_script = restore_script
            
            # Set keyboard_blocked flag to true
            self.keyboard_blocked = True
            
            # We'll use a simpler approach that doesn't rely on finding keyboard devices
            # Just launch the background process to continuously disable shortcuts
            self.show_message("키보드가 원격 세션으로 전달됩니다", self.success_color)
        except Exception as e:
            self.show_error(f"키보드 차단 실패: {str(e)}")
            self.keyboard_blocked = False

    def stop_keyboard_blocking(self):
        """Stop blocking keyboard input"""
        self.keyboard_blocked = False
        
        # Run the restore script
        if hasattr(self, 'restore_script') and os.path.exists(self.restore_script):
            subprocess.run(["pkexec", self.restore_script], capture_output=True)
        
        self.show_message("로컬 키보드 입력이 복원되었습니다", self.success_color)

if __name__ == "__main__":
    # Check if we need root privileges for keyboard blocking
    if len(sys.argv) > 1 and sys.argv[1] == "--with-keyboard-blocking":
        if os.geteuid() != 0:
            print("키보드 차단을 위해 관리자 권한이 필요합니다")
            subprocess.run(["pkexec", sys.executable, sys.argv[0], "--with-keyboard-blocking"])
            sys.exit(0)
    
    root = tk.Tk()
    app = RemminaRDPApp(root)
    root.mainloop()
