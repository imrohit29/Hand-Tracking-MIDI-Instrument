import cv2
import threading
import pygame.midi
import time
import tkinter as tk
from tkinter import ttk
from cvzone.HandTrackingModule import HandDetector

# Initialize Pygame MIDI
pygame.midi.init()
player = pygame.midi.Output(0)

# Chord sets for songs
song_chords = {
    "Happy Birthday": [
        ("left", "thumb"),
        ("left", "index"),
        ("right", "thumb"),
        ("right", "index"),
        ("left", "middle"),
        ("right", "middle")
    ],
    "Twinkle Twinkle": [
        ("left", "thumb"),
        ("left", "ring"),
        ("right", "index"),
        ("right", "pinky"),
    ]
}

# Chords mapping to MIDI notes
chords = {
    "left": {
        "thumb": [60, 64, 67],
        "index": [62, 65, 69],
        "middle": [64, 67, 71],
        "ring": [65, 69, 72],
        "pinky": [67, 71, 74]
    },
    "right": {
        "thumb": [60, 64, 67],
        "index": [62, 65, 69],
        "middle": [64, 67, 71],
        "ring": [65, 69, 72],
        "pinky": [67, 71, 74]
    }
}

# Function to play chords
def play_chord(hand, finger):
    if hand in chords and finger in chords[hand]:
        for note in chords[hand][finger]:
            player.note_on(note, 127)
        time.sleep(1)
        for note in chords[hand][finger]:
            player.note_off(note, 127)

# Hand Tracking Function
def start_hand_tracking(selected_song):
    cap = cv2.VideoCapture(0)
    detector = HandDetector(detectionCon=0.8)
    sequence = song_chords[selected_song]
    step = 0

    while True:
        success, img = cap.read()
        if not success:
            continue
        hands, img = detector.findHands(img, draw=True)

        if hands and step < len(sequence):
            hand, finger = sequence[step]
            play_chord(hand, finger)
            step += 1
            time.sleep(1)
        
        cv2.putText(img, f"Raise: {sequence[step-1][1]} on {sequence[step-1][0]}", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Hand Tracking MIDI", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    pygame.midi.quit()

# Tkinter UI
def start_tracking():
    selected_song = song_var.get()
    threading.Thread(target=start_hand_tracking, args=(selected_song,), daemon=True).start()

root = tk.Tk()
root.title("MIDI Hand Tracking - Song Mode")
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky="W")

ttk.Label(frame, text="Select a Song:").grid(row=0, column=0, sticky="W")
song_var = tk.StringVar()
song_dropdown = ttk.Combobox(frame, textvariable=song_var, state="readonly")
song_dropdown['values'] = list(song_chords.keys())
song_dropdown.current(0)
song_dropdown.grid(row=0, column=1, pady=5, sticky="W")

start_button = ttk.Button(frame, text="Start Playing", command=start_tracking)
start_button.grid(row=1, column=0, columnspan=2, pady=10)

root.mainloop()
