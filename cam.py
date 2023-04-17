import sys
from pip import main
import tkinter as tk
import time
import cv2
from PIL import Image, ImageTk
import threading
import mpmeasure as mpm
from calibrationClass import calibration as cal
from arucoClass import scaleAq as aru
import numpy as np
import mediapipe as mp
from queue import Queue
import connector


# Define a function to update the webcam output
def update_frame(q, heightq, armq, shoulderq, instructionq, connect):
    global label
    calibBool = False
    while True:
        _, frame = cap.read()
        image_height, image_width, _ = frame.shape

        #if len(imagearr) != 30:
            #imagearr.append(frame)
        
        #with mp_pose.Pose(
        #       min_detection_confidence=0.5,
        #      min_tracking_confidence=0.5) as pose:
        if not q.empty():
            #print("queue triggered")
            calibBool = q.get()
            print(calibBool)

        results = pose.process(frame)
        mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
        
        if results.pose_landmarks != None:
            rshoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            lshoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
            rwrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
            relbow = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW]
            relbowx = relbow.x * image_width
            relbowy = relbow.y * image_height
            nose = results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]
            nosex = nose.x * image_width
            nosey = nose.y * image_height
            rshoulderx = rshoulder.x * image_width
            rshouldery = rshoulder.y * image_height
            chestx = ((rshoulder.x * image_width) + (lshoulder.x * image_width)) / 2
            chesty = ((rshoulder.y * image_height) + (lshoulder.y * image_height)) / 2
            
            if not instructionq.empty():
                instruction = instructionq.get()
            if not heightq.empty():
                height = heightq.get()
            if not armq.empty():
                arml = armq.get()
            if not shoulderq.empty():
                shoulderl = shoulderq.get()
            
            if instruction == "Paper Up":
                cv2.putText(frame, "Hold Aruco Marker up against chest", (int(image_width*.02), int(image_height*.85)), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 205, 50), 3)
            elif instruction == "Papers Down":
                cv2.putText(frame, "Put papers down", (int(image_width*.05), int(image_height*.85)), cv2.FONT_HERSHEY_COMPLEX, 1.05, (50, 205, 50), 3)
            elif instruction == "be still":
                cv2.putText(frame, "Stand still and hold arms to side", (int(image_width*.02), int(image_height*.85)), cv2.FONT_HERSHEY_COMPLEX, 1.05, (50, 205, 50), 3)
            elif instruction == "start":
                cv2.putText(frame, "Ensure full body is in frame", (int(image_width*.05), int(image_height*.85)), cv2.FONT_HERSHEY_COMPLEX, 1.05, (50, 205, 50), 3)
            elif instruction == "wait":
                cv2.putText(frame, "Calculating...", (int(image_width*.05), int(image_height*.85)), cv2.FONT_HERSHEY_COMPLEX, 1.05, (50, 205, 50), 3)
            elif instruction == "end":
                 cv2.putText(frame, "Measurements are shown above!", (int(image_width*.05), int(image_height*.85)), cv2.FONT_HERSHEY_COMPLEX, 1.05, (50, 205, 50), 3)
               
            
            if arml != 0:
                cv2.putText(frame, "Arm Length: {}".format(round(arml,1)), (int(relbowx), int(relbowy)), cv2.FONT_HERSHEY_COMPLEX, 1.05, (50, 205, 50), 3)
            if height != 0:
                cv2.putText(frame, "Height: {}".format(round(height, 1)), (int(nosex), int(nosey) - 40), cv2.FONT_HERSHEY_COMPLEX, 1.1, (50, 205, 50), 3)
            if shoulderl != 0:
                cv2.putText(frame, "Shoulder Width: {}".format(round(shoulderl, 1)), (int(rshoulderx), int(rshouldery)), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 205, 50), 3)
            
            #cv2.circle(frame, (int(relbowx), int(relbowy)), 10, (0, 0, 255), -1)

        sca.scale(frame)
        if sca.bboxs:
            sca.scale(frame)
            int_corners = np.int0(sca.bboxs)
            cv2.polylines(frame, int_corners, True, (0, 255, 0), 2)
        #if calibBool:
        #print("calib")
            #calibFrameUpdate.singleImage(frame)
            #if calibFrameUpdate.threedpoints:
                #frame = cv2.drawChessboardCorners(frame, calibFrameUpdate.CHECKERBOARD, calibFrameUpdate.corners2, calibFrameUpdate.ret)
        
        connect.setImage(frame)
        #cv2.imshow("image", frame)
        key = cv2.waitKey(1)
        if key == 27:
            cv2.destroyAllWindows()
            return
        if not im.is_alive:
            cv2.destroyAllWindows()
        
            #update_frame(imagearr)

