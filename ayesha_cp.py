

import cv2
import mediapipe as mp
import numpy as np

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


# ============================================================
# 1. WINDOWS VOLUME SETUP
# ============================================================

devices = AudioUtilities.GetSpeakers()

# Support different Pycaw AudioDevice API versions
if hasattr(devices, "_dev"):
    audio_device = devices._dev
else:
    audio_device = devices

interface = audio_device.Activate(
    IAudioEndpointVolume._iid_,
    CLSCTX_ALL,
    None
)

volume = cast(interface, POINTER(IAudioEndpointVolume))

# Read actual Windows volume
vol_perc = volume.GetMasterVolumeLevelScalar() * 100


# ============================================================
# 2. MEDIAPIPE FACE MESH
# ============================================================

mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)


# ============================================================
# 3. CAMERA
# ============================================================

wCam = 640
hCam = 480

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, wCam)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, hCam)

if not cap.isOpened():
    print("Could not access camera.")
    face_mesh.close()
    raise SystemExit


# ============================================================
# 4. FACIAL CONTROL SETTINGS
# ============================================================

# Mouth opening threshold
mouth_open_threshold = 18

# Minimum head movement in pixels
head_movement_threshold = 5

# Volume sensitivity
# Increase to 4.0 if volume changes too slowly
sensitivity = 2.5

# Smoothing factor
smoothing = 0.30

# Nose position smoothing
nose_smoothing = 0.35

# Tracking state
is_tracking = False
neutral_nose_y = None
smoothed_nose_y = None

# Starting volume
base_volume = vol_perc


# ============================================================
# 5. MAIN LOOP
# ============================================================

