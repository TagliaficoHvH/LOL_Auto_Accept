"""
LoL Auto Accept with GUI, screen detection, and hotkey toggle using pynput.

Requirements (install with pip):
    pip install pyautogui opencv-python pillow pynput

Notes:
- Works on any resolution as long as the template matches.
- pyautogui has a failsafe that aborts if you slam the mouse into a corner; disable if needed.
- Automating LoL may violate Riot’s Terms of Service. Use at your own risk.
"""
import os
import threading
import time
from pathlib import Path

import cv2
import numpy as np
import pyautogui
import tkinter as tk
from tkinter import ttk
from pynput import keyboard

# ------------ CONFIGURATION ------------
TEMPLATE_PATH = Path("accept_template.png")  # Screenshot of the Accept button
CHECK_INTERVAL = 4                            # Seconds between checks
DEFAULT_HOTKEY = "<f8>"                       # Toggle key (pynput format)
THRESHOLD = 0.5                               # Template‑matching threshold

class AutoAcceptApp:
    def __init__(self):
        if not TEMPLATE_PATH.exists():
            raise FileNotFoundError(
                f"Template image '{TEMPLATE_PATH}' not found. Capture the Accept button and save it there.")

        self.template = cv2.imread(str(TEMPLATE_PATH), cv2.IMREAD_GRAYSCALE)
        self.temp_h, self.temp_w = self.template.shape[:2]

        self.enabled = False
        self.hotkey = DEFAULT_HOTKEY

        # --- GUI ---
        self.root = tk.Tk()
        self.root.title("LoL Auto Accept")
        self.root.geometry("300x170")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(False, False)

        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TCheckbutton", background="#1e1e1e", foreground="white")
        style.configure("TLabel", background="#1e1e1e", foreground="white")
        style.map("TCheckbutton", background=[], foreground=[])

        self.var_enable = tk.BooleanVar()
        chk = ttk.Checkbutton(self.root, text="Enable Auto‑Accept", variable=self.var_enable,
                               command=self.toggle)
        chk.pack(pady=20)

        self.lbl_status = ttk.Label(self.root, text="Inactive", font=("Segoe UI", 12, "bold"), foreground="red")
        self.lbl_status.pack(pady=6)

        self.footer = ttk.Label(self.root, text="Press F8 to toggle Auto‑Accept", font=("Segoe UI", 8))
        self.footer.pack(pady=10)

        # Start worker threads
        self.listener_thread = threading.Thread(target=self.start_hotkey_listener, daemon=True)
        self.listener_thread.start()

        self.worker_thread = threading.Thread(target=self.worker, daemon=True)
        self.worker_thread.start()

        self.root.mainloop()

    def start_hotkey_listener(self):
        def on_press(key):
            try:
                if key == keyboard.Key.f8:
                    self.var_enable.set(not self.var_enable.get())
                    self.toggle()
            except Exception:
                pass

        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()

    def toggle(self):
        self.enabled = self.var_enable.get()
        self.lbl_status.config(text="Active" if self.enabled else "Inactive",
                               foreground="lime" if self.enabled else "red")

    def worker(self):
        while True:
            if self.enabled:
                screenshot = pyautogui.screenshot()
                gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2GRAY)
                res = cv2.matchTemplate(gray, self.template, cv2.TM_CCOEFF_NORMED)
                loc = np.where(res >= THRESHOLD)
                if loc[0].size:
                    y, x = int(loc[0][0]), int(loc[1][0])
                    pyautogui.moveTo(x + self.temp_w // 2, y + self.temp_h // 2)
                    pyautogui.click()
            time.sleep(CHECK_INTERVAL)

# ------------- Main -------------
if __name__ == "__main__":
    AutoAcceptApp()
