import cv2
from arucoClass import scaleAq as aru
import mpmeasure as mpm
from PIL import Image, ImageTk
import threading
import numpy as np
from queue import Queue
import time
import mediapipe as mp



class camClass:
    def __init__(self):
        self.q = Queue()
        self.heightq = Queue()
        self.armq = Queue()
        self.shoulderq = Queue()
        self.instructionq = Queue()
        
        #media pipe definitions
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.pose = self.mp_pose.Pose(model_complexity=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        
        
        self.sca = aru()
        
        self.heightq.put(0)
        self.armq.put(0)
        self.shoulderq.put(0)
        self.instructionq.put("None")
        
        self.arml = 0
        self.shoulderl = 0
        self.height = 0
        self.instruction = "None"
        self.q.put(False)
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        
    def imaging(self):
        self.instructionq.put("start")
        time.sleep(10)
        
        imagearr = []
        for i in range(30):
            _, tempCap = self.cap.read()
            imagearr.append(tempCap)
            
        self.q.put(False)
        print("Put checkerboard down and hold aruco marker", flush=True)
        self.instructionq.put("Paper Up")
        time.sleep(2)
        corrected= []
        for i in range(30):
            _, tempCap = self.cap.read()
            corrected.append(tempCap)
        
        ratio = self.scale(corrected)

        while ratio < 4:
            arucoArray = []
            time.sleep(2)
            for i in range(30):
                _, tempCap = self.cap.read()
                arucoArray.append(tempCap)
                
            ratio = self.scale(arucoArray)
            
            
        mediapipeImgs = []
        self.instructionq.put("Papers Down")
        time.sleep(3)
        self.instructionq.put("be still")
        time.sleep(2)
            
        for i in range(30):
            _, tempCap = self.cap.read()
            mediapipeImgs.append(tempCap)
                
        self.instructionq.put("wait")
        measurelist = [[] for i in range(3)]
        #for image in corrected:
        for image in mediapipeImgs:
            temparray = mpm.media(image)
            print(tempCap, flush=True)
            measurelist[0].append(temparray[0])
            measurelist[1].append(temparray[1])
            measurelist[2].append(temparray[2])
        avglist = self.measureavg(measurelist, ratio)
        print("Height: ", avglist[0], "\nShoulder: ", avglist[1], "\nArms: ", avglist[2], flush=True)

        self.instructionq.put("end")
        self.heightq.put(avglist[0])
        self.shoulderq.put(avglist[1])
        self.armq.put(avglist[2])
             
    def scale(self, corrected):
        #sca = aru()
        ratio = []
        # Get the scales for each image
        for img in corrected:
            #print("in for", flush = True)
            if self.sca.scale(img):
                #print(sca.scale(img), flush=True)
                ratio.append(self.sca.ratio)
        print("after for in scale", flush=True)
        # Check for issues
        if len(ratio) < 15:
            print("no aruco images found", flush=True)
            return 0
        # Calculating the average scale
        temp = 0
        for num in ratio:
            temp = temp + num
        temp = temp / len(ratio)
        return temp

    def measureavg(self, measurelist, ratio):
        height = 0
        shoulder = 0
        arms = 0
        # Add together all of the measurements in the lists
        counter = 0
        heightL = 0
        shoulderL = 0
        armsL = 0
        for list in measurelist:
            if counter == 0:
                heightL = len(list)
            elif counter == 1:
                shoulderL = len(list)
            elif counter == 2:
                armsL = len(list)
            for num in list:
                if counter == 0:
                    height += num
                elif counter == 1:
                    shoulder += num
                elif counter == 2:
                    arms += num
            counter += 1
            #height = list[0]
            #shoulder = list[1]
            #arms = list[2]
        print(height)
        print(shoulder)
        print(arms)
        # Average the measurements
        height = height / heightL
        shoulder = shoulder / shoulderL
        arms = arms / armsL
        # Scale and return
        height = height / ratio
        shoulder = shoulder / ratio
        arms = arms / ratio
        return height, shoulder, arms
    
    def update_frame(self):
        global label
        calibBool = False
        _, frame = self.cap.read()
        image_height, image_width, _ = frame.shape

        #if len(imagearr) != 30:
                #imagearr.append(frame)
            
            #with mp_pose.Pose(
            #       min_detection_confidence=0.5,
            #      min_tracking_confidence=0.5) as pose:

        results = self.pose.process(frame)
        self.mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style())
        
        
        self.sca.scale(frame)
        if self.sca.bboxs:
            self.sca.scale(frame)
            int_corners = np.int0(self.sca.bboxs)
            cv2.polylines(frame, int_corners, True, (0, 255, 0), 2)    
       
       
        if results.pose_landmarks != None:
            rshoulder = results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            lshoulder = results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            rwrist = results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST]
            relbow = results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_ELBOW]
            relbowx = relbow.x * image_width
            relbowy = relbow.y * image_height
            nose = results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.NOSE]
            nosex = nose.x * image_width
            nosey = nose.y * image_height
            rshoulderx = rshoulder.x * image_width
            rshouldery = rshoulder.y * image_height
            chestx = ((rshoulder.x * image_width) + (lshoulder.x * image_width)) / 2
            chesty = ((rshoulder.y * image_height) + (lshoulder.y * image_height)) / 2
                
            if not self.instructionq.empty():
                self.instruction = self.instructionq.get()
            if not self.heightq.empty():
                self.height = self.heightq.get()
            if not self.armq.empty():
                self.arml = self.armq.get()
            if not self.shoulderq.empty():
                self.shoulderl = self.shoulderq.get()
                
            if self.instruction == "Paper Up":
                cv2.putText(frame, "Hold Aruco Marker up against chest", (int(image_width*.02), int(image_height*.85)), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 205, 50), 3)
            elif self.instruction == "Papers Down":
                cv2.putText(frame, "Put papers down", (int(image_width*.05), int(image_height*.85)), cv2.FONT_HERSHEY_COMPLEX, 1.05, (50, 205, 50), 3)
            elif self.instruction == "be still":
                cv2.putText(frame, "Stand still and hold arms to side", (int(image_width*.02), int(image_height*.85)), cv2.FONT_HERSHEY_COMPLEX, 1.05, (50, 205, 50), 3)
            elif self.instruction == "start":
                cv2.putText(frame, "Ensure full body is in frame", (int(image_width*.05), int(image_height*.85)), cv2.FONT_HERSHEY_COMPLEX, 1.05, (50, 205, 50), 3)
            elif self.instruction == "wait":
                cv2.putText(frame, "Calculating...", (int(image_width*.05), int(image_height*.85)), cv2.FONT_HERSHEY_COMPLEX, 1.05, (50, 205, 50), 3)
            elif self.instruction == "end":
                cv2.putText(frame, "Measurements are shown above!", (int(image_width*.05), int(image_height*.85)), cv2.FONT_HERSHEY_COMPLEX, 1.05, (50, 205, 50), 3)
                
                
            if self.arml != 0:
                cv2.putText(frame, "Arm Length: {}".format(round(self.arml,1)), (int(relbowx), int(relbowy)), cv2.FONT_HERSHEY_COMPLEX, 1.05, (50, 205, 50), 3)
            if self.height != 0:
                cv2.putText(frame, "Height: {}".format(round(self.height, 1)), (int(nosex), int(nosey) - 40), cv2.FONT_HERSHEY_COMPLEX, 1.1, (50, 205, 50), 3)
            if self.shoulderl != 0:
                cv2.putText(frame, "Shoulder Width: {}".format(round(self.shoulderl, 1)), (int(rshoulderx), int(rshouldery)), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 205, 50), 3)
                
                #cv2.circle(frame, (int(relbowx), int(relbowy)), 10, (0, 0, 255), -1)

        _, frame = cv2.imencode('.jpg', frame)
        return frame.tobytes()
    
    def clear(self):
        self.arml = 0
        self.shoulderl = 0
        self.height = 0