try:
    while True:

        success, img = cap.read()

        if not success:
            print("Could not read camera frame.")
            break

        # Mirror camera
        img = cv2.flip(img, 1)

        # Convert BGR to RGB
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Detect face
        results = face_mesh.process(rgb_img)

        face_detected = False
        mouth_distance = 0

        if results.multi_face_landmarks:

            face_detected = True
            face_landmarks = results.multi_face_landmarks[0]

            # ------------------------------------------------
            # FACE LANDMARKS
            # ------------------------------------------------

            nose = face_landmarks.landmark[1]
            upper_lip = face_landmarks.landmark[13]
            lower_lip = face_landmarks.landmark[14]

            nose_x = int(nose.x * wCam)
            nose_y = int(nose.y * hCam)

            upper_lip_x = int(upper_lip.x * wCam)
            upper_lip_y = int(upper_lip.y * hCam)

            lower_lip_x = int(lower_lip.x * wCam)
            lower_lip_y = int(lower_lip.y * hCam)

            # ------------------------------------------------
            # SMOOTH NOSE POSITION
            # ------------------------------------------------

            if smoothed_nose_y is None:
                smoothed_nose_y = float(nose_y)
            else:
                smoothed_nose_y = (
                    nose_smoothing * nose_y
                    + (1 - nose_smoothing) * smoothed_nose_y
                )

            # ------------------------------------------------
            # MOUTH OPENING DISTANCE
            # ------------------------------------------------

            mouth_distance = np.sqrt(
                (upper_lip_x - lower_lip_x) ** 2
                + (upper_lip_y - lower_lip_y) ** 2
            )

            # ------------------------------------------------
            # MOUTH OPEN: START CONTROL
            # ------------------------------------------------

            if mouth_distance > mouth_open_threshold:

                if not is_tracking:

                    is_tracking = True

                    # Set neutral head position
                    neutral_nose_y = smoothed_nose_y

                    # Save current volume as reference
                    base_volume = vol_perc

                # Calculate head movement from reference
                if neutral_nose_y is not None:

                    movement = neutral_nose_y - smoothed_nose_y

                    # Ignore tiny movements
                    if abs(movement) < head_movement_threshold:
                        movement = 0

                    # Calculate target volume
                    target_volume = (
                        base_volume + movement * sensitivity
                    )

                    target_volume = max(
                        0,
                        min(100, target_volume)
                    )

                    # Smooth volume changes
                    vol_perc = (
                        smoothing * target_volume
                        + (1 - smoothing) * vol_perc
                    )

            # ------------------------------------------------
            # MOUTH CLOSED: PAUSE CONTROL
            # ------------------------------------------------

            else:

                is_tracking = False
                neutral_nose_y = None

            # ------------------------------------------------
            # APPLY WINDOWS VOLUME
            # ------------------------------------------------

            vol_perc = max(0, min(100, vol_perc))

            volume.SetMasterVolumeLevelScalar(
                vol_perc / 100.0,
                None
            )

            # ------------------------------------------------
            # DRAW FACE LANDMARKS
            # ------------------------------------------------

            for landmark in face_landmarks.landmark:

                x = int(landmark.x * wCam)
                y = int(landmark.y * hCam)

                cv2.circle(
                    img,
                    (x, y),
                    1,
                    (255, 255, 255),
                    -1
                )

            # Nose marker
            cv2.circle(
                img,
                (nose_x, nose_y),
                7,
                (0, 255, 0),
                -1
            )

            # Mouth markers
            cv2.circle(
                img,
                (upper_lip_x, upper_lip_y),
                5,
                (255, 0, 0),
                -1
            )

            cv2.circle(
                img,
                (lower_lip_x, lower_lip_y),
                5,
                (255, 0, 0),
                -1
            )

            # Mouth line
            cv2.line(
                img,
                (upper_lip_x, upper_lip_y),
                (lower_lip_x, lower_lip_y),
                (255, 0, 0),
                2
            )

            # Display mouth distance
            cv2.putText(
                img,
                f"Mouth Distance: {int(mouth_distance)}",
                (20, 125),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 0),
                2
            )

        else:

            # Reset tracking if face disappears
            is_tracking = False
            neutral_nose_y = None
            smoothed_nose_y = None

        # ====================================================
        # 6. VOLUME BAR
        # ====================================================

        bar_left = 580
        bar_right = 620
        bar_top = 140
        bar_bottom = 340

        bar_height = int(
            np.interp(
                vol_perc,
                [0, 100],
                [bar_bottom, bar_top]
            )
        )

        # Background
        cv2.rectangle(
            img,
            (bar_left, bar_top),
            (bar_right, bar_bottom),
            (70, 70, 70),
            -1
        )

        # Volume fill
        bar_color = (
            (255, 255, 255)
            if is_tracking
            else (0, 0, 255)
        )

        cv2.rectangle(
            img,
            (bar_left, bar_height),
            (bar_right, bar_bottom),
            bar_color,
            -1
        )

        # Border
        cv2.rectangle(
            img,
            (bar_left, bar_top),
            (bar_right, bar_bottom),
            (255, 255, 255),
            2
        )

        # ====================================================
        # 7. VOLUME TEXT
        # ====================================================

        cv2.putText(
            img,
            f"Volume: {int(vol_perc)}%",
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        # ====================================================
        # 8. STATUS
        # ====================================================

        if not face_detected:
            status = "NO FACE DETECTED"
        elif is_tracking:
            status = "LIVE CONTROL - MOUTH OPEN"
        else:
            status = "PAUSED - OPEN MOUTH"

        cv2.putText(
            img,
            status,
            (20, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 255, 0) if is_tracking else (0, 0, 255),
            2
        )

        # ====================================================
        # 9. INSTRUCTIONS
        # ====================================================

        cv2.putText(
            img,
            "Open Mouth = Activate",
            (20, 395),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2
        )

        cv2.putText(
            img,
            "Head UP = Volume +",
            (20, 420),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2
        )

        cv2.putText(
            img,
            "Head DOWN = Volume -",
            (20, 445),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2
        )

        cv2.putText(
            img,
            "Press ESC to exit",
            (20, 470),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 200, 200),
            1
        )

        # ====================================================
        # 10. DISPLAY WINDOW
        # ====================================================

        cv2.imshow("Facial Volume Control", img)

        if cv2.waitKey(1) & 0xFF == 27:
            break

finally:

    # ========================================================
    # 11. CLEANUP
    # ========================================================

    cap.release()
    cv2.destroyAllWindows()
    face_mesh.close()

    print("Facial Volume Control stopped.")