# Function for main
def main(connect):
    time.sleep(4)
    global cap
    global sca
    global pose
    global mp_pose
    global mp_drawing
    global mp_drawing_styles
    global frame
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    pose = mp_pose.Pose(model_complexity=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)

    sca = aru()
    global calib
    calib = cal()

    global calibBool
    calibBool = False
    
    global calibFrameUpdate
    heightq = Queue()
    heightq.put(0)
    
    armq = Queue()
    armq.put(0)
    
    shoulderq = Queue()
    shoulderq.put(0)
    
    instructionq = Queue()
    instructionq.put("None")
    
    q = Queue()
    q.put(False)
    calibFrameUpdate = cal()
    sys.setrecursionlimit(9999)
    imagearr = []
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1024)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 768)
    global im 
    im = threading.Thread(target = imaging, args=(q, heightq, armq, shoulderq, instructionq))
    im.start()
    update_frame(q, heightq, armq, shoulderq, instructionq, connect)

def imaging(q, heightq, armq, shoulderq, instructionq):
    instructionq.put("start")
    time.sleep(10)
    # Undistort images
    #calib = cal()
    imagearr = []
    for i in range(30):
        _, tempCap = cap.read() 
        imagearr.append(tempCap)
    #q.put(True)
    #temp = calib.getMatrix(imagearr)
    #while temp == False:
        #print("Checkerboard not found. Hold it up", flush=True)
        #for i in range(30):
            #_, tempImage = cap.read() 
            #imagearr[i] = tempImage
            #time.sleep(2)
           # temp = calib.getMatrix(imagearr)
          #  q.put(True)
        
    
    q.put(False)
    print("Put checkerboard down and hold aruco marker", flush=True)
    instructionq.put("Paper Up")
    time.sleep(2)
    corrected = []
    for i in range(30):
        _, tempCap = cap.read() 
        corrected.append(tempCap)
        #corrected.append(calib.undistortImage(tempCap))
    ##for img in imagearr:
        #corrected.append(calib.undistortImage(img))

    print("before scale", flush=True)
    ratio = scale(corrected)
    print("ratio",flush=True)
    print(ratio,flush=True)
    # Get scale and measurements
    while ratio < 4:
        arucoArray = []
        print("Make sure aruco marker is visible", flush=True)
        time.sleep(2)
        for i in range(30):
            _, tempCap = cap.read() 
            arucoArray.append(tempCap)
            #arucoArray.append(calib.undistortImage(tempCap))
            
        ratio = scale(arucoArray)
        print("length", len(arucoArray), flush=True)
        print("ratio",flush=True)
        print(ratio,flush=True)
    
    CAM_CONTROL = True
    
    mediapipeImgs = []
    
    print("Put papers down", flush=True)
    instructionq.put("Papers Down")
    time.sleep(3)
    instructionq.put("be still")
    time.sleep(2)
    for i in range(30):
        _, tempCap = cap.read() 
        mediapipeImgs.append(tempCap)
        #mediapipeImgs.append(calib.undistortImage(tempCap))
        #mediapipeImgs[i] = calib.undistortImage(mediapipeImgs[i])
    instructionq.put("wait")
    measurelist = [[] for i in range(3)]
    #for image in corrected:
    for image in mediapipeImgs:
        temparray = mpm.media(image)
        print(tempCap, flush=True)
        measurelist[0].append(temparray[0])
        measurelist[1].append(temparray[1])
        measurelist[2].append(temparray[2])
    avglist = measureavg(measurelist, ratio)
    # Print final values
    print("Height: ", avglist[0], "\nShoulder: ", avglist[1], "\nArms: ", avglist[2], flush=True)
    instructionq.put("end")
    heightq.put(avglist[0])
    shoulderq.put(avglist[1])
    armq.put(avglist[2])

    
    
    
def scale(corrected):
    #sca = aru()
    ratio = []
    # Get the scales for each image
    for img in corrected:
        print("in for", flush = True)
        if sca.scale(img):
            #print(sca.scale(img), flush=True)
            ratio.append(sca.ratio)
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

def measureavg(measurelist, ratio):
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

if __name__ == "__main__":
    main()