import cv2
import numpy as np
import mediapipe as mp

# ----------------------------
# MediaPipe setup
# ----------------------------
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False,
                    model_complexity=1,
                    enable_segmentation=False,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5)

# ----------------------------
# Angle calculation function
# ----------------------------
def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    return np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))

# ----------------------------
# Extract angles from video (Push-ups)
# ----------------------------
def extract_angles(video_path):
    cap = cv2.VideoCapture(video_path)
    angles_seq = []
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert to RGB for MediaPipe
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        keypoints_flat = np.zeros(33*2)  # 33 landmarks x (x,y)
        if results.pose_landmarks:
            for i, lm in enumerate(results.pose_landmarks.landmark):
                keypoints_flat[i*2] = lm.x * width
                keypoints_flat[i*2 + 1] = lm.y * height

            # Calculate angles using proper MediaPipe indices
            left_elbow = calculate_angle(keypoints_flat[11*2:11*2+2],
                                         keypoints_flat[13*2:13*2+2],
                                         keypoints_flat[15*2:15*2+2])

            right_elbow = calculate_angle(keypoints_flat[12*2:12*2+2],
                                          keypoints_flat[14*2:14*2+2],
                                          keypoints_flat[16*2:16*2+2])

            back_angle = calculate_angle(keypoints_flat[11*2:11*2+2],
                                         keypoints_flat[23*2:23*2+2],
                                         keypoints_flat[25*2:25*2+2])

            left_knee = calculate_angle(keypoints_flat[23*2:23*2+2],
                                        keypoints_flat[25*2:25*2+2],
                                        keypoints_flat[27*2:27*2+2])

            right_knee = calculate_angle(keypoints_flat[24*2:24*2+2],
                                         keypoints_flat[26*2:26*2+2],
                                         keypoints_flat[28*2:28*2+2])

            angles_seq.append([left_elbow, right_elbow, back_angle, left_knee, right_knee])
        else:
            angles_seq.append([0,0,0,0,0])

    cap.release()
    return np.array(angles_seq)

# -----------------------------------------
# Tricep Dips Angle Extraction Function
# -----------------------------------------
def extract_tricep_dips_angles(video_path):
    cap = cv2.VideoCapture(video_path)
    angles_seq = []
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # Key joints for tricep dips (using both sides)
            # Left side
            left_shoulder = [landmarks[11].x * width, landmarks[11].y * height]
            left_elbow = [landmarks[13].x * width, landmarks[13].y * height]
            left_wrist = [landmarks[15].x * width, landmarks[15].y * height]
            left_hip = [landmarks[23].x * width, landmarks[23].y * height]
            
            # Right side
            right_shoulder = [landmarks[12].x * width, landmarks[12].y * height]
            right_elbow = [landmarks[14].x * width, landmarks[14].y * height]
            right_wrist = [landmarks[16].x * width, landmarks[16].y * height]
            right_hip = [landmarks[24].x * width, landmarks[24].y * height]

            # Calculate key angles for tricep dips
            left_elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
            right_elbow_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
            
            # Shoulder angles (to check body lean/position)
            left_shoulder_angle = calculate_angle(left_elbow, left_shoulder, left_hip)
            right_shoulder_angle = calculate_angle(right_elbow, right_shoulder, right_hip)

            angles_seq.append([left_elbow_angle, right_elbow_angle, 
                             left_shoulder_angle, right_shoulder_angle])

    cap.release()
    return np.array(angles_seq)

# -----------------------------------------
# Pull-up Angle Extraction Function
# -----------------------------------------
def extract_pullup_angles(video_path):
    cap = cv2.VideoCapture(video_path)
    angles_seq = []
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # Get coordinates (left side for consistency)
            shoulder = [landmarks[11].x * width, landmarks[11].y * height]
            elbow = [landmarks[13].x * width, landmarks[13].y * height]
            wrist = [landmarks[15].x * width, landmarks[15].y * height]
            hip = [landmarks[23].x * width, landmarks[23].y * height]

            # Calculate key angles for pull-ups
            elbow_angle = calculate_angle(wrist, elbow, shoulder)
            shoulder_angle = calculate_angle(elbow, shoulder, hip)

            angles_seq.append([elbow_angle, shoulder_angle])

    cap.release()
    return np.array(angles_seq)

# -----------------------------------------
# Plank Angle Extraction Function
# -----------------------------------------
def extract_plank_angles(video_path):
    cap = cv2.VideoCapture(video_path)
    angles_seq = []
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # Core joints for planks — check body alignment
            shoulder = [landmarks[11].x * width, landmarks[11].y * height]
            hip = [landmarks[23].x * width, landmarks[23].y * height]
            ankle = [landmarks[27].x * width, landmarks[27].y * height]

            elbow = [landmarks[13].x * width, landmarks[13].y * height]
            wrist = [landmarks[15].x * width, landmarks[15].y * height]
            knee = [landmarks[25].x * width, landmarks[25].y * height]

            # Calculate angles relevant to plank posture
            back_angle = calculate_angle(shoulder, hip, ankle)     # Body straightness
            elbow_angle = calculate_angle(shoulder, elbow, wrist)  # Arm support angle
            hip_angle = calculate_angle(shoulder, hip, knee)       # Hip drop/raise

            angles_seq.append([back_angle, elbow_angle, hip_angle])

    cap.release()
    return np.array(angles_seq)

# -----------------------------------------
# Squat Angle Extraction Function
# -----------------------------------------
def extract_squat_angles(video_path):
    cap = cv2.VideoCapture(video_path)
    angles_seq = []
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # Key joints for squats (using left side for consistency)
            hip = [landmarks[23].x * width, landmarks[23].y * height]
            knee = [landmarks[25].x * width, landmarks[25].y * height]
            ankle = [landmarks[27].x * width, landmarks[27].y * height]
            
            shoulder = [landmarks[11].x * width, landmarks[11].y * height]
            
            # For right side comparison
            hip_r = [landmarks[24].x * width, landmarks[24].y * height]
            knee_r = [landmarks[26].x * width, landmarks[26].y * height]
            ankle_r = [landmarks[28].x * width, landmarks[28].y * height]

            # Calculate key angles for squats
            left_knee_angle = calculate_angle(hip, knee, ankle)      # Knee bend depth
            right_knee_angle = calculate_angle(hip_r, knee_r, ankle_r)  # Right knee
            
            left_hip_angle = calculate_angle(shoulder, hip, knee)    # Hip flexion
            right_hip_angle = calculate_angle(shoulder, hip_r, knee_r)  # Right hip
            
            # Back angle (torso lean) - shoulder to hip to ankle
            back_angle = calculate_angle(shoulder, hip, ankle)

            angles_seq.append([left_knee_angle, right_knee_angle, left_hip_angle, 
                             right_hip_angle, back_angle])

    cap.release()
    return np.array(angles_seq)