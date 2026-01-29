import os
import sys
import json
import time
import base64
import hashlib
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk

# =========================
# CONSTANTS
# =========================
SAVE_KEY = "8724ff54-03f7-4585-9871-edd2073dea7d"
DEV_PASSWORD = "OxioDev-1234"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIE_IMG_PATH = os.path.join(BASE_DIR, "cookie.png")
SAVE_FILE = os.path.join(BASE_DIR, "save.dat")

# =========================
# GAME VARIABLES
# =========================
cookies = 0
cookies_per_click = 1
auto_clickers = 0
auto_clicker_cost = 50
upgrade_cost = 20

# =========================
# ENCRYPTION
# =========================
def _xor(data: bytes, key: str) -> bytes:
    key = key.encode()
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

def generate_signature(data: dict) -> str:
    raw = json.dumps(data, sort_keys=True).encode()
    return hashlib.sha256(raw + SAVE_KEY.encode()).hexdigest()

# =========================
# SAVE / LOAD (ANTI-CHEAT)
# =========================
def save_game():
    data = {
        "cookies": cookies,
        "cookies_per_click": cookies_per_click,
        "auto_clickers": auto_clickers,
        "auto_clicker_cost": auto_clicker_cost,
        "upgrade_cost": upgrade_cost,
        "time": int(time.time())
    }

    data["signature"] = generate_signature(data)

    raw = json.dumps(data).encode()
    encrypted = _xor(raw, SAVE_KEY)
    encoded = base64.b64encode(encrypted)

    with open(SAVE_FILE, "wb") as f:
        f.write(encoded)

def load_game():
    global cookies, cookies_per_click, auto_clickers, auto_clicker_cost, upgrade_cost

    if not os.path.exists(SAVE_FILE):
        return

    try:
        with open(SAVE_FILE, "rb") as f:
            encoded = f.read()

        encrypted = base64.b64decode(encoded)
        raw = _xor(encrypted, SAVE_KEY)
        data = json.loads(raw.decode())

        sig = data.pop("signature", None)
        if sig != generate_signature(data):
            raise ValueError("Signature mismatch")

        # Sanity checks
        if (
            data["cookies"] < 0 or
            data["cookies"] > 1_000_000_000 or
            data["cookies_per_click"] < 1 or
            data["cookies_per_click"] > 1000 or
            data["auto_clickers"] < 0 or
            data["auto_clickers"] > 10000
        ):
            raise ValueError("Invalid values")

        cookies = data["cookies"]
        cookies_per_click = data["cookies_per_click"]
        auto_clickers = data["auto_clickers"]
        auto_clicker_cost = data["auto_clicker_cost"]
        upgrade_cost = data["upgrade_cost"]

    except Exception:
        handle_cheat()

def handle_cheat():
    messagebox.showerror(
        "CHEAT DETECTED",
        "Save file was modified.\nProgress reset."
    )
    reset_game()

def reset_game():
    global cookies, cookies_per_click, auto_clickers, auto_clicker_cost, upgrade_cost
    cookies = 0
    cookies_per_click = 1
    auto_clickers = 0
    auto_clicker_cost = 50
    upgrade_cost = 20
    save_game()
    update_labels()

# =========================
# GAME LOGIC
# =========================
def click_cookie(event=None):
    global cookies
    cookies += cookies_per_click
    update_labels()
    animate_click()

def buy_auto_clicker():
    global cookies, auto_clickers, auto_clicker_cost
    if cookies >= auto_clicker_cost:
        cookies -= auto_clicker_cost
        auto_clickers += 1
        auto_clicker_cost = int(auto_clicker_cost * 1.5)
        update_labels()

def upgrade_click():
    global cookies, cookies_per_click, upgrade_cost
    if cookies >= upgrade_cost:
        cookies -= upgrade_cost
        cookies_per_click += 1
        upgrade_cost = int(upgrade_cost * 2)
        update_labels()

def auto_click():
    global cookies
    cookies += auto_clickers
    update_labels()
    root.after(1000, auto_click)

def update_labels():
    cookie_label.config(text=f"🍪 Cookies: {cookies}")
    click_label.config(text=f"Click Power: {cookies_per_click}")
    auto_label.config(text=f"Auto-Clickers: {auto_clickers}")
    auto_button.config(text=f"Buy Auto-Clicker ({auto_clicker_cost}🍪)")
    upgrade_button.config(text=f"Upgrade Click (+1) ({upgrade_cost}🍪)")

def animate_click():
    cookie_button.config(width=220, height=220)
    root.after(100, lambda: cookie_button.config(width=200, height=200))

# =========================
# DEV PANEL
# =========================
def open_dev_panel():
    password = simpledialog.askstring("Dev Panel", "Password:", show="*")
    if password != DEV_PASSWORD:
        messagebox.showerror("Access Denied", "Wrong password")
        return

    dev = tk.Toplevel(root)
    dev.title("DEV PANEL")
    dev.geometry("300x300")

    tk.Button(dev, text="+1000 Cookies", command=lambda: add_cookies(1000)).pack(pady=5)
    tk.Button(dev, text="+10 Click Power", command=lambda: add_power(10)).pack(pady=5)
    tk.Button(dev, text="+10 Auto Clickers", command=lambda: add_auto(10)).pack(pady=5)
    tk.Button(dev, text="MAX EVERYTHING", fg="red", command=max_all).pack(pady=15)

def add_cookies(amount):
    global cookies
    cookies += amount
    update_labels()

def add_power(amount):
    global cookies_per_click
    cookies_per_click += amount
    update_labels()

def add_auto(amount):
    global auto_clickers
    auto_clickers += amount
    update_labels()

def max_all():
    global cookies, cookies_per_click, auto_clickers
    cookies = 999_999_999
    cookies_per_click = 999
    auto_clickers = 999
    update_labels()

# =========================
# GUI
# =========================
root = tk.Tk()
root.title("🍪 Cookie Clicker")
root.geometry("500x550")
root.configure(bg="#fdf6e3")

root.bind("*", lambda e: open_dev_panel())

cookie_label = tk.Label(root, font=("Comic Sans MS", 20, "bold"), bg="#fdf6e3")
cookie_label.pack(pady=10)

click_label = tk.Label(root, font=("Helvetica", 14), bg="#fdf6e3")
click_label.pack()

auto_label = tk.Label(root, font=("Helvetica", 14), bg="#fdf6e3")
auto_label.pack()

if not os.path.exists(COOKIE_IMG_PATH):
    messagebox.showerror("Error", "cookie.png missing")
    sys.exit()

img = Image.open(COOKIE_IMG_PATH).resize((200, 200))
photo = ImageTk.PhotoImage(img)

cookie_button = tk.Label(root, image=photo, bg="#fdf6e3")
cookie_button.pack(pady=20)
cookie_button.bind("<Button-1>", click_cookie)

auto_button = tk.Button(root, width=22, bg="#ffcc00", command=buy_auto_clicker)
auto_button.pack(pady=5)

upgrade_button = tk.Button(root, width=22, bg="#ff9966", command=upgrade_click)
upgrade_button.pack(pady=5)

# =========================
# START
# =========================
load_game()
update_labels()
root.after(1000, auto_click)
root.protocol("WM_DELETE_WINDOW", lambda: [save_game(), root.destroy()])
root.mainloop()
