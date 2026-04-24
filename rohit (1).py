import cv2
import threading
import pygame.midi
import time
from cvzone.HandTrackingModule import HandDetector

# ---------------- MIDI ----------------
pygame.midi.init()
player = pygame.midi.Output(0)

# Harmonium / Organ sound
player.set_instrument(19)

# ------------ Camera Fix -------------
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

detector = HandDetector(detectionCon=0.8,maxHands=2)

# -------- Sargam Notes --------
notes = {
    "thumb":60,    # Sa
    "index":62,    # Re
    "middle":64,   # Ga
    "ring":65,     # Ma
    "pinky":67     # Pa
}

sargam = {
60:"Sa",
62:"Re",
64:"Ga",
65:"Ma",
67:"Pa"
}

prev_states={
finger:0 for finger in notes
}

# ---------- Play Note ----------
def play_note(note):
    player.note_on(note,127)
    time.sleep(0.6)
    player.note_off(note,127)

print("🎵 Harmonium Started - Press Q to Quit")

while True:

    success,img=cap.read()

    if not success:
        print("Camera not capturing")
        continue

    hands,img=detector.findHands(img,draw=True)

    if hands:

        hand=hands[0]

        fingers=detector.fingersUp(hand)

        finger_names=[
            "thumb",
            "index",
            "middle",
            "ring",
            "pinky"
        ]

        for i,finger in enumerate(finger_names):

            if fingers[i]==1 and prev_states[finger]==0:

                note=notes[finger]

                threading.Thread(
                    target=play_note,
                    args=(note,),
                    daemon=True
                ).start()

                print("Playing:",sargam[note])

                cv2.putText(
                    img,
                    sargam[note],
                    (50,100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    2,
                    (0,255,0),
                    4
                )

            prev_states[finger]=fingers[i]

    cv2.imshow("Virtual Harmonium",img)

    if cv2.waitKey(1) & 0xFF==ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pygame.midi.quit()