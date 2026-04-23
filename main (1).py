import cv2
import threading
import pygame.midi
import time
from cvzone.HandTrackingModule import HandDetector

# Initialize Pygame MIDI
pygame.midi.init()
player = pygame.midi.Output(0)

default_instrument_left = 0  # Default Acoustic Grand Piano
default_instrument_right = 24  # Default Acoustic Guitar (nylon)

# Define chord mappings
chords = {
    "left": {
        "thumb": {"notes": [60, 64]},  # Sa & Ma (C & F#)
        "index": {"notes": [62, 67]},  # Re & Pa (D & G)
        "middle": {"notes": [64, 71]}, # Ga & Ni (E & B)
        "ring": {"notes": [65, 69]},  # Ma & Dha (F# & A)
        "pinky": {"notes": [67, 72]}  # Pa & Sa (G & C)
    },
    "right": {
        "thumb": {"notes": [60, 64, 67]},  # Sa Ma Pa (C F# G)
        "index": {"notes": [62, 66, 71]},  # Re Ma Ni (D F# B)
        "middle": {"notes": [64, 69, 74]}, # Ga Dha Re (E A D)
        "ring": {"notes": [65, 70, 76]},  # Ma Ni Ga (F# B E)
        "pinky": {"notes": [67, 72, 79]}  # Pa Sa Ga (G C E)
    }
}

# Sargam Mapping
sargam_map = {60: "Sa", 62: "Re", 64: "Ga", 65: "Ma", 67: "Pa", 69: "Dha", 71: "Ni", 72: "Sa"}

# Sustain time
SUSTAIN_TIME = 2.0
SARGAM_DISPLAY_TIME = 3.5  # Increased display time
prev_states = {hand: {finger: 0 for finger in chords[hand]} for hand in chords}

sargam_text = "-"
sargam_timestamp = time.time()

def play_chord(instrument, chord_notes):
    player.set_instrument(instrument)
    for note in chord_notes:
        player.note_on(note, 127)
    print(f"Playing chord {chord_notes} on instrument {instrument}")

def stop_chord_after_delay(chord_notes):
    time.sleep(SUSTAIN_TIME)
    for note in chord_notes:
        player.note_off(note, 127)
    print(f"Stopped chord {chord_notes}")

def start_hand_tracking(left_instrument=default_instrument_left, right_instrument=default_instrument_right):
    global sargam_text, sargam_timestamp
    instruments = {"left": left_instrument, "right": right_instrument}
    cap = cv2.VideoCapture(0)
    detector = HandDetector(detectionCon=0.8, maxHands=2)
    prev_states = {hand: {finger: 0 for finger in chords[hand]} for hand in chords}
    
    while cap.isOpened():
        success, img = cap.read()
        if not success:
            print("❌ Camera not capturing frames")
            continue

        hands, img = detector.findHands(img, draw=True)
        detected_hands = {}
        
        for hand in hands:
            hand_type = "left" if hand["type"] == "Left" else "right"
            detected_hands[hand_type] = hand  # Store detected hands

        # Display hand labels *only once per hand type*
        for hand_type, hand in detected_hands.items():
            cv2.putText(img, f"{hand_type.capitalize()} Hand", (hand["bbox"][0], hand["bbox"][1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        current_sargam = "-"
        for hand_type in ["left", "right"]:
            if hand_type in detected_hands:
                fingers_state = detector.fingersUp(detected_hands[hand_type])
                finger_names = ["thumb", "index", "middle", "ring", "pinky"]

                for i, finger in enumerate(finger_names):
                    if finger in chords[hand_type]:
                        chord_notes = chords[hand_type][finger]["notes"]
                        instrument = instruments[hand_type]

                        if fingers_state[i] == 1 and prev_states[hand_type][finger] == 0:
                            play_chord(instrument, chord_notes)
                            current_sargam = sargam_map.get(chord_notes[0], "-")
                            sargam_text = current_sargam
                            sargam_timestamp = time.time()
                        elif fingers_state[i] == 0 and prev_states[hand_type][finger] == 1:
                            threading.Thread(target=stop_chord_after_delay, args=(chord_notes,), daemon=True).start()
                        prev_states[hand_type][finger] = fingers_state[i]
                
        if time.time() - sargam_timestamp < SARGAM_DISPLAY_TIME:
            cv2.putText(img, sargam_text, (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 3)

        cv2.imshow("Hand Tracking MIDI Chords", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    pygame.midi.quit()

if __name__ == "__main__":
    start_hand_tracking()