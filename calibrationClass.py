import cv2
import numpy as np
import os
from time import sleep
from numpy import savetxt
from numpy import genfromtxt


class calibration:
    def __init__(self):
        self.CHECKERBOARD = (7 ,4)
        self.MIN_POINTS = 50
        self.RECORD = True   

        self.ret = None
        self.corners=None
        self.corners2= None
        self.matrix = None
        self.distortion = None
        self.r_vecs = None
        self.t_vecs = None
        self.newcameramatrix = None
        self.roi = None
        self.outputImage = None

        # stop the iteration when specified
        # accuracy, epsilon, is reached or
        # specified number of iterations are completed.
        self.criteria = (cv2.TERM_CRITERIA_EPS +
                    cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        self.threedpoints = []

	    # Vector for 2D points
        self.twodpoints = []


	    # 3D points real world coordinates
        self.objectp3d = np.zeros((1, self.CHECKERBOARD[0]
						* self.CHECKERBOARD[1],
						3), np.float32)
        self.objectp3d[0, :, :2] = np.mgrid[0:self.CHECKERBOARD[0],
								0:self.CHECKERBOARD[1]].T.reshape(-1, 2)
        self.prev_img_shape = None


    def singleImage(self, image):
        self.reset()
        grayColor = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.ret, self.corners = cv2.findChessboardCorners(
                            grayColor, self.CHECKERBOARD,
                            cv2.CALIB_CB_ADAPTIVE_THRESH
                            + cv2.CALIB_CB_FAST_CHECK +
                            cv2.CALIB_CB_NORMALIZE_IMAGE)
        if self.ret == True:
            self.threedpoints.append(self.objectp3d)
            self.corners2 = cv2.cornerSubPix(
                    grayColor, self.corners, (11, 11), (-1, -1), self.criteria)

            self.twodpoints.append(self.corners2)
        

    def getMatrix(self, images):
        for filename in images:
            image = filename
            grayColor = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Find the chess board corners
            # If desired number of corners are
            # found in the image then ret = true
            self.ret, self.corners = cv2.findChessboardCorners(
                            grayColor, self.CHECKERBOARD,
                            cv2.CALIB_CB_ADAPTIVE_THRESH
                            + cv2.CALIB_CB_FAST_CHECK +
                            cv2.CALIB_CB_NORMALIZE_IMAGE)

            # If desired number of corners can be detected then,
            # refine the pixel coordinates and display
            # them on the images of checker board
            if self.ret == True:
                self.threedpoints.append(self.objectp3d)

                # Refining pixel coordinates
                # for given 2d points.
                self.corners2 = cv2.cornerSubPix(
                    grayColor, self.corners, (11, 11), (-1, -1), self.criteria)

                self.twodpoints.append(self.corners2)

                # Draw and display the corners
                #image = cv2.drawChessboardCorners(image,
                                                #self.CHECKERBOARD,
                                                #self.corners2, self.ret)
                #cv2.imshow('temp', image)
                #cv2.waitKey(1)
        # Perform camera calibration by
        # passing the value of above found out 3D points (threedpoints)
        # and its corresponding pixel coordinates of the
        # detected corners (twodpoints)
        print(len(self.threedpoints), flush=True)
        if len(self.threedpoints) > 5:
            self.ret, self.matrix, self.distortion, self.r_vecs, self.t_vecs = cv2.calibrateCamera(
                self.threedpoints, self.twodpoints, grayColor.shape[::-1], None, None)
            print("matrix aquired", flush=True)
            self.getNewCameraMatrix(images[0])
            return True
        else:
            #print("checkerboard not found", flush=True)
            return False
        
    def getNewCameraMatrix(self, image):
        h, w = image.shape[:2]
        self.newcameramatrix, self.roi = cv2.getOptimalNewCameraMatrix(self.matrix, self.distortion, (w,h), 1, (w,h))
        print("new camera matrix aqured")
        return
        
            
    
    def undistortImage(self, image):
        img = image
        #h, w = img.shape[:2]
        #self.newcameramatrix, self.roi = cv2.getOptimalNewCameraMatrix(self.matrix, self.distortion, (w,h), 1, (w,h))
        outputImage = cv2.undistort(img, self.matrix, self.distortion, None, self.newcameramatrix)
        #mapx, mapy = cv2.initUndistortRectifyMap(self.matrix, self.distortion, None, self.newcameramatrix, (w,h), 5)
        #self.outputImage = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)
        x, y, w, h = self.roi
        outputImage = outputImage[y:y+h, x:x+w]
        #print("image undistorted")
        return outputImage
    
    def reset(self):
        self.ret = None
        self.corners=None
        self.corners2= None
        self.matrix = None
        self.distortion = None
        self.r_vecs = None
        self.t_vecs = None
        self.newcameramatrix = None
        self.roi = None
        self.outputImage = None

        # stop the iteration when specified
        # accuracy, epsilon, is reached or
        # specified number of iterations are completed.
        self.criteria = (cv2.TERM_CRITERIA_EPS +
                    cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        self.threedpoints = []

	    # Vector for 2D points
        self.twodpoints = []


	    # 3D points real world coordinates
        self.objectp3d = np.zeros((1, self.CHECKERBOARD[0]
						* self.CHECKERBOARD[1],
						3), np.float32)
        self.objectp3d[0, :, :2] = np.mgrid[0:self.CHECKERBOARD[0],
								0:self.CHECKERBOARD[1]].T.reshape(-1, 2)
        self.prev_img_shape = None