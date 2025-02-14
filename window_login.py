import tkinter as tk
import subprocess
import os
import time
from PIL import Image, ImageTk


class RDPLoginApp(tk.Tk):
    """A Tkinter application for logging into an RDP session using xfreerdp and benchmarking the connection."""

    def __init__(self):
        super().__init__()
        self.title("RDP Login")
        self.ip_file = "ip_address.txt"
        self.bg_image_path = "image/background_image.jpg"
        self.sims_logo_path = "image/sims_logo.png"
        self.soft11_logo_path = "image/soft11_logo.png"

        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.geometry(f"{self.screen_width}x{self.screen_height}")

        self._create_widgets()
        self.after(500, lambda: self.attributes("-fullscreen", True))  # Delayed fullscreen

    def _create_widgets(self):
        """Create and layout the main UI widgets."""
        self._load_background()
        self._create_login_frame()
        self._create_settings_button()
        self._create_message_label()

    def _load_background(self):
        """Load and display the background image."""
        bg_image = Image.open(self.bg_image_path)
        bg_image = bg_image.resize((self.screen_width, self.screen_height), Image.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(self, image=self.bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    def _create_login_frame(self):
        """Create the login frame containing logos, user inputs, and the login button."""
        self.login_frame = tk.Frame(self, bg="#abdbe3", bd=2, relief=tk.SOLID)
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

        self._create_logo_section()
        self._create_input_fields()
        self._create_connect_button()

    def _create_logo_section(self):
        """Load and display the logos side by side."""
        logos_frame = tk.Frame(self.login_frame, bg="#abdbe3")
        logos_frame.pack(pady=(30, 20))

        sims_logo = Image.open(self.sims_logo_path).resize((200, 100), Image.LANCZOS)
        soft11_logo = Image.open(self.soft11_logo_path).resize((200, 100), Image.LANCZOS)
        self.sims_photo = ImageTk.PhotoImage(sims_logo)
        self.soft11_photo = ImageTk.PhotoImage(soft11_logo)

        soft11_logo_label = tk.Label(logos_frame, image=self.soft11_photo, bg="#abdbe3")
        soft11_logo_label.pack(side=tk.LEFT, padx=10)
        sims_logo_label = tk.Label(logos_frame, image=self.sims_photo, bg="#abdbe3")
        sims_logo_label.pack(side=tk.LEFT, padx=10)

    def _create_input_fields(self):
        """Create the username and password entry fields."""
        # Username
        username_label = tk.Label(
            self.login_frame, text="Username", bg="#abdbe3", fg="#1E3F66", font=("Helvetica", 14)
        )
        username_label.pack(anchor="w", padx=30, pady=(0, 5))
        self.username_entry = tk.Entry(
            self.login_frame,
            font=("Helvetica", 16),
            bg="#abdbe3",
            bd=0,
            highlightthickness=1,
            highlightcolor="#1E3F66",
            width=25,
        )
        self.username_entry.pack(ipady=8, ipadx=8, padx=30, pady=(0, 15))

        # Password
        password_label = tk.Label(
            self.login_frame, text="Password", bg="#abdbe3", fg="#1E3F66", font=("Helvetica", 14)
        )
        password_label.pack(anchor="w", padx=30, pady=(0, 5))
        self.password_entry = tk.Entry(
            self.login_frame,
            font=("Helvetica", 16),
            bg="#abdbe3",
            bd=0,
            highlightthickness=1,
            highlightcolor="#1E3F66",
            show="•",
            width=25,
        )
        self.password_entry.pack(ipady=8, ipadx=8, padx=30, pady=(0, 20))

        # Bind events to clear any messages when user interacts with entries
        for entry in (self.username_entry, self.password_entry):
            entry.bind("<FocusIn>", self.clear_message)
            entry.bind("<Key>", self.clear_message)
            entry.bind("<Return>", lambda event: self.connect_rdp())

    def _create_connect_button(self):
        """Create the login/connect button."""
        self.connect_button = tk.Button(
            self.login_frame,
            text="LOGIN",
            command=self.connect_rdp,
            font=("Helvetica", 16, "bold"),
            bg="#7a6a6a",
            fg="white",
            bd=0,
            padx=30,
            pady=10,
        )
        self.connect_button.pack(pady=(0, 30))

    def _create_settings_button(self):
        """Create a settings button for changing the IP address."""
        settings_button = tk.Button(
            self,
            text="⚙️",
            command=self.open_settings,
            font=("Helvetica", 16),
            bg="white",
            fg="#1E3F66",
            bd=0,
        )
        settings_button.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=20)

    def _create_message_label(self):
        """Create the label used for displaying status and error messages."""
        self.message_label = tk.Label(self, font=("Helvetica", 12), bg="white", wraplength=500)

    def connect_rdp(self):
        """Attempt to connect using xfreerdp with the provided credentials and perform a benchmark."""
        ip_address = self.load_ip()
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not ip_address or not username or not password:
            self.show_error("Please fill in all fields and set IP in settings")
            return

        command = [
            "xfreerdp",
            f"/v:{ip_address}",
            f"/u:{username}",
            f"/p:{password}",
            "/f",  # fullscreen
            "/compression-level:2",
            "/gdi:hw",
            "/bpp:16",  # 16-bit color depth
            "/disable-wallpaper",
            "/disable-full-window-drag",
            "/disable-themes",
            "/disable-menu-animations",
            "/auto-reconnect",
            "/auto-reconnect-max-retries:3",
            "/network:auto",
            "+fonts",  # Enable font smoothing
            "/gfx:AVC444",  # Use AVC444 codec for better compression
            "/gfx-h264:AVC444",  # Use AVC444 for H.264 codec
        ]

        try:
            start_time = time.time()
            result = subprocess.run(command, capture_output=True, text=True)
            end_time = time.time()

            if result.returncode != 0:
                self.show_error(f"Error: Cannot Connect\n\nDetails: {result.stderr}")
            else:
                connection_time = end_time - start_time
                success_msg = f"Connection successful\nTime taken: {connection_time:.2f} seconds"
                benchmark_result = self.perform_benchmark(ip_address)
                full_msg = f"{success_msg}\n\nBenchmark Result:\n{benchmark_result}"
                self.show_message(full_msg, "#4CAF50")
        except Exception as e:
            self.show_error(f"Unexpected error: {str(e)}")

    def perform_benchmark(self, ip_address):
        """Perform a simple network benchmark using ping."""
        ping_command = ["ping", "-c", "10", ip_address]
        try:
            result = subprocess.run(ping_command, capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if "rtt min/avg/max/mdev" in line:
                    return line
            return "Benchmark failed: Could not parse ping results"
        except Exception as e:
            return f"Benchmark failed: {str(e)}"

    def show_error(self, message):
        """Display an error message."""
        self.message_label.config(text=message, fg="#F44336")
        self.message_label.place(relx=0.5, rely=0.9, anchor="center")

    def show_message(self, message, color="#000000"):
        """Display a status message."""
        self.message_label.config(text=message, fg=color)
        self.message_label.place(relx=0.5, rely=0.9, anchor="center")

    def clear_message(self, event=None):
        """Hide the message label."""
        self.message_label.place_forget()

    def open_settings(self):
        """Open the settings window to update the IP address."""
        settings_window = tk.Toplevel(self)
        settings_window.title("Settings")
        width, height = 300, 200
        x = (self.screen_width - width) // 2
        y = (self.screen_height - height) // 2
        settings_window.geometry(f"{width}x{height}+{x}+{y}")
        settings_window.configure(bg="white")

        ip_label = tk.Label(settings_window, text="IP Address:", bg="white", font=("Helvetica", 12))
        ip_label.pack(pady=(20, 5))

        ip_input = tk.Entry(
            settings_window,
            font=("Helvetica", 12),
            bg="white",
            bd=0,
            highlightthickness=1,
            highlightcolor="#4CAF50",
        )
        ip_input.pack(pady=5, padx=20, ipady=5, ipadx=5)
        ip_input.insert(0, self.load_ip())

        ip_input.bind("<Return>", lambda event: self.save_ip(ip_input.get(), settings_window))

        save_button = tk.Button(
            settings_window,
            text="Save",
            command=lambda: self.save_ip(ip_input.get(), settings_window),
            bg="#7a6a6a",
            fg="white",
            font=("Helvetica", 12),
            bd=0,
            padx=20,
            pady=5,
        )
        save_button.pack(pady=20)

    def save_ip(self, ip, window):
        """Save the provided IP address to a file and close the settings window."""
        with open(self.ip_file, "w") as f:
            f.write(ip)
        window.destroy()

    def load_ip(self):
        """Load the IP address from the file, if it exists."""
        if os.path.exists(self.ip_file):
            with open(self.ip_file, "r") as f:
                return f.read().strip()
        return ""

    def toggle_fullscreen(self, event=None):
        """Toggle the fullscreen mode."""
        current = self.attributes("-fullscreen")
        self.attributes("-fullscreen", not current)


if __name__ == "__main__":
    app = RDPLoginApp()
    app.mainloop()
