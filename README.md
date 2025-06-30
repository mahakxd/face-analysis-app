✨ Overview
Style Advisor Pro is a Python-based desktop application that uses computer vision to analyze facial features in real time and suggest styling ideas such as haircuts, contouring tips, makeup shades, and accessory styles.

✅ Live webcam feed with optional face mesh overlay
✅ Countdown timer for photo capture
✅ Automated detection (approximate):

Skin undertone (warm/cool/neutral)

Face shape

Nose shape

✅ Personalized suggestion ideas for:

Contouring and highlight

Haircuts and hair colors

Makeup recommendations

Eyewear and jewellery styles

📺 Demo Video
👉 https://youtu.be/N30L8C3mC_U

🖥️ Features
>Live Camera Feed with face mesh visualization

>Photo Capture with 3-second countdown

>Facial Landmark Analysis using MediaPipe

>Skin Tone & Face Shape Estimation

>Styling Suggestion Tabs including:

>Contour and highlight tips

>Recommended haircuts and hair colors

>Makeup shades

>Eyewear and jewellery suggestions

>Modern, easy-to-use Tkinter interface

🛠️ Tech Stack
Python 3

OpenCV – Camera capture and image processing

MediaPipe Face Mesh – Facial landmark detection

Tkinter – Desktop GUI

Pillow – Image handling

NumPy – Color analysis

📦 Installation
1️⃣ Clone this repository:

bash
Copy
Edit
git clone https://github.com/yourusername/style-advisor-pro.git
cd style-advisor-pro

2️⃣ Install dependencies:

bash
Copy
Edit
pip install opencv-python mediapipe pillow numpy

3️⃣ Run the app:

bash
Copy
Edit
python main.py

⚡ How It Works
>Opens your webcam in a desktop GUI

>Uses MediaPipe Face Mesh to detect 468 facial landmarks

>Estimates skin undertone and face shape with simple heuristics

>Generates suggested styling tips based on detected features

>Displays results in well-organized tabs

⚠️ Disclaimer
This app is for demonstration and educational purposes only.
It uses approximate computer vision methods to give styling ideas and is not meant to judge, classify, or assess anyone’s actual face type, skin tone, or appearance.
Results are intended as fun, inspirational suggestions and should not be used for any form of personal or social judgement.

🤝 Contributing
Contributions are welcome!
Feel free to fork the repo and open pull requests to improve analysis accuracy, add new styling recommendations, or refine the UI.


