import cv2
import threading
import pygame.midi
import time
from cvzone.HandTrackingModule import HandDetector  # Ensure you have cvzone installed

# 🎵 Initialize Pygame MIDI
pygame.midi.init()
player = pygame.midi.Output(0)
player.set_instrument(118)  # 118 = Percussive Instrument (Drums)

# 🎐 Initialize Hand Detector
cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8)

# 🎺 Drum Mapping for Virtual Zones
drums = {
    "left": {
        "thumb": 36,   # Kick Drum
        "index": 38,   # Snare Drum
        "middle": 42,  # Hi-Hat Closed
        "ring": 46,    # Hi-Hat Open
        "pinky": 49    # Crash Cymbal
    },
    "right": {
        "thumb": 36,   # Kick Drum
        "index": 38,   # Snare Drum
        "middle": 42,  # Hi-Hat Closed
        "ring": 46,    # Hi-Hat Open
        "pinky": 49    # Crash Cymbal
    }
}

# Sustain Time (in seconds) before stopping drum sounds
SUSTAIN_TIME = 0.2

# Track Previous States to Prevent Repeated Hits
prev_states = {hand: {finger: 0 for finger in drums[hand]} for hand in drums}

# 🎵 Function to Play a Drum Sound
def play_drum(drum_note):
    player.note_on(drum_note, 127)  # Start drum sound
    time.sleep(0.1)  # Short sustain for a drum hit
    player.note_off(drum_note, 127)  # Stop drum sound

while True:
    success, img = cap.read()
    if not success:
        print("❌ Camera not capturing frames")
        continue

    hands, img = detector.findHands(img, draw=True)

    if hands:
        for hand in hands:
            hand_type = "left" if hand["type"] == "Left" else "right"
            fingers = detector.fingersUp(hand)
            finger_names = ["thumb", "index", "middle", "ring", "pinky"]

            for i, finger in enumerate(finger_names):
                if finger in drums[hand_type]:  # Only check assigned drums
                    if fingers[i] == 1 and prev_states[hand_type][finger] == 0:
                        threading.Thread(target=play_drum, args=(drums[hand_type][finger],), daemon=True).start()
                    prev_states[hand_type][finger] = fingers[i]  # Update state

    cv2.imshow("Air Drums", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pygame.midi.quit()
