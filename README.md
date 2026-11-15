# Facial-movement-volume-control
A computer vision-based assistive system that controls Windows volume using facial movements and MediaPipe Face Mesh.
# Facial Movement-Based Volume Control System Using Computer Vision

## 📌 Project Overview

The Facial Movement-Based Volume Control System is a computer vision-based assistive technology designed to control Windows system volume using facial movements.

The system uses a webcam to detect facial landmarks and track specific facial gestures. It allows users to increase or decrease system volume without using a keyboard, mouse, or physical volume buttons.

This project aims to improve accessibility and provide an alternative human-computer interaction method, particularly for individuals with limited hand mobility.

## 🎯 Objectives

- Develop a hands-free volume control system.
- Detect facial movements using computer vision.
- Track facial landmarks in real time.
- Convert facial gestures into volume adjustments.
- Improve accessibility through assistive technology.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| OpenCV | Webcam access and image processing |
| MediaPipe Face Mesh | Facial landmark detection |
| NumPy | Numerical calculations |
| Pycaw | Windows system volume control |

## ⚙️ How It Works

The system works through the following steps:

1. **Webcam Capture:** The webcam continuously captures the user's face.
2. **Face Detection:** OpenCV captures video frames, and MediaPipe Face Mesh identifies facial landmarks.
3. **Mouth Movement Detection:** The system measures the distance between the upper and lower lips. Opening the mouth activates volume control.
4. **Nose Movement Tracking:** The vertical movement of the nose is tracked to determine the required volume adjustment.
5. **Volume Calculation:** Facial movement is converted into a corresponding volume level.
6. **Volume Adjustment:** Pycaw updates the Windows master volume based on the calculated value.
7. **Smoothing:** A smoothing mechanism helps reduce sudden volume fluctuations.

## 🔄 System Workflow

```text
       Webcam Input
             |
             v
      Frame Capture
             |
             v
    Face Landmark Detection
       (MediaPipe)
             |
             v
     Facial Gesture Detection
             |
       +-----+------+
       |            |
       v            v
   Mouth Opening  Nose Movement
   (Activation)   (Volume Control)
       |            |
       +-----+------+
             |
             v
      Volume Calculation
             |
             v
       Volume Smoothing
             |
             v
     Windows Volume Control
          (Pycaw)
             |
             v
       Volume Updated
```

## 💻 Installation

### 1. Clone the repository

```bash
git clone https://github.com/2005Ayesha/facial-movement-volume-control.git
```

### 2. Navigate to the project directory

```bash
cd facial-movement-volume-control
```

### 3. Install the required libraries

```bash
pip install opencv-python mediapipe numpy pycaw comtypes
```

### 4. Run the project

Run your main Python file:

```bash
python main.py
```

Replace `main.py` with the actual filename of your main program if it is different.

## 📋 Requirements

- Windows operating system
- Python installed
- Working webcam
- Microphone or audio output is not required for volume control
- Required Python libraries installed

## 🌍 Applications

- Assistive technology for people with limited hand mobility.
- Hands-free computer interaction.
- Accessibility-focused human-computer interaction.
- Alternative computer control systems.

## ⚠️ Limitations

- Currently designed for Windows because it uses Pycaw.
- Performance may vary depending on lighting conditions.
- Webcam positioning and facial visibility can affect detection accuracy.
- Facial landmark detection may be affected by camera quality and movement.

## 🚀 Future Enhancements

- Improve gesture recognition accuracy.
- Add support for additional facial gestures.
- Develop cross-platform compatibility.
- Improve calibration and personalization.
- Integrate advanced machine learning techniques.

## 👨‍💻 Author

**Ayesha**

GitHub: [2005Ayesha](https://github.com/2005Ayesha)

---

⭐ If you find this project interesting, consider giving the repository a star..
