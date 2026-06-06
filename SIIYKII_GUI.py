# SIIYKII_GUI.py
# Compact Cyberpunk RF4S GUI

import customtkinter as ctk
import subprocess
import threading

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class SIIYKII_GUI(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("SIIYKII PRIVATE BUILD")
        self.geometry("720x820")
        self.resizable(False, False)

        self.process = None

        # =========================
        # HEADER
        # =========================
        self.header = ctk.CTkLabel(
            self,
            text="SIIYKII PRIVATE BUILD",
            font=("Orbitron", 24, "bold"),
            text_color="#00FFFF"
        )
        self.header.pack(pady=15)

        # =========================
        # SHORTCUT FRAME
        # =========================
        self.shortcut_frame = ctk.CTkFrame(self)
        self.shortcut_frame.pack(padx=15, pady=10, fill="x")

        shortcuts = [
            ("🎯 Jig Step", 14),
            ("🐕 Walk Dog", 12),
            ("🌀 Spin", 0),
            ("🐟 Bottom", 15),
            ("🌊 Waky Drift", 34),
        ]

        for name, pid in shortcuts:
            btn = ctk.CTkButton(
                self.shortcut_frame,
                text=name,
                height=42,
                fg_color="#1a1a1a",
                hover_color="#00FFFF",
                border_width=2,
                border_color="#00FFFF",
                command=lambda pid=pid: self.start_bot(pid)
            )
            btn.pack(padx=8, pady=8, fill="x")

        # =========================
        # CONTROL FRAME
        # =========================
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.pack(padx=15, pady=10, fill="x")

        self.start_btn = ctk.CTkButton(
            self.control_frame,
            text="▶ START",
            fg_color="#00aa00",
            hover_color="#00ff00",
            command=lambda: self.start_bot(0)
        )
        self.start_btn.pack(side="left", padx=10, pady=10, expand=True, fill="x")

        self.stop_btn = ctk.CTkButton(
            self.control_frame,
            text="■ STOP",
            fg_color="#aa0000",
            hover_color="#ff0000",
            command=self.stop_bot
        )
        self.stop_btn.pack(side="left", padx=10, pady=10, expand=True, fill="x")

        # =========================
        # STATS FRAME
        # =========================
        self.stats_frame = ctk.CTkFrame(self)
        self.stats_frame.pack(padx=15, pady=10, fill="x")

        self.stats = {
            "Fish Caught": "0",
            "Keep(Tag)": "0",
            "Yellow Tag": "0",
            "Blue Tag": "0",
            "Coffee Use": "0"
        }

        for key in self.stats:
            label = ctk.CTkLabel(
                self.stats_frame,
                text=f"{key}: {self.stats[key]}",
                font=("Consolas", 14),
                anchor="w"
            )
            label.pack(anchor="w", padx=10, pady=2)

        # =========================
        # CONSOLE
        # =========================
        self.console = ctk.CTkTextbox(
            self,
            height=180,
            fg_color="#111111",
            border_color="#00FFFF",
            border_width=2,
            text_color="#00FFCC"
        )
        self.console.pack(padx=15, pady=10, fill="both", expand=True)

        self.log("SIIYKII GUI READY")

    # =========================
    # LOG SYSTEM
    # =========================
    def log(self, text):
        self.console.insert("end", f"{text}\n")
        self.console.see("end")

    # =========================
    # START BOT
    # =========================
    def start_bot(self, pid):
        print("BUTTON CLICKED", pid)
        if self.process:
            self.log("Bot already running.")
            return

        command = [
            "python",
            "main_SIIYKII_ultimate_build.py",
            "bot",
            "-t",
            "-c",
            "-s",
            "-R",
            "5",
            "-p",
            str(pid)
        ]

        self.log(f"COMMAND: {' '.join(command)}")

        try:

            import os

            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )

            self.log("BOT PROCESS STARTED")

            threading.Thread(
                target=self.read_output,
                daemon=True
            ).start()

        except Exception as e:
            self.log(f"ERROR: {e}")

    # =========================
    # READ OUTPUT
    # =========================
    def read_output(self):

        while self.process:

            output = self.process.stdout.readline()

            if output:
                self.log(output.strip())

            if self.process is None:
                break

            if self.process.poll() is not None:
                break

        self.log("BOT STOPPED")
        self.process = None

    # =========================
    # STOP BOT
    # =========================
    def stop_bot(self):

        if self.process:
            self.log("STOPPING BOT...")
            self.process.terminate()
            self.log("BOT TERMINATED")
            self.process = None

        else:
            self.log("NO BOT RUNNING")


if __name__ == "__main__":
    app = SIIYKII_GUI()
    app.mainloop()