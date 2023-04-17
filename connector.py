import cv2

class connector:
    def __init__(self):
        self.image = None
        
    def setImage(self, image):
        self.image = image
        
    def getImage(self):
        return self.image