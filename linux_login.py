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
        
        result = subprocess.run(["remmina", "-c", connection_file], capture_output=True, text=True)
        
        # Stop keyboard blocking after Remmina closes
        self.stop_keyboard_blocking()
        
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
            'quality': '9',
            'grab_keyboard': '1',
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
        """Find all keyboard input devices"""
        keyboards = []
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
            self.show_error(f"키보드 장치 검색 실패: {str(e)}")
        return keyboards

    def start_keyboard_blocking(self):
        """Start blocking keyboard input on the local machine"""
        if self.keyboard_blocked:
            return
            
        try:
            # Create a comprehensive script to disable all system keyboard shortcuts
            temp_script = "/tmp/disable_all_shortcuts.sh"
            with open(temp_script, "w") as f:
                f.write("""#!/bin/bash
# Completely disable all system keyboard shortcuts

# 1. Disable all GNOME keyboard shortcuts
gsettings set org.gnome.desktop.wm.keybindings panel-main-menu "[]"
gsettings set org.gnome.desktop.wm.keybindings close "[]"
gsettings set org.gnome.desktop.wm.keybindings maximize "[]"
gsettings set org.gnome.desktop.wm.keybindings minimize "[]"
gsettings set org.gnome.desktop.wm.keybindings toggle-maximized "[]"
gsettings set org.gnome.desktop.wm.keybindings activate-window-menu "[]"
gsettings set org.gnome.desktop.wm.keybindings begin-move "[]"
gsettings set org.gnome.desktop.wm.keybindings begin-resize "[]"
gsettings set org.gnome.desktop.wm.keybindings toggle-on-all-workspaces "[]"
gsettings set org.gnome.desktop.wm.keybindings switch-applications "[]"
gsettings set org.gnome.desktop.wm.keybindings switch-applications-backward "[]"
gsettings set org.gnome.desktop.wm.keybindings switch-windows "[]"
gsettings set org.gnome.desktop.wm.keybindings switch-windows-backward "[]"
gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-1 "[]"
gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-2 "[]"
gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-3 "[]"
gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-4 "[]"
gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-left "[]"
gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-right "[]"
gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-up "[]"
gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-down "[]"
gsettings set org.gnome.desktop.wm.keybindings move-to-workspace-1 "[]"
gsettings set org.gnome.desktop.wm.keybindings move-to-workspace-2 "[]"
gsettings set org.gnome.desktop.wm.keybindings move-to-workspace-3 "[]"
gsettings set org.gnome.desktop.wm.keybindings move-to-workspace-4 "[]"
gsettings set org.gnome.desktop.wm.keybindings move-to-workspace-left "[]"
gsettings set org.gnome.desktop.wm.keybindings move-to-workspace-right "[]"
gsettings set org.gnome.desktop.wm.keybindings move-to-workspace-up "[]"
gsettings set org.gnome.desktop.wm.keybindings move-to-workspace-down "[]"
gsettings set org.gnome.desktop.wm.keybindings move-to-corner-nw "[]"
gsettings set org.gnome.desktop.wm.keybindings move-to-corner-ne "[]"
gsettings set org.gnome.desktop.wm.keybindings move-to-corner-sw "[]"
gsettings set org.gnome.desktop.wm.keybindings move-to-corner-se "[]"
gsettings set org.gnome.desktop.wm.keybindings move-to-side-n "[]"
gsettings set org.gnome.desktop.wm.keybindings move-to-side-s "[]"
gsettings set org.gnome.desktop.wm.keybindings move-to-side-e "[]"
gsettings set org.gnome.desktop.wm.keybindings move-to-side-w "[]"
gsettings set org.gnome.desktop.wm.keybindings move-to-center "[]"

# 2. Disable media keys
gsettings set org.gnome.settings-daemon.plugins.media-keys volume-down "[]"
gsettings set org.gnome.settings-daemon.plugins.media-keys volume-up "[]"
gsettings set org.gnome.settings-daemon.plugins.media-keys volume-mute "[]"
gsettings set org.gnome.settings-daemon.plugins.media-keys play "[]"
gsettings set org.gnome.settings-daemon.plugins.media-keys pause "[]"
gsettings set org.gnome.settings-daemon.plugins.media-keys stop "[]"
gsettings set org.gnome.settings-daemon.plugins.media-keys next "[]"
gsettings set org.gnome.settings-daemon.plugins.media-keys previous "[]"
gsettings set org.gnome.settings-daemon.plugins.media-keys logout "[]"
gsettings set org.gnome.settings-daemon.plugins.media-keys eject "[]"
gsettings set org.gnome.settings-daemon.plugins.media-keys media "[]"
gsettings set org.gnome.settings-daemon.plugins.media-keys calculator "[]"
gsettings set org.gnome.settings-daemon.plugins.media-keys email "[]"
gsettings set org.gnome.settings-daemon.plugins.media-keys www "[]"
gsettings set org.gnome.settings-daemon.plugins.media-keys home "[]"
gsettings set org.gnome.settings-daemon.plugins.media-keys search "[]"
gsettings set org.gnome.settings-daemon.plugins.media-keys screensaver "[]"

# 3. Disable shell keybindings
gsettings set org.gnome.shell.keybindings toggle-overview "[]"
gsettings set org.gnome.shell.keybindings toggle-application-view "[]"
gsettings set org.gnome.shell.keybindings toggle-message-tray "[]"
gsettings set org.gnome.shell.keybindings focus-active-notification "[]"
gsettings set org.gnome.shell.keybindings toggle-quick-settings "[]"

# 4. Set Wayland to allow Remmina to grab keyboard
gsettings set org.gnome.mutter.wayland xwayland-grab-access-rules "['Remmina', 'remmina']"

# 5. Create an Xmodmap file to disable Super key
echo "keycode 133 = NoSymbol" > /tmp/disable_super.xmodmap
echo "keycode 134 = NoSymbol" >> /tmp/disable_super.xmodmap

# 6. Apply the Xmodmap if we're in X11
if [ "$XDG_SESSION_TYPE" = "x11" ]; then
    xmodmap /tmp/disable_super.xmodmap
fi

# 7. Use xinput to disable problematic keys directly
# Find all keyboard devices
for device in $(xinput list | grep -i keyboard | grep -v pointer | sed -n 's/.*id=\\([0-9]*\\).*/\\1/p'); do
    # Create a temporary mapping file that disables Super keys
    echo "keycode 133 = NoSymbol" > /tmp/disable_keys.xkb
    echo "keycode 134 = NoSymbol" >> /tmp/disable_keys.xkb
    
    # Apply the mapping to the device
    setxkbmap -device $device -print | xkbcomp -i $device - /tmp/xkb.dump
    xkbcomp -i $device /tmp/disable_keys.xkb $DISPLAY
done

# 8. For Wayland, use dconf directly as it's more reliable
dconf write /org/gnome/desktop/wm/keybindings/switch-applications "[]"
dconf write /org/gnome/desktop/wm/keybindings/switch-applications-backward "[]"
dconf write /org/gnome/mutter/wayland/xwayland-grab-access-rules "['Remmina', 'remmina']"

# 9. Disable GNOME Shell overlay key (Super key)
gsettings set org.gnome.mutter overlay-key ""
""")
            os.chmod(temp_script, 0o755)
            
            # Run the script to disable all shortcuts
            subprocess.run(["pkexec", temp_script], capture_output=True)
            
            # Now proceed with keyboard grabbing
            if os.geteuid() != 0:
                # Restart the script with sudo for keyboard grabbing
                result = subprocess.run(["pkexec", sys.executable] + sys.argv + ["--with-keyboard-blocking"], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    self.show_error("관리자 권한을 얻지 못했습니다. 키보드 차단이 작동하지 않을 수 있습니다.")
                    return
                    
            self.keyboard_devices = self.find_keyboard_devices()
            if not self.keyboard_devices:
                self.show_error("키보드 장치를 찾을 수 없습니다")
                return
                
            self.keyboard_blocked = True
            self.keyboard_blocker_thread = threading.Thread(
                target=self.block_keyboard, 
                daemon=True
            )
            self.keyboard_blocker_thread.start()
            
            # Also launch a separate process to monitor and intercept Super key presses
            self.launch_super_key_blocker()
            
            self.show_message("키보드가 원격 세션으로 전달됩니다", self.success_color)
        except Exception as e:
            self.show_error(f"키보드 차단 실패: {str(e)}")
            self.keyboard_blocked = False

    def launch_super_key_blocker(self):
        """Launch a separate process to specifically block Super key"""
        blocker_script = "/tmp/super_key_blocker.py"
        with open(blocker_script, "w") as f:
            f.write("""#!/usr/bin/env python3
import evdev
from evdev import ecodes, InputDevice, UInput
import select
import sys
import time

# Find all keyboard devices
keyboards = []
for path in evdev.list_devices():
    try:
        device = evdev.InputDevice(path)
        capabilities = device.capabilities()
        if ecodes.EV_KEY in capabilities:
            if any(key in capabilities[ecodes.EV_KEY] for key in 
                  [ecodes.KEY_A, ecodes.KEY_SPACE, ecodes.KEY_1]):
                keyboards.append(device)
    except:
        pass

if not keyboards:
    print("No keyboard devices found")
    sys.exit(1)

# Try to grab all keyboard devices
grabbed_devices = []
for device in keyboards:
    try:
        device.grab()
        grabbed_devices.append(device)
    except:
        print(f"Failed to grab {device.name}")

if not grabbed_devices:
    print("Could not grab any keyboard devices")
    sys.exit(1)

# Create a virtual keyboard to forward events
ui_capabilities = {
    ecodes.EV_KEY: grabbed_devices[0].capabilities().get(ecodes.EV_KEY, []),
    ecodes.EV_SYN: [],
}

try:
    with UInput(ui_capabilities, name="remmina-virtual-keyboard") as ui:
        # Track special key states
        special_keys = {
            ecodes.KEY_LEFTALT: False,
            ecodes.KEY_RIGHTALT: False,
            ecodes.KEY_TAB: False,
            ecodes.KEY_LEFTMETA: False,
            ecodes.KEY_RIGHTMETA: False
        }
        
        print("Super key blocker running...")
        
        # Main event loop
        while True:
            devices_to_read = []
            for device in grabbed_devices:
                try:
                    devices_to_read.append(device.fd)
                except:
                    continue
                    
            if not devices_to_read:
                break
                
            r, w, x = select.select(devices_to_read, [], [], 0.1)
            
            for fd in r:
                for device in grabbed_devices:
                    if device.fd == fd:
                        try:
                            for event in device.read():
                                if event.type == ecodes.EV_KEY:
                                    # Track special key states
                                    if event.code in special_keys:
                                        special_keys[event.code] = (event.value == 1 or event.value == 2)
                                    
                                    # Always forward the event
                                    ui.write(event.type, event.code, event.value)
                                    ui.syn()
                                    
                                    # Special handling for Alt+Tab
                                    alt_pressed = special_keys[ecodes.KEY_LEFTALT] or special_keys[ecodes.KEY_RIGHTALT]
                                    if alt_pressed and event.code == ecodes.KEY_TAB:
                                        time.sleep(0.01)
                                        if special_keys[ecodes.KEY_LEFTALT]:
                                            ui.write(ecodes.EV_KEY, ecodes.KEY_LEFTALT, event.value)
                                        if special_keys[ecodes.KEY_RIGHTALT]:
                                            ui.write(ecodes.EV_KEY, ecodes.KEY_RIGHTALT, event.value)
                                        ui.write(ecodes.EV_KEY, ecodes.KEY_TAB, event.value)
                                        ui.syn()
                                    
                                    # Special handling for Super key
                                    if event.code in [ecodes.KEY_LEFTMETA, ecodes.KEY_RIGHTMETA]:
                                        time.sleep(0.01)
                                        ui.write(ecodes.EV_KEY, event.code, event.value)
                                        ui.syn()
                        except:
                            continue
except KeyboardInterrupt:
    pass
finally:
    # Release all grabbed devices
    for device in grabbed_devices:
        try:
            device.ungrab()
        except:
            pass
""")
        os.chmod(blocker_script, 0o755)
        
        # Launch the blocker script with sudo
        subprocess.Popen(["pkexec", "python3", blocker_script], 
                       stdout=subprocess.PIPE, 
                       stderr=subprocess.PIPE)

    def stop_keyboard_blocking(self):
        """Stop blocking keyboard input"""
        self.keyboard_blocked = False
        if self.keyboard_blocker_thread:
            # Thread will exit on its own when keyboard_blocked becomes False
            self.keyboard_blocker_thread = None
            
            # Kill the super key blocker process
            subprocess.run(["pkill", "-f", "super_key_blocker.py"], capture_output=True)
            
            # Restore all keyboard shortcuts
            restore_script = "/tmp/restore_all_shortcuts.sh"
            with open(restore_script, "w") as f:
                f.write("""#!/bin/bash
# Reset all GNOME keyboard shortcuts
gsettings reset-recursively org.gnome.desktop.wm.keybindings
gsettings reset-recursively org.gnome.settings-daemon.plugins.media-keys
gsettings reset-recursively org.gnome.shell.keybindings
gsettings reset org.gnome.mutter.wayland xwayland-grab-access-rules
gsettings reset org.gnome.mutter overlay-key

# Reset xmodmap if in X11
if [ "$XDG_SESSION_TYPE" = "x11" ]; then
    setxkbmap -layout us  # Reset to default keyboard layout
fi

# Reset xinput settings
for device in $(xinput list | grep -i keyboard | grep -v pointer | sed -n 's/.*id=\\([0-9]*\\).*/\\1/p'); do
    setxkbmap -device $device -layout us
done
""")
            os.chmod(restore_script, 0o755)
            subprocess.run(["pkexec", restore_script], capture_output=True)
            
            self.show_message("로컬 키보드 입력이 복원되었습니다", self.success_color)

    def block_keyboard(self):
        """Block all keyboard events by grabbing devices exclusively"""
        grabbed_devices = []
        
        try:
            # Try to grab all keyboard devices
            for device in self.keyboard_devices:
                try:
                    device.grab()
                    grabbed_devices.append(device)
                except Exception as e:
                    self.show_error(f"키보드 장치 '{device.name}' 차단 실패: {str(e)}")
            
            # If we couldn't grab any devices, exit
            if not grabbed_devices:
                self.show_error("키보드 차단 실패: 장치를 차단할 수 없습니다")
                self.keyboard_blocked = False
                return
                
            # Create a virtual keyboard to forward events to Remmina
            ui_capabilities = {
                ecodes.EV_KEY: grabbed_devices[0].capabilities().get(ecodes.EV_KEY, []),
                ecodes.EV_SYN: [],
            }
            
            # Set up a mapping for special keys that need special handling
            special_keys = {
                ecodes.KEY_LEFTALT: False,  # Track Alt key state
                ecodes.KEY_RIGHTALT: False, # Track Alt key state
                ecodes.KEY_TAB: False,      # Track Tab key state
                ecodes.KEY_LEFTMETA: False, # Track Windows/Super key state
                ecodes.KEY_RIGHTMETA: False # Track Windows/Super key state
            }
            
            with UInput(ui_capabilities, name="remmina-virtual-keyboard") as ui:
                # Main event loop - intercept and forward events
                while self.keyboard_blocked:
                    for device in grabbed_devices:
                        try:
                            # Non-blocking read with timeout
                            r, w, x = select.select([device.fd], [], [], 0.1)
                            if r:
                                for event in device.read():
                                    if event.type == ecodes.EV_KEY:
                                        # Track state of special keys
                                        if event.code in special_keys:
                                            special_keys[event.code] = (event.value == 1 or event.value == 2)
                                            
                                        # Handle Alt+Tab specifically
                                        alt_pressed = special_keys[ecodes.KEY_LEFTALT] or special_keys[ecodes.KEY_RIGHTALT]
                                        
                                        # Always forward the event to our virtual keyboard
                                        ui.write(event.type, event.code, event.value)
                                        ui.syn()
                                        
                                        # For Alt+Tab, send an additional event to ensure it's captured
                                        if alt_pressed and event.code == ecodes.KEY_TAB:
                                            # Send a small delay to help the remote system distinguish the key combo
                                            time.sleep(0.01)
                                            # Resend the Alt key to ensure it's recognized in combination
                                            if special_keys[ecodes.KEY_LEFTALT]:
                                                ui.write(ecodes.EV_KEY, ecodes.KEY_LEFTALT, event.value)
                                            if special_keys[ecodes.KEY_RIGHTALT]:
                                                ui.write(ecodes.EV_KEY, ecodes.KEY_RIGHTALT, event.value)
                                            ui.write(ecodes.EV_KEY, ecodes.KEY_TAB, event.value)
                                            ui.syn()
                                        
                                        # For Windows/Super key, ensure it's properly forwarded
                                        if event.code in [ecodes.KEY_LEFTMETA, ecodes.KEY_RIGHTMETA]:
                                            # Send an additional event to ensure it's captured
                                            time.sleep(0.01)
                                            ui.write(ecodes.EV_KEY, event.code, event.value)
                                            ui.syn()
                        except Exception as e:
                            # Device might have been disconnected
                            continue
        
        except Exception as e:
            self.show_error(f"키보드 차단 중 오류 발생: {str(e)}")
        
        finally:
            # Release all grabbed devices
            for device in grabbed_devices:
                try:
                    device.ungrab()
                except:
                    pass
            
            self.keyboard_blocked = False

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
