import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# =========================
# Paths
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Folder where Game.py is located
COOKIE_IMG_PATH = os.path.join(BASE_DIR, "cookie.png")  # Make sure downloader saves this image
SAVE_FILE = os.path.join(BASE_DIR, "save.json")

# =========================
# Game variables
# =========================
cookies = 0
cookies_per_click = 1
auto_clickers = 0
auto_clicker_cost = 50
upgrade_cost = 20

# =========================
# Functions
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
    else:
        messagebox.showinfo("Not enough cookies", "You don't have enough cookies for an auto-clicker!")

def upgrade_click():
    global cookies, cookies_per_click, upgrade_cost
    if cookies >= upgrade_cost:
        cookies -= upgrade_cost
        cookies_per_click += 1
        upgrade_cost = int(upgrade_cost * 2)
        update_labels()
    else:
        messagebox.showinfo("Not enough cookies", "You don't have enough cookies to upgrade!")

def auto_click():
    global cookies
    cookies += auto_clickers
    update_labels()
    root.after(1000, auto_click)  # repeat every second

def update_labels():
    cookie_label.config(text=f"🍪 Cookies: {cookies}")
    click_label.config(text=f"Click Power: {cookies_per_click}")
    auto_button.config(text=f"Buy Auto-Clicker ({auto_clicker_cost}🍪)")
    upgrade_button.config(text=f"Upgrade Click (+1) ({upgrade_cost}🍪)")
    auto_label.config(text=f"Auto-Clickers: {auto_clickers}")

def animate_click():
    cookie_button.config(width=220, height=220)
    root.after(100, lambda: cookie_button.config(width=200, height=200))

def save_game():
    import json
    data = {
        "cookies": cookies,
        "cookies_per_click": cookies_per_click,
        "auto_clickers": auto_clickers,
        "auto_clicker_cost": auto_clicker_cost,
        "upgrade_cost": upgrade_cost
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

def load_game():
    global cookies, cookies_per_click, auto_clickers, auto_clicker_cost, upgrade_cost
    import json
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            cookies = data.get("cookies", 0)
            cookies_per_click = data.get("cookies_per_click", 1)
            auto_clickers = data.get("auto_clickers", 0)
            auto_clicker_cost = data.get("auto_clicker_cost", 50)
            upgrade_cost = data.get("upgrade_cost", 20)

# =========================
# GUI setup
# =========================
root = tk.Tk()
root.title("🍪 Cookie Clicker")
root.geometry("500x550")
root.configure(bg="#fdf6e3")  # light cookie background

# Frames
top_frame = tk.Frame(root, bg="#fdf6e3")
top_frame.pack(pady=10)
middle_frame = tk.Frame(root, bg="#fdf6e3")
middle_frame.pack(pady=10)
bottom_frame = tk.Frame(root, bg="#fdf6e3")
bottom_frame.pack(pady=10)

# Labels
cookie_label = tk.Label(top_frame, text=f"🍪 Cookies: {cookies}", font=("Comic Sans MS", 20, "bold"), bg="#fdf6e3")
cookie_label.pack()
click_label = tk.Label(top_frame, text=f"Click Power: {cookies_per_click}", font=("Helvetica", 14), bg="#fdf6e3")
click_label.pack()
auto_label = tk.Label(top_frame, text=f"Auto-Clickers: {auto_clickers}", font=("Helvetica", 14), bg="#fdf6e3")
auto_label.pack()

# Load cookie image
if not os.path.exists(COOKIE_IMG_PATH):
    messagebox.showerror("Missing Image", f"Cookie image not found!\nExpected at:\n{COOKIE_IMG_PATH}")
    sys.exit()

cookie_img = Image.open(COOKIE_IMG_PATH).resize((200, 200))
cookie_photo = ImageTk.PhotoImage(cookie_img)

# Cookie button
cookie_button = tk.Label(middle_frame, image=cookie_photo, bg="#fdf6e3")
cookie_button.pack(pady=20)
cookie_button.bind("<Button-1>", click_cookie)

# Buttons
auto_button = tk.Button(bottom_frame, text=f"Buy Auto-Clicker ({auto_clicker_cost}🍪)", font=("Helvetica", 14), width=20, bg="#ffcc00", command=buy_auto_clicker)
auto_button.pack(pady=5)
upgrade_button = tk.Button(bottom_frame, text=f"Upgrade Click (+1) ({upgrade_cost}🍪)", font=("Helvetica", 14), width=20, bg="#ff9966", command=upgrade_click)
upgrade_button.pack(pady=5)

# Hover effects
def on_enter(e):
    e.widget.config(bg="#ffee88")
def on_leave(e):
    if e.widget == auto_button:
        e.widget.config(bg="#ffcc00")
    else:
        e.widget.config(bg="#ff9966")

auto_button.bind("<Enter>", on_enter)
auto_button.bind("<Leave>", on_leave)
upgrade_button.bind("<Enter>", on_enter)
upgrade_button.bind("<Leave>", on_leave)

# Load save and start auto-click loop
load_game()
root.after(1000, auto_click)

# Save game on close
root.protocol("WM_DELETE_WINDOW", lambda: [save_game(), root.destroy()])

root.mainloop()
