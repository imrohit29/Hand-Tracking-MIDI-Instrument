import cv2
import threading
import pygame.midi
import time
import tkinter as tk
from tkinter import ttk
from cvzone.HandTrackingModule import HandDetector  # type: ignore

# --------------------------
# Initialize Pygame MIDI
# --------------------------
pygame.midi.init()
player = pygame.midi.Output(0)

# --------------------------
# General MIDI Instrument Options
# --------------------------
instrument_options = {
    0: "Acoustic Grand Piano",
    1: "Bright Acoustic Piano",
    2: "Electric Grand Piano",
    3: "Honky-tonk Piano",
    4: "Electric Piano 1",
    5: "Electric Piano 2",
    16: "Hammond Organ",
    17: "Percussive Organ",
    24: "Acoustic Guitar (nylon)",
    25: "Acoustic Guitar (steel)",
    26: "Electric Guitar (jazz)",
    27: "Electric Guitar (clean)",
    32: "Acoustic Bass",
    33: "Electric Bass (finger)",
    34: "Electric Bass (pick)",
    40: "Violin",
    41: "Viola",
    42: "Cello",
    48: "String Ensemble 1",
    49: "String Ensemble 2",
    56: "Trumpet",
    57: "Trombone",
    64: "Saxophone",
    71: "Clarinet",
    80: "Synth Lead",
    88: "Synth Pad",
    38: "Synth Bass",
    8:  "Celesta",
    9:  "Glockenspiel",
    10: "Music Box",
    11: "Vibraphone",
    12: "Marimba"
}

# --------------------------
# Fixed Chord Mapping for Fingers (D Major Scale)
# --------------------------
chords = {
    "left": {
        "thumb": {"notes": [62, 66, 69]},   # D Major (D, F#, A)
        "index": {"notes": [64, 67, 71]},   # E Minor (E, G, B)
        "middle": {"notes": [66, 69, 73]},  # F# Minor (F#, A, C#)
        "ring": {"notes": [67, 71, 74]},    # G Major (G, B, D)
        "pinky": {"notes": [69, 73, 76]}     # A Major (A, C#, E)
    },
    "right": {
        "thumb": {"notes": [62, 66, 69]},
        "index": {"notes": [64, 67, 71]},
        "middle": {"notes": [66, 69, 73]},
        "ring": {"notes": [67, 71, 74]},
        "pinky": {"notes": [69, 73, 76]}
    }
}

# Sustain time (seconds) after finger is lowered
SUSTAIN_TIME = 2.0

# Track previous finger states for state changes
prev_states = {hand: {finger: 0 for finger in chords[hand]} for hand in chords}


# --------------------------
# Function to Play and Stop Chords
# --------------------------
def play_chord(instrument, chord_notes):
    # Set instrument and play each note
    player.set_instrument(instrument)
    for note in chord_notes:
        player.note_on(note, 127)
    print(f"Playing chord {chord_notes} on instrument {instrument}")


def stop_chord_after_delay(chord_notes):
    time.sleep(SUSTAIN_TIME)
    for note in chord_notes:
        player.note_off(note, 127)
    print(f"Stopped chord {chord_notes}")


# --------------------------
# Hand Tracking Function (runs in a separate thread)
# --------------------------
def start_hand_tracking(left_instrument, right_instrument):
    instruments = {"left": left_instrument, "right": right_instrument}
    cap = cv2.VideoCapture(0)
    detector = HandDetector(detectionCon=0.8)

    global prev_states
    prev_states = {hand: {finger: 0 for finger in chords[hand]} for hand in chords}

    while True:
        success, img = cap.read()
        if not success:
            print("❌ Camera not capturing frames")
            continue

        # Detect hands and draw landmarks
        hands, img = detector.findHands(img, draw=True)
        # Debug: print whether a hand was detected
        if hands:
            print("Hand(s) detected.")
            for hand in hands:
                hand_type = "left" if hand["type"] == "Left" else "right"
                fingers_state = detector.fingersUp(hand)
                finger_names = ["thumb", "index", "middle", "ring", "pinky"]

                for i, finger in enumerate(finger_names):
                    if finger in chords[hand_type]:
                        chord_notes = chords[hand_type][finger]["notes"]
                        instrument = instruments[hand_type]

                        # If finger is raised and was previously down, play chord
                        if fingers_state[i] == 1 and prev_states[hand_type][finger] == 0:
                            play_chord(instrument, chord_notes)
                        # If finger is lowered and was previously raised, stop chord after sustain
                        elif fingers_state[i] == 0 and prev_states[hand_type][finger] == 1:
                            threading.Thread(target=stop_chord_after_delay, args=(chord_notes,), daemon=True).start()

                        prev_states[hand_type][finger] = fingers_state[i]
        else:
            # If no hand is detected, stop all chords
            print("No hand detected.")
            for hand in chords:
                for finger in chords[hand]:
                    threading.Thread(target=stop_chord_after_delay, args=(chords[hand][finger]["notes"],), daemon=True).start()
            prev_states = {hand: {finger: 0 for finger in chords[hand]} for hand in chords}

        cv2.imshow("Hand Tracking MIDI Chords", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    pygame.midi.quit()


# --------------------------
# Tkinter GUI Setup
# --------------------------
def start_tracking():
    # Extract the instrument number from the dropdown text
    left_text = left_instrument_var.get()
    right_text = right_instrument_var.get()

    try:
        left_inst = int(left_text.split(":")[0].strip())
    except (ValueError, IndexError):
        left_inst = 0

    try:
        right_inst = int(right_text.split(":")[0].strip())
    except (ValueError, IndexError):
        right_inst = 0

    print(f"Starting hand tracking with Left Instrument: {left_inst} and Right Instrument: {right_inst}")

    # Start hand tracking in a separate thread to avoid blocking the UI
    threading.Thread(target=start_hand_tracking, args=(left_inst, right_inst), daemon=True).start()


# Create the main window for Tkinter
root = tk.Tk()
root.title("Hand Tracking MIDI Chords")

# Create a frame for instrument selection
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky="W")

# Label and dropdown for left hand instrument
ttk.Label(frame, text="Left Hand Instrument:").grid(row=0, column=0, sticky="W")
left_instrument_var = tk.StringVar()
left_dropdown = ttk.Combobox(frame, textvariable=left_instrument_var, state="readonly")
left_dropdown['values'] = [f"{num}: {name}" for num, name in sorted(instrument_options.items())]
left_dropdown.current(0)  # Default to the first option (Acoustic Grand Piano)
left_dropdown.grid(row=0, column=1, pady=5, sticky="W")

# Label and dropdown for right hand instrument
ttk.Label(frame, text="Right Hand Instrument:").grid(row=1, column=0, sticky="W")
right_instrument_var = tk.StringVar()
right_dropdown = ttk.Combobox(frame, textvariable=right_instrument_var, state="readonly")
right_dropdown['values'] = [f"{num}: {name}" for num, name in sorted(instrument_options.items())]
right_dropdown.current(0)
right_dropdown.grid(row=1, column=1, pady=5, sticky="W")

# Button to start hand tracking
start_button = ttk.Button(frame, text="Start Hand Tracking", command=start_tracking)
start_button.grid(row=2, column=0, columnspan=2, pady=10)

# Run the Tkinter event loop
root.mainloop()
