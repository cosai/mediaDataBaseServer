from flask import Flask, Response
import cv2
import threading
from imutils.video import VideoStream
import time
import imutils
import os
import requests
import json

### This code reads the camera feed and sends it to the media server 
### The media server we are stating here is the media server in this repository.
###

exiting = False

vid = cv2.VideoCapture(0)

time.sleep(2.0)
WEBPORT = 5000
itemid="phototest"
websitename="http://192.168.0.154:"+str(WEBPORT)


r_session = requests.Session()

# returns tuple
# if successful tuple will be 200,"OK"
# if not the the first element will be the error code, The second element is reason of the error
def post_image(img):
    test_url = websitename+'/uploadFile/'+itemid

    # prepare headers for http request
    content_type = 'image/jpeg'
    headers = {'content-type': content_type}

    _, img_encoded = cv2.imencode('.jpg', img)
    # we are encoding as jpeg file
    response = r_session.post(test_url, data=img_encoded.tobytes(), headers=headers)
    scode=response.status_code
    reason="OK"
    if scode != 200:
        reason=response.reason
    response.close()
    return scode,reason

#this function can be used a target of a thread
def send_frame():
    while not exiting:
        # read the next frame from the video stream, resize it,
        ret, frame = vid.read()
        if frame is not None:
            
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cv2.imshow(itemid,frame) # we are showing the frame to the user on screen.
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            message_status_code, reason = post_image(frame)
            if message_status_code !=200:
                print(reason)
            
    # Destroy all the windows
    vid.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    send_frame()
