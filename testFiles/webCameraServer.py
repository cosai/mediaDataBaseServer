from flask import Flask, Response
import cv2
import threading
from imutils.video import VideoStream
import time
import imutils
import os


exiting = False
outputFrame = None
lock = threading.Lock()
# initialize a flask object
app = Flask(__name__)
vs = VideoStream(src=0).start()
# videocam = cv2.VideoCapture(0)
time.sleep(2.0)
WEBPORT = 7776
IMAGEWIDTH=640
IMAGEHEIGHT=640

# this class is to create a web cam server using flask.
# NOTE that this code is a candidate for production use.
# you can go to localhost:PORT/video_feed to see the video stream
# you can go to localhost:PORT/exit to exit the server

@app.route("/exit")
def exit_app():
    global exiting
    exiting = True
    t.join()
    return "Done"


@app.route('/')
def index():
    line1 = "<p>go to <a href=\"http://localhost:" + str(WEBPORT) + "/video_feed\">Here</a> to see the camera feed.</p>"
    line2 = "<p>go to <a href=\"http://localhost:" + str(WEBPORT) + "/exit\">Here</a> to exit</p>"
    return line1 + line2


#this is  opencv alternative of the generate function
# when no threading is used
def gen():
    while False:
         success, image = videocam.read()
         ret, jpeg = cv2.imencode('.jpg', image)

         frame = jpeg.tobytes()
         yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


def get_frame():
    # grab global references to the video stream, output frame, and
    # lock variables
    global vs, outputFrame
    # initialize the motion detector and the total number of frames
    # read thus far
    total = 0
    # loop over frames from the video stream
    while not exiting:
        # read the next frame from the video stream, resize it,
        # convert the frame to grayscale, and blur it
        frame = vs.read()
        if frame is not None:
            frame = imutils.resize(frame, width=IMAGEWIDTH, height=IMAGEHEIGHT)
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            outputFrame = frame.copy()


def generate():
    # grab global references to the output frame and lock variables
    global outputFrame
    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if outputFrame is None:
                continue
            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
            # ensure the frame was successfully encoded
            if not flag:
                continue
        # yield the output frame in the byte format
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')


@app.teardown_request
def teardown(exception):
    global t
    if exiting:
        os._exit(0)


if __name__ == '__main__':
    global t
    from waitress import serve
    t = threading.Thread(target=get_frame, args=())
    t.daemon = True
    t.start()
    serve(app, host="0.0.0.0", port=WEBPORT)
