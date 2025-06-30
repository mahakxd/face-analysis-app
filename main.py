import cv2
import mediapipe as mp
import numpy as np
import random
import time
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

face_mesh_model = mp.solutions.face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

drawing_utils = mp.solutions.drawing_utils
drawing_styles = mp.solutions.drawing_styles

class BeautyAdvisor:
    def __init__(self, window):
        self.window = window
        self.window.title("Beauty Advisor Pro")
        self.window.geometry("1200x800")
        self.window.configure(bg="#f0f2f5")
        
        self.visual_style = ttk.Style()
        self.visual_style.theme_use('clam')
        self.visual_style.configure('TNotebook', background='#f0f2f5')
        self.visual_style.configure('TNotebook.Tab', background='#d1d9e6', padding=[15,5])
        self.visual_style.map('TNotebook.Tab', background=[('selected', '#4a6fa5')], foreground=[('selected', 'white')])
        
        self.current_skin_tone = "Analyzing..."
        self.current_face_shape = "Analyzing..."
        self.current_eyebrows = "Analyzing..."
        self.current_lip_shape = "Analyzing..."
        self.current_nose_shape = "Analyzing..."
        self.suggested_highlights = []
        self.contouring_advice = []
        self.recommended_haircuts = []
        self.suggested_glasses = []
        self.recommended_earrings = []
        self.makeup_recommendations = []
        self.jewelry_suggestions = []
        self.camera = None
        self.current_photo = None
        self.camera_active = False
        self.show_face_mesh = True
        
        self.setup_interface()
        self.initialize_camera()

    def setup_interface(self):
        main_container = tk.Frame(self.window, bg="#f0f2f5")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        camera_panel = tk.Frame(main_container, bg="#ffffff", bd=0, highlightbackground="#c9d0de", highlightthickness=2, relief=tk.RAISED)
        camera_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        camera_header = tk.Frame(camera_panel, bg="#4a6fa5")
        camera_header.pack(fill=tk.X)
        tk.Label(camera_header, text="Live Camera", font=("Arial", 14, "bold"), bg="#4a6fa5", fg="white").pack(pady=8)
        
        self.camera_display = tk.Label(camera_panel, bg="#e6e9f0", bd=0)
        self.camera_display.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        button_panel = tk.Frame(camera_panel, bg="#ffffff")
        button_panel.pack(pady=(0,15))
        
        self.capture_button = tk.Button(
            button_panel, text="Capture Photo (3s)", command=self.prepare_capture,
            font=("Arial", 12, "bold"), bg="#4a6fa5", fg="white",
            activebackground="#3a5a80", relief=tk.FLAT, width=18, height=2
        )
        self.capture_button.pack(side=tk.LEFT, padx=10)
        
        self.mesh_button = tk.Button(
            button_panel, text="Toggle Face Mesh", command=self.switch_mesh_display,
            font=("Arial", 12, "bold"), bg="#6c757d", fg="white",
            activebackground="#5a6268", relief=tk.FLAT, width=18, height=2
        )
        self.mesh_button.pack(side=tk.LEFT, padx=10)
        
        results_panel = tk.Frame(main_container, bg="#ffffff", bd=0, highlightbackground="#c9d0de", highlightthickness=2, relief=tk.RAISED)
        results_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        results_header = tk.Frame(results_panel, bg="#4a6fa5")
        results_header.pack(fill=tk.X)
        tk.Label(results_header, text="Beauty Analysis", font=("Arial", 14, "bold"), bg="#4a6fa5", fg="white").pack(pady=8)
        
        self.analysis_notebook = ttk.Notebook(results_panel)
        self.analysis_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        facial_analysis_tab = tk.Frame(self.analysis_notebook, bg="#ffffff")
        self.analysis_notebook.add(facial_analysis_tab, text="Facial Analysis")
        
        features_section = tk.LabelFrame(facial_analysis_tab, text=" Your Features ", font=("Arial", 12, "bold"), bg="#ffffff", fg="#4a6fa5", bd=2, relief=tk.GROOVE, padx=10, pady=10)
        features_section.pack(fill=tk.X, padx=10, pady=5)
        
        feature_font = ("Arial", 10)
        feature_bg = "#f8f9fa"
        
        tk.Label(features_section, text="Skin Undertone:", font=feature_font, bg=feature_bg, fg="#495057").grid(row=0, column=0, sticky="w", pady=3)
        self.skin_tone_label = tk.Label(features_section, text=self.current_skin_tone, font=feature_font, bg=feature_bg, fg="#212529")
        self.skin_tone_label.grid(row=0, column=1, sticky="w", pady=3)
        
        tk.Label(features_section, text="Face Shape:", font=feature_font, bg=feature_bg, fg="#495057").grid(row=1, column=0, sticky="w", pady=3)
        self.face_shape_label = tk.Label(features_section, text=self.current_face_shape, font=feature_font, bg=feature_bg, fg="#212529")
        self.face_shape_label.grid(row=1, column=1, sticky="w", pady=3)
        
        tk.Label(features_section, text="Nose Shape:", font=feature_font, bg=feature_bg, fg="#495057").grid(row=2, column=0, sticky="w", pady=3)
        self.nose_shape_label = tk.Label(features_section, text=self.current_nose_shape, font=feature_font, bg=feature_bg, fg="#212529")
        self.nose_shape_label.grid(row=2, column=1, sticky="w", pady=3)
        
        contouring_section = tk.LabelFrame(facial_analysis_tab, text=" Contouring Guide ", font=("Arial", 12, "bold"), bg="#ffffff", fg="#4a6fa5", bd=2, relief=tk.GROOVE, padx=10, pady=10)
        contouring_section.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.contouring_text = tk.Text(contouring_section, wrap=tk.WORD, font=("Arial", 10), bg="#f8f9fa", fg="#212529", height=8, padx=10, pady=10, bd=0, highlightthickness=0)
        self.contouring_text.pack(fill=tk.BOTH, expand=True)
        self.contouring_text.insert(tk.END, "Take a photo to get personalized contouring tips!")
        self.contouring_text.config(state=tk.DISABLED)
        
        hair_tab = tk.Frame(self.analysis_notebook, bg="#ffffff")
        self.analysis_notebook.add(hair_tab, text="Hair & Style")
        
        highlights_section = tk.LabelFrame(hair_tab, text=" Suggested Highlights ", font=("Arial", 12, "bold"), bg="#ffffff", fg="#4a6fa5", bd=2, relief=tk.GROOVE, padx=10, pady=10)
        highlights_section.pack(fill=tk.X, padx=10, pady=5)
        
        self.highlights_text = tk.Text(highlights_section, wrap=tk.WORD, font=("Arial", 10), bg="#f8f9fa", fg="#212529", height=4, padx=10, pady=10, bd=0, highlightthickness=0)
        self.highlights_text.pack(fill=tk.BOTH, expand=True)
        self.highlights_text.insert(tk.END, "Will be suggested based on your skin tone")
        self.highlights_text.config(state=tk.DISABLED)
        
        haircut_section = tk.LabelFrame(hair_tab, text=" Recommended Haircuts ", font=("Arial", 12, "bold"), bg="#ffffff", fg="#4a6fa5", bd=2, relief=tk.GROOVE, padx=10, pady=10)
        haircut_section.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.haircut_text = tk.Text(haircut_section, wrap=tk.WORD, font=("Arial", 10), bg="#f8f9fa", fg="#212529", height=6, padx=10, pady=10, bd=0, highlightthickness=0)
        self.haircut_text.pack(fill=tk.BOTH, expand=True)
        self.haircut_text.insert(tk.END, "Will be suggested based on your face shape")
        self.haircut_text.config(state=tk.DISABLED)
        
        makeup_tab = tk.Frame(self.analysis_notebook, bg="#ffffff")
        self.analysis_notebook.add(makeup_tab, text="Makeup")
        
        self.makeup_text = tk.Text(makeup_tab, wrap=tk.WORD, font=("Arial", 10), bg="#f8f9fa", fg="#212529", padx=15, pady=15, bd=0, highlightthickness=0)
        self.makeup_text.pack(fill=tk.BOTH, expand=True)
        self.makeup_text.insert(tk.END, "Personalized makeup recommendations will appear here")
        self.makeup_text.config(state=tk.DISABLED)
        
        accessories_tab = tk.Frame(self.analysis_notebook, bg="#ffffff")
        self.analysis_notebook.add(accessories_tab, text="Accessories")
        
        glasses_section = tk.LabelFrame(accessories_tab, text=" Eyewear Frames ", font=("Arial", 12, "bold"), bg="#ffffff", fg="#4a6fa5", bd=2, relief=tk.GROOVE, padx=10, pady=10)
        glasses_section.pack(fill=tk.X, padx=10, pady=5)
        
        self.glasses_text = tk.Text(glasses_section, wrap=tk.WORD, font=("Arial", 10), bg="#f8f9fa", fg="#212529", height=4, padx=10, pady=10, bd=0, highlightthickness=0)
        self.glasses_text.pack(fill=tk.BOTH, expand=True)
        self.glasses_text.insert(tk.END, "Suggested based on your face shape")
        self.glasses_text.config(state=tk.DISABLED)
        
        jewelry_section = tk.LabelFrame(accessories_tab, text=" Jewellery ", font=("Arial", 12, "bold"), bg="#ffffff", fg="#4a6fa5", bd=2, relief=tk.GROOVE, padx=10, pady=10)
        jewelry_section.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.jewelry_text = tk.Text(jewelry_section, wrap=tk.WORD, font=("Arial", 10), bg="#f8f9fa", fg="#212529", height=6, padx=10, pady=10, bd=0, highlightthickness=0)
        self.jewelry_text.pack(fill=tk.BOTH, expand=True)
        self.jewelry_text.insert(tk.END, "Metal tones and styles that complement you")
        self.jewelry_text.config(state=tk.DISABLED)
    
    def switch_mesh_display(self):
        self.show_face_mesh = not self.show_face_mesh
        if hasattr(self, 'last_camera_frame'):
            self.process_face_image(self.last_camera_frame, update_only=True)
    
    def initialize_camera(self):
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            messagebox.showerror("Error", "Could not open camera")
            return
        self.update_camera_feed()
    
    def update_camera_feed(self):
        if not self.camera_active and self.camera is not None:
            success, frame = self.camera.read()
            if success:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (640, 480))
                
                self.last_camera_frame = frame.copy()
                
                if self.show_face_mesh:
                    frame = self.draw_face_landmarks(frame)
                
                display_image = Image.fromarray(frame)
                self.current_photo = ImageTk.PhotoImage(image=display_image)
                self.camera_display.config(image=self.current_photo)
        self.window.after(15, self.update_camera_feed)
    
    def draw_face_landmarks(self, image):
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        face_results = face_mesh_model.process(image_bgr)
        
        if face_results.multi_face_landmarks:
            for landmarks in face_results.multi_face_landmarks:
                drawing_utils.draw_landmarks(
                    image=image,
                    landmark_list=landmarks,
                    connections=mp.solutions.face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=drawing_styles.get_default_face_mesh_tesselation_style())
                
                drawing_utils.draw_landmarks(
                    image=image,
                    landmark_list=landmarks,
                    connections=mp.solutions.face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=drawing_styles.get_default_face_mesh_contours_style())
        
        return image
    
    def prepare_capture(self):
        self.camera_active = True
        self.capture_button.config(state=tk.DISABLED)
        self.mesh_button.config(state=tk.DISABLED)
        
        for countdown in range(3, 0, -1):
            success, frame = self.camera.read()
            if success:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (640, 480))
                
                cv2.putText(frame, f"Smile! {countdown}...", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 3)
                
                if self.show_face_mesh:
                    frame = self.draw_face_landmarks(frame)
                
                display_image = Image.fromarray(frame)
                self.current_photo = ImageTk.PhotoImage(image=display_image)
                self.camera_display.config(image=self.current_photo)
                self.window.update()
                time.sleep(1)
        
        success, final_frame = self.camera.read()
        if success:
            final_frame = cv2.cvtColor(final_frame, cv2.COLOR_BGR2RGB)
            final_frame = cv2.resize(final_frame, (640, 480))
            self.last_camera_frame = final_frame.copy()
            self.process_face_image(final_frame)
        
        self.camera_active = False
        self.capture_button.config(state=tk.NORMAL)
        self.mesh_button.config(state=tk.NORMAL)
    
    def process_face_image(self, frame, update_only=False):
        image_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        face_results = face_mesh_model.process(image_bgr)
        
        if face_results.multi_face_landmarks:
            landmarks = face_results.multi_face_landmarks[0]
            
            self.current_skin_tone = self.analyze_skin_tone(image_bgr, landmarks)
            self.current_face_shape = self.determine_face_structure(landmarks, image_bgr.shape)
            self.current_eyebrows, self.current_lip_shape = self.describe_facial_features(landmarks, image_bgr.shape)
            self.current_nose_shape = self.analyze_nose_structure(landmarks, image_bgr.shape)
            
            self.suggested_highlights = self.recommend_hair_highlights(self.current_skin_tone, self.current_face_shape)
            self.contouring_advice = self.suggest_contouring_techniques(self.current_face_shape, self.current_nose_shape, self.current_skin_tone)
            self.recommended_haircuts = self.suggest_hairstyles(self.current_face_shape)
            self.suggested_glasses = self.recommend_eyewear(self.current_face_shape)
            self.recommended_earrings = self.suggest_earring_styles(self.current_face_shape)
            self.makeup_recommendations = self.recommend_makeup_products(self.current_skin_tone)
            self.jewelry_suggestions = self.suggest_jewelry_metals(self.current_skin_tone)
            
            self.update_analysis_results()
            
            if not update_only:
                processed_frame = frame.copy()
                if self.show_face_mesh:
                    processed_frame = self.draw_face_landmarks(processed_frame)
                
                display_image = Image.fromarray(processed_frame)
                self.current_photo = ImageTk.PhotoImage(image=display_image)
                self.camera_display.config(image=self.current_photo)
        else:
            messagebox.showwarning("No Face", "Couldn't detect a face. Please try again with better lighting.")
    
    def update_analysis_results(self):
        self.skin_tone_label.config(text=self.current_skin_tone)
        self.face_shape_label.config(text=self.current_face_shape)
        self.nose_shape_label.config(text=self.current_nose_shape)
        
        self.contouring_text.config(state=tk.NORMAL)
        self.contouring_text.delete(1.0, tk.END)
        for tip in self.contouring_advice:
            self.contouring_text.insert(tk.END, f"• {tip}\n")
        self.contouring_text.config(state=tk.DISABLED)
        
        self.highlights_text.config(state=tk.NORMAL)
        self.highlights_text.delete(1.0, tk.END)
        for highlight in self.suggested_highlights:
            self.highlights_text.insert(tk.END, f"• {highlight}\n")
        self.highlights_text.config(state=tk.DISABLED)
        
        self.haircut_text.config(state=tk.NORMAL)
        self.haircut_text.delete(1.0, tk.END)
        for haircut in self.recommended_haircuts:
            self.haircut_text.insert(tk.END, f"• {haircut}\n")
        self.haircut_text.config(state=tk.DISABLED)
        
        self.makeup_text.config(state=tk.NORMAL)
        self.makeup_text.delete(1.0, tk.END)
        self.makeup_text.insert(tk.END, "Makeup that will complement you:\n\n")
        for tip in self.makeup_recommendations:
            self.makeup_text.insert(tk.END, f"• {tip}\n")
        self.makeup_text.config(state=tk.DISABLED)
        
        self.glasses_text.config(state=tk.NORMAL)
        self.glasses_text.delete(1.0, tk.END)
        for style in self.suggested_glasses:
            self.glasses_text.insert(tk.END, f"• {style}\n")
        self.glasses_text.config(state=tk.DISABLED)
        
        self.jewelry_text.config(state=tk.NORMAL)
        self.jewelry_text.delete(1.0, tk.END)
        self.jewelry_text.insert(tk.END, "Best metal tones for you:\n\n")
        for metal in self.jewelry_suggestions:
            self.jewelry_text.insert(tk.END, f"• {metal}\n")
        self.jewelry_text.config(state=tk.DISABLED)
    
    def close_application(self):
        if self.camera is not None:
            self.camera.release()
        self.window.destroy()

    def analyze_skin_tone(self, image, face_landmarks):
        height, width = image.shape[:2]
        
        sampling_points = [1, 4, 33, 94, 152, 263, 296, 168, 197, 2, 326]
        
        sampled_coordinates = []
        for point in sampling_points:
            landmark = face_landmarks.landmark[point]
            x_pos, y_pos = int(landmark.x * width), int(landmark.y * height)
            if 0 <= x_pos < width and 0 <= y_pos < height:
                sampled_coordinates.append((x_pos, y_pos))
        
        color_samples = [image[y, x] for x, y in sampled_coordinates]
        
        if not color_samples:
            return "could not determine"
        
        average_color = np.mean(color_samples, axis=0)
        return self.determine_undertone(average_color)

    def determine_undertone(self, color_values):
        blue, green, red = color_values
        
        red_blue_diff = red - blue
        green_blue_diff = green - blue
        
        if red_blue_diff > 15 and green_blue_diff > 15:
            if red > green * 1.1:
                return "warm (golden/peachy)"
            elif green > red * 1.1:
                return "neutral (olive)"
            else:
                return "neutral (balanced)"
        elif red_blue_diff < -10:
            return "cool (pinkish)"
        else:
            return "neutral (balanced)"

    def determine_face_structure(self, landmarks, image_dimensions):
        height, width = image_dimensions[:2]
        landmark_points = [(int(landmark.x * width), int(landmark.y * height)) for landmark in landmarks.landmark]
        
        jaw_width = abs(landmark_points[454][0] - landmark_points[234][0])
        forehead_width = abs(landmark_points[21][0] - landmark_points[251][0])
        face_height = abs(landmark_points[10][1] - landmark_points[152][1])
        cheek_width = abs(landmark_points[454][0] - landmark_points[234][0])
        
        jaw_to_forehead = jaw_width / forehead_width
        height_to_width = face_height / cheek_width
        
        if height_to_width > 1.5:
            if jaw_to_forehead < 0.85:
                return "heart (wider forehead, narrow chin)"
            elif 0.85 <= jaw_to_forehead <= 1.15:
                return "oval (balanced proportions)"
            else:
                return "oblong (long and narrow)"
        elif height_to_width <= 1.5:
            if jaw_to_forehead > 1.1:
                return "square (strong jawline)"
            elif abs(cheek_width - jaw_width) < 0.1 * cheek_width:
                return "round (similar width and length)"
            else:
                return "diamond (wide cheekbones)"
        return "oval"

    def analyze_nose_structure(self, landmarks, image_dimensions):
        height, width = image_dimensions[:2]
        landmark_points = [(int(landmark.x * width), int(landmark.y * height)) for landmark in landmarks.landmark]
        
        face_width = abs(landmark_points[454][0] - landmark_points[234][0])
        face_height = abs(landmark_points[10][1] - landmark_points[152][1])
        
        nose_width = abs(landmark_points[129][0] - landmark_points[358][0])
        nose_length = abs(landmark_points[1][1] - landmark_points[4][1])
        bridge_width = abs(landmark_points[44][0] - landmark_points[276][0])
        
        width_proportion = nose_width / face_width
        length_proportion = nose_length / face_height
        bridge_proportion = bridge_width / nose_width
        
        if width_proportion > 0.25:
            if bridge_proportion < 0.3:
                return "wide with narrow bridge"
            else:
                return "wide (broad nostrils)"
        elif width_proportion < 0.15:
            return "narrow (slim)"
        elif length_proportion > 0.3:
            return "long (prominent)"
        elif bridge_proportion < 0.25:
            return "thin (delicate bridge)"
        elif length_proportion < 0.2:
            return "short (button-like)"
        else:
            return "balanced (classic proportions)"

    def describe_facial_features(self, landmarks, image_dimensions):
        height, width = image_dimensions[:2]
        landmark_points = [(int(landmark.x * width), int(landmark.y * height)) for landmark in landmarks.landmark]

        eyebrow_thickness = abs(landmark_points[70][1] - landmark_points[105][1])
        eyebrow_style = "arched" if eyebrow_thickness < 10 else "straight"

        lip_height = abs(landmark_points[13][1] - landmark_points[14][1])
        lip_width = abs(landmark_points[78][0] - landmark_points[308][0])
        lip_ratio = lip_width / max(lip_height, 1)

        if lip_ratio < 1.2:
            lip_style = "round"
        elif lip_height > 16:
            lip_style = "full"
        elif lip_height < 8:
            lip_style = "thin"
        elif landmark_points[13][1] < landmark_points[14][1] and lip_width > 90:
            lip_style = "bunny"
        elif landmark_points[14][1] - landmark_points[13][1] > 12 and lip_width > 95:
            lip_style = "heart"
        elif abs(landmark_points[78][0] - landmark_points[308][0]) > 120 and abs(landmark_points[13][1] - landmark_points[14][1]) < 10:
            lip_style = "diamond"
        else:
            lip_style = "balanced"

        return eyebrow_style, lip_style

    def suggest_contouring_techniques(self, face_shape, nose_shape, skin_tone):
        contour_suggestions = []
        
        if "round" in face_shape:
            contour_suggestions.append("Apply contour along temples and under cheekbones to elongate face")
            contour_suggestions.append("Focus on creating angles with your contour")
        elif "square" in face_shape:
            contour_suggestions.append("Soften jawline with contour along the edges")
            contour_suggestions.append("Round out the forehead corners slightly")
        elif "heart" in face_shape:
            contour_suggestions.append("Contour temples to balance wider forehead")
            contour_suggestions.append("Add slight contour to chin point to soften")
        elif "oval" in face_shape:
            contour_suggestions.append("Light contouring just to enhance natural structure")
        elif "oblong" in face_shape:
            contour_suggestions.append("Contour forehead and chin to visually shorten face")
        elif "diamond" in face_shape:
            contour_suggestions.append("Contour cheekbone peaks to soften angles")
        
        if "wide" in nose_shape:
            contour_suggestions.append("Apply contour along sides of nose to create slimming effect")
        elif "narrow" in nose_shape:
            contour_suggestions.append("Use subtle highlight down nose bridge to enhance")
        elif "long" in nose_shape:
            contour_suggestions.append("Apply contour at nose tip to visually shorten")
        elif "short" in nose_shape:
            contour_suggestions.append("Highlight down nose bridge to elongate appearance")
        elif "thin" in nose_shape:
            contour_suggestions.append("Minimal nose contouring needed")
        
        if "warm" in skin_tone:
            contour_suggestions.append("Use warm-toned contour shades (taupe, caramel)")
        elif "cool" in skin_tone:
            contour_suggestions.append("Use cool-toned contour shades (ash brown, grey-brown)")
        else:
            contour_suggestions.append("Use neutral contour shades (mocha, soft brown)")
        
        return contour_suggestions

    def recommend_hair_highlights(self, skin_tone, face_shape):
        warm_colors = ['caramel', 'honey blonde', 'golden brown', 'coffee brown', 'rust']
        cool_colors = ['ash blonde', 'burgundy', 'cool brown', 'plum', 'wine red']
        neutral_colors = ['chocolate brown', 'auburn', 'chestnut', 'bronze']

        if "warm" in skin_tone:
            base_colors = warm_colors
        elif "cool" in skin_tone:
            base_colors = cool_colors
        else:
            base_colors = neutral_colors

        if "round" in face_shape or "square" in face_shape:
            base_colors.extend(['face-framing highlights', 'dimensional coloring'])
        elif "long" in face_shape:
            base_colors.extend(['horizontal emphasis colors', 'soft balayage'])

        return random.sample(base_colors, min(4, len(base_colors)))

    def suggest_hairstyles(self, face_shape):
        hairstyle_map = {
            "oval": ["long layers", "wavy bob", "side-swept bangs", "face-framing layers"],
            "round": ["long straight", "layered lob", "pixie cut", "asymmetrical bob"],
            "heart": ["chin-length bob", "deep side part", "fringe", "textured crop"],
            "square": ["soft curls", "feathered layers", "textured bob", "tapered cut"],
            "oblong": ["blunt bangs", "chin-length bob", "curtain bangs", "voluminous curls"],
            "diamond": ["side-parted styles", "long layers", "soft bangs", "shoulder-length cuts"]
        }
        
        for shape in hairstyle_map:
            if shape in face_shape.lower():
                return hairstyle_map[shape]
        
        return hairstyle_map["oval"]

    def recommend_eyewear(self, face_shape):
        glasses_styles = {
            "oval": ["square frames", "rectangle frames", "aviators"],
            "round": ["cat-eye", "angular frames", "geometric frames"],
            "heart": ["bottom-heavy frames", "rimless frames", "lightweight metal frames"],
            "square": ["round frames", "oval frames", "browline glasses"],
            "oblong": ["oversized frames", "decorative temples", "low bridge designs"],
            "diamond": ["oval frames", "semi-rimless", "light-colored frames"]
        }
        
        for shape in glasses_styles:
            if shape in face_shape.lower():
                return glasses_styles[shape]
        
        return glasses_styles["oval"]

    def suggest_earring_styles(self, face_shape):
        earring_styles = {
            "oval": ["hoops", "teardrops", "long dangles"],
            "round": ["drop earrings", "vertical lines", "angled studs"],
            "heart": ["teardrop", "chandelier", "bottom-heavy styles"],
            "square": ["round hoops", "curved designs", "drops"],
            "oblong": ["cluster studs", "short danglers", "wide designs"],
            "diamond": ["elongated shapes", "geometric designs", "medium-length drops"]
        }
        
        for shape in earring_styles:
            if shape in face_shape.lower():
                return earring_styles[shape]
        
        return earring_styles["oval"]

    def recommend_makeup_products(self, skin_tone):
        if "warm" in skin_tone:
            return [
                "Bronze or peach blush",
                "Gold or copper eyeshadow",
                "Coral or terracotta lips",
                "Warm-toned highlighter"
            ]
        elif "cool" in skin_tone:
            return [
                "Rosy or berry blush",
                "Cool-toned eyeshadow (taupe, mauve)",
                "Berry or mauve lips",
                "Icy highlighter"
            ]
        else:
            return [
                "Neutral blush (dusty rose)",
                "Brown or bronze eyeshadow",
                "Nude or pink lipstick",
                "Champagne highlighter"
            ]

    def suggest_jewelry_metals(self, skin_tone):
        if "warm" in skin_tone:
            return ["Gold", "Rose gold", "Brass", "Copper"]
        elif "cool" in skin_tone:
            return ["Silver", "White gold", "Platinum", "Palladium"]
        else:
            return ["Gold", "Silver", "Rose gold", "Mixed metals"]

if __name__ == "__main__":
    application_window = tk.Tk()
    beauty_app = BeautyAdvisor(application_window)
    application_window.protocol("WM_DELETE_WINDOW", beauty_app.close_application)
    application_window.mainloop()