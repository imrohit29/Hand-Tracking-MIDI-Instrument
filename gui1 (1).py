import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading
import pygame.midi
import random
from main import start_hand_tracking


pygame.midi.init()

def main_window():
    root = tk.Tk()
    root.title("Hand Tracking MIDI Chords")
    root.geometry("1000x650")  
    root.configure(bg="#1E1E1E") 

    # Load and set background image
    try:
        bg_img = Image.open("D:/Programming/Project/music-6018641_1280.webp")
        bg_img = bg_img.resize((1000, 650), Image.Resampling.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_img)
    except Exception as e:
        print(f"Error loading background image: {e}")
        bg_photo = None

    canvas = tk.Canvas(root, width=1000, height=650, bg="#1E1E1E", highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    if bg_photo:
        canvas.bg_photo = bg_photo
        canvas.create_image(0, 0, anchor="nw", image=canvas.bg_photo)

    # Floating music notes animation
    notes = []
    for _ in range(15):
        x = random.randint(50, 950)
        y = random.randint(50, 600)
        notes.append(canvas.create_text(x, y, text="♪", font=("Arial", 20, "bold"), fill="gold"))
    
    def animate_notes():
        for note in notes:
            canvas.move(note, 0, random.choice([-1, 1]))
        root.after(50, animate_notes)
    
    animate_notes()

    # Panel for UI components with styling
    panel = tk.Frame(root, bg="#2E2E2E", padx=30, pady=30, relief="ridge", bd=8)
    panel_id = canvas.create_window(500, 350, window=panel, anchor="center")

    # Heading label with bold bright text
    header_label = ttk.Label(panel, text="Hand Tracking MIDI Chords", font=("Arial Black", 22), foreground="gold", background="#2E2E2E")
    header_label.grid(row=0, column=0, columnspan=2, pady=15)

    # Instrument options
    instrument_options = {
        "Acoustic Grand Piano": 0, "Bright Acoustic Piano": 1, "Electric Grand Piano": 2, "Honky-tonk Piano": 3,
        "Electric Piano 1": 4, "Electric Piano 2": 5, "Hammond Organ": 16, "Percussive Organ": 17,
        "Acoustic Guitar (nylon)": 24, "Acoustic Guitar (steel)": 25, "Electric Guitar (jazz)": 26, "Electric Guitar (clean)": 27,
        "Acoustic Bass": 32, "Electric Bass (finger)": 33, "Electric Bass (pick)": 34, "Violin": 40,
        "Viola": 41, "Cello": 42, "String Ensemble 1": 48, "String Ensemble 2": 49,
        "Trumpet": 56, "Trombone": 57, "Saxophone": 64, "Clarinet": 71,
        "Synth Lead": 80, "Synth Pad": 88, "Synth Bass": 38, "Celesta": 8,
        "Glockenspiel": 9, "Music Box": 10, "Vibraphone": 11, "Marimba": 12
    }

    # Left Hand Instrument
    ttk.Label(panel, text="Left Hand Instrument:", background="#2E2E2E", foreground="white", font=("Arial", 12, "bold")).grid(row=1, column=0, padx=10, pady=8, sticky="w")
    left_instrument_var = tk.StringVar()
    left_dropdown = ttk.Combobox(panel, textvariable=left_instrument_var, state="readonly", width=35)
    left_dropdown['values'] = list(instrument_options.keys())
    left_dropdown.current(0)
    left_dropdown.grid(row=1, column=1, pady=8)

    # Right Hand Instrument
    ttk.Label(panel, text="Right Hand Instrument:", background="#2E2E2E", foreground="white", font=("Arial", 12, "bold")).grid(row=2, column=0, padx=10, pady=8, sticky="w")
    right_instrument_var = tk.StringVar()
    right_dropdown = ttk.Combobox(panel, textvariable=right_instrument_var, state="readonly", width=35)
    right_dropdown['values'] = list(instrument_options.keys())
    right_dropdown.current(0)
    right_dropdown.grid(row=2, column=1, pady=8)

    # Start button with hover effects
    style = ttk.Style()
    style.configure("TButton", font=("Arial", 12), padding=8)
    
    def start_tracking():
        left_text = left_instrument_var.get()
        right_text = right_instrument_var.get()
        left_inst = instrument_options.get(left_text, 0)
        right_inst = instrument_options.get(right_text, 0)

        messagebox.showinfo("Starting", f"Left: {left_text} | Right: {right_text}")
        threading.Thread(target=start_hand_tracking, args=(left_inst, right_inst), daemon=True).start()

    start_button = ttk.Button(panel, text="Start Hand Tracking", command=start_tracking, style="TButton")
    start_button.grid(row=3, column=0, columnspan=2, pady=20)

    root.mainloop()

# Splash Screen
splash_root = tk.Tk()
splash_root.overrideredirect(True)
splash_root.geometry("450x350+500+250")

try:
    splash_img = Image.open("D:/Programming/Project/splash.png")
    splash_img = splash_img.resize((450, 350), Image.Resampling.LANCZOS)
    splash_photo = ImageTk.PhotoImage(splash_img)
except Exception as e:
    print(f"Error loading splash image: {e}")
    splash_photo = None

splash_label = tk.Label(splash_root, image=splash_photo, bg="white")
splash_label.pack(fill="both", expand=True)

def load_main():
    splash_root.destroy()
    main_window()

splash_root.after(3000, load_main)
splash_root.mainloop()
