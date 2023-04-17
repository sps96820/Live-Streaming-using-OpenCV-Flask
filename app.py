from flask import Flask, render_template, Response, request
import cv2
import threading
from connector import connector
from camClass import camClass
app = Flask(__name__)

#camera = cv2.VideoCapture(0)  # use 0 for web camera
#  for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera
# for local webcam use cv2.VideoCapture(0)
camera = camClass()
####################################################################

def gen_frames(camera):  # generate frame by frame from camera
    #im = threading.Thread(target = camera.imaging, args=())
    #im.start()

    while True:
        # Capture frame-by-frame
        frame = camera.update_frame()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@app.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(camera), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/run-script', methods=['POST'])
def run_script():
    camera.clear()
    camera.imaging()
    return '', 204


@app.route('/', methods=['POST', 'GET'])
def index():
    """Video streaming home page."""
    #if request.method =="POST":
     #   camera.imaging()
     #   print("imaging started")
     #   #im = threading.Thread(target = camera.imaging, args=())
        #im.start()
        
    return render_template('index.html')


if __name__ == '__main__':
    
    app.run(debug=True, threaded=True)