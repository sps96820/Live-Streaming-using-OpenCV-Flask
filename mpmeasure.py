import cv2
from math import sqrt
from pip import main
import time
from PIL import Image, ImageTk
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
close = 0

# Function for mediapipe code
def media(image):
    measurements = []
    # For static images:
    BG_COLOR = (192, 192, 192) # gray
    with mp_pose.Pose(
        static_image_mode=True,
        model_complexity=2,
        enable_segmentation=True,
        min_detection_confidence=0.5) as pose:
            image_height, image_width, _ = image.shape
            # Convert the BGR image to RGB before processing.
            results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

            if not results.pose_landmarks:
                print("error exiting")
                return 0
            print(f'Nose coordinates: ('
                f'{results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].x * image_width}, '
                f'{results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].y * image_height})')
            # # Draw segmentation on the image.
            # # To improve segmentation around boundaries, consider applying a joint
            # # bilateral filter to "results.segmentation_mask" with "image".
            # condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.1
            # bg_image = np.zeros(image.shape, dtype=np.uint8)
            # bg_image[:] = BG_COLOR
            # annotated_image = np.where(condition, annotated_image, bg_image)
            # # Draw pose landmarks on the image.
            # mp_drawing.draw_landmarks(
            #     annotated_image,
            #     results.pose_landmarks,
            #     mp_pose.POSE_CONNECTIONS,
            #     landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
            # cv2.imwrite('/tmp/annotated_image' + str(idx) + '.png', annotated_image)
            reyebrow = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_EYE]
            rheel = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HEEL]
            lshoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
            rshoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            rwrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
            rhip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
            lhip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
            rankle = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE]

            height = abs(reyebrow.y*image_height - rheel.y*image_height)
            shoulder = abs(lshoulder.x*image_width - rshoulder.x*image_width)
            armsx = abs(rshoulder.x*image_width - rwrist.x*image_width)
            armsy = abs(rshoulder.y*image_height - rwrist.y*image_height)
            arms = sqrt(armsx*armsx + armsy*armsy)
            #measurements.append(height, shoulder, arms)
            measurements.append(height)
            measurements.append(shoulder)
            measurements.append(arms)
            print("measurements")
            print(measurements)
            return measurements


            
