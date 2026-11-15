import cv2
import numpy as np
import time
from HandTrackingModule import HandDetector  # Corrected import
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# ================= SETTINGS ====================
wCam, hCam = 640, 480
min_dist = 25
max_dist = 190
vol_bar = 340
vol_color = (250, 0, 0)
pTime = 0
# ===============================================

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = HandDetector(detection_conf=0.75, max_hands=1)

# Setup audio control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
vol_range = volume.GetVolumeRange()
min_vol, max_vol = vol_range[0], vol_range[1]

while True:
    success, img = cap.read()
    img = detector.findHands(img, draw=True)
    lmList, b_box = detector.findPosition(img, draw=True)

    if len(lmList) != 0:
        # Filter based on hand size
        area = (b_box[2] - b_box[0]) * (b_box[3] - b_box[1]) // 100
        if 200 < area < 1000:
            # Find distance between index and thumb
            length, img, line_info = detector.findDistance(4, 8, img)

            # Convert length to volume percent
            vol_bar = np.interp(length, [min_dist, max_dist], [340, 140])
            vol_perc = np.interp(length, [min_dist, max_dist], [0, 100])
            smoothness = 10
            vol_perc = smoothness * round(vol_perc / smoothness)

            # Check which fingers are up
            fingers = detector.fingersUp()

            # Set volume only if pinky is down
            if fingers and not fingers[4]:
                volume.SetMasterVolumeLevelScalar(vol_perc / 100, None)
                cv2.circle(img, (line_info[4], line_info[5]), 5, (255, 255, 0), cv2.FILLED)
                vol_color = (135, 0, 255)
            else:
                vol_color = (250, 0, 0)

            # Min & Max volume indicator color
            if length < min_dist:
                cv2.circle(img, (line_info[4], line_info[5]), 5, (0, 0, 255), cv2.FILLED)
            elif length > max_dist:
                cv2.circle(img, (line_info[4], line_info[5]), 5, (0, 255, 0), cv2.FILLED)

    # Draw volume bar
    cv2.rectangle(img, (55, 140), (85, 340), (255, 255, 0), 3)
    cv2.rectangle(img, (55, int(vol_bar)), (85, 340), (255, 255, 0), cv2.FILLED)
    cv2.putText(img, f'Vol = {int(vol_perc)} %', (18, 380),
                cv2.FONT_HERSHEY_COMPLEX, 0.6, (51, 255, 255), 2)

    curr_vol = int(volume.GetMasterVolumeLevelScalar() * 100)
    cv2.putText(img, f'Vol set to: {curr_vol} %', (410, 50),
                cv2.FONT_HERSHEY_COMPLEX, 0.7, vol_color, 2)

    # Show FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (30, 50),
                cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 0, 0), 2)

    cv2.imshow("Hand Volume Control", img)
    cv2.waitKey(1)
