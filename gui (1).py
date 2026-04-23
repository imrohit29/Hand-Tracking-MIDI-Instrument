import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
print("GUI script started")
from main import start_hand_tracking
print("Import successful")

# Initialize the main window
window = tk.Tk()
window.title("Hand Tracking Instrument Selector")
window.geometry("1280x720")

# Load and set background image
try:
    bg_img = Image.open("D:/Programming/Project/music-6018641_1280.webp")
    bg_img = bg_img.resize((1280, 720), Image.Resampling.LANCZOS)
    background = ImageTk.PhotoImage(bg_img)
    bg_label = tk.Label(window, image=background)
    bg_label.place(relwidth=1, relheight=1)
except Exception as e:
    print(f"Error loading background image: {e}")

# Instrument list (example MIDI instruments)
instruments = [
    "0: Acoustic Grand Piano",
    "24: Acoustic Guitar (nylon)",
    "26: Electric Guitar (jazz)",
    "40: Violin",
    "56: Trumpet"
]

# Left hand instrument selection
left_label = tk.Label(window, text="Left Hand Instrument:", font=("Arial", 14), bg="white")
left_label.pack(pady=10)
left_combo = ttk.Combobox(window, values=instruments, state="readonly", font=("Arial", 12))
left_combo.set(instruments[0])  # Default to piano
left_combo.pack()

# Right hand instrument selection
right_label = tk.Label(window, text="Right Hand Instrument:", font=("Arial", 14), bg="white")
right_label.pack(pady=10)
right_combo = ttk.Combobox(window, values=instruments, state="readonly", font=("Arial", 12))
right_combo.set(instruments[1])  # Default to guitar
right_combo.pack()

# Function to start hand tracking
def start_tracking():
    left_text = left_combo.get()
    right_text = right_combo.get()
    left_inst = int(left_text.split(":")[0].strip())
    right_inst = int(right_text.split(":")[0].strip())
    print(f"Selected - Left: {left_inst}, Right: {right_inst}")
    threading.Thread(target=start_hand_tracking, args=(left_inst, right_inst), daemon=True).start()

# Start button
start_button = tk.Button(window, text="Start Hand Tracking", command=start_tracking, font=("Arial", 14))
start_button.pack(pady=20)

# Run the GUI
window.mainloop()