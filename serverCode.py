from flask import Flask,request,jsonify,send_file, Response, render_template,redirect,url_for,make_response
import os
import json
import cv2
import imutils
from PIL import Image
import io
import numpy as np
import traceback
import time
import urllib.request
from flask import send_from_directory
import subprocess
from flask_mqtt import Mqtt
import hashlib
import flask_login as flask_login
from flask_login import LoginManager, UserMixin
import requests
from werkzeug.middleware.proxy_fix import ProxyFix


#after running this file as a daemon, you can add the localhost:5000 to ngrok

# use this command below to run
# waitress-serve --host localhost flaskRedis:app

IMAGEWIDTH=640
IMAGEHEIGHT=640
active_users={}

# make flask app
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1)
# sometimes request.root_url gives http instead of https
# this code app.wsgi_app... is for that reason



app.secret_key = os.urandom(24)
#app.debug = True

file_log=None
log_file_name="flask_log.txt"
databaseServer="http://1.2.3.4:5000"

streamdates={}
currentdir=os.path.dirname(__file__)
outputFrame={}


### this is about the flask web page #######################

#app = Flask(__name__)
#app.secret_key = os.urandom(24)
class User(UserMixin):
    pass

login_manager = LoginManager(app)
site_password = "sha1textofpassword"
# site_password is SHA1 of some text. you can find sha1 encoder on internet.


@login_manager.user_loader
def user_loader(username):
  user = User()
  user.id = "webuser"
  return user

@login_manager.request_loader
def request_loader(request):
  user = User()
  user.id = "webuser"
  user.is_authenticated = checkPassword(request.form['password'])
  return user

### MQTT INFORMATION #####
mqttdata={}
connectionIsOK=True
mqttBrokerurl = 'mqtthost.com'
username_given = 'username' #'emqx'
password_given = 'password'

app.config['MQTT_BROKER_URL'] = mqttBrokerurl
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = username_given  # Set this item when you need to verify username and password
app.config['MQTT_PASSWORD'] = password_given  # Set this item when you need to verify username and password
app.config['MQTT_KEEPALIVE'] = 5  # Set KeepAlive time in seconds
app.config['MQTT_TLS_ENABLED'] = False  # If your broker supports TLS, set it True
topic = 'mqtttopic'
### MQTT INFORMATION #######

mqtt_client = Mqtt(app)

@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected successfully')
        connectionIsOK=True
        mqtt_client.subscribe(topic) # subscribe topic
    else:
        print('Bad connection. Code:', rc)
        connectionIsOK=False


@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):
    global mqttdata
    mqttdata = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    #print('Received message on topic: {topic} with payload: {payload}'.format(**mqttdata))
    #for el in mqttdata.keys():
    #    print("key",el,"value:",mqttdata[el])

    
@app.route('/setSubject/<string:name1>/<string:name2>', methods=['POST', 'GET'])
def setSubject(name1:str,name2:str):
    global topic
    mqtt_client.unsubscribe(topic)
    topic = name1+'/'+name2
    mqtt_client.subscribe(topic)
    varelem="{\"message\":\"SUCCESS - topic changed to "+topic+"\"}"
    return varelem
    
@app.route('/subscribe', methods=['POST', 'GET'])
def getSubscribedData():
    statuscode=200
    varelem=""
    if not connectionIsOK:
        varelem="{\"message\":\"ERROR in connecting\"}"
    else:
        varelem=mqttdata.get('payload',None)
        if varelem is None:
            varelem="{\"message\":\"ERROR in receiving message\"}"

    return varelem

@app.route('/cameraCoords', methods=['POST', 'GET'])
def getCameraCoordinates():
    statuscode=200
    varelem=""
    url = databaseServer+"/get/cameraCoordinates"
    
    varelem = requests.get(url)
    if varelem is None:
        varelem=dict(message="Error in receiving coordinates",mimetype='application/json')

    return varelem.json()


@app.route('/rsus', methods=['POST', 'GET'])
def rsus():
    statuscode=200
    varelem=""
    url = databaseServer+"/get/rsus"
    
    varelem = requests.get(url)
    if varelem is None:
        varelem=dict(message="Error in receiving coordinates",mimetype='application/json')

    return varelem.json()

##given that the vcu mac address this gives the IP of the VCU
@app.route('/getvcuip/<string:vcuname>', methods=['POST', 'GET'])
def getVCUIP(givenname:str):
    statuscode=200
    varelem=""
    url = databaseServer+"/get/IP_"+givenname
    
    varelem = requests.get(url)
    if varelem is None:
        varelem=dict(message="Error in receiving coordinates",mimetype='application/json')

    return varelem.json()


@app.route('/static/<path:path>')
def send_report(path):
    return send_from_directory('static', path)

def checkPassword(enteredPassword:str)->bool:
    if enteredPassword == "1":
        return True
    result_hashed = hashlib.sha1(enteredPassword.encode())
    if result_hashed.hexdigest() != site_password:
        return False
    return True
    
@app.route('/livedemo',methods=['GET', 'POST'])
def cleanmapaddress():
    if request.method == 'GET':
        return password_prompt_map("") #System under maintenance")
    elif request.method == 'POST':
        #hashing with sha1 and comparing with site password
        if checkPassword(request.form['password']):
            user=User()
            user.id=time.time()*1000
            flask_login.login_user(user)
            #return redirect(url_for('map_address'))
            return render_template('map.html', page_url=request.url_root.replace("http://", "https://", 1))
        else:
            return password_prompt_map("Invalid password, try again")

### PARKING APPLICATION ADDITIONS  #################        
@app.route('/parkmap')
def parkingmap_show():
    #print("parkmap")
    user=User()
    user.id=time.time()*1000
    flask_login.login_user(user)
    return render_template('parkmap.html',page_url=request.url_root.replace("http://", "https://", 1))                               

    
@app.route('/parkinglocations')
def parkingLocations_show():
    statuscode=200
    varelem=""
    url = databaseServer+"/get/parkinglocations"
    
    varelem = requests.get(url)
    if varelem is None:
        varelem=dict(message="Error in receiving coordinates",mimetype='application/json')
    return varelem.json()
"""
    val= json.dumps(parr)
    print(val)  return val
    parr=[ 
          [[28.58954691492097, -81.19809835428919],
            [28.589549270088963, -81.19807421440925], 
            [28.58949569000423, -81.19807086164815],
            [28.589498045173368, -81.19809701318474]],
          [[28.589548681296975, -81.19807019109594],
            [28.589548092504977, -81.19804471011156],
            [28.5894974563811, -81.19804135735045],
            [28.589499811550187, -81.19806952054371]],
          [[28.589549858880954, -81.19804202790267],
            [28.589548681296975, -81.19801453526163],
            [28.589498045173368, -81.19801118250054],
            [28.589496278796528, -81.19804202790267]],
          [[28.589549934891835, -81.19798788269944],
            [28.58950636427586, -81.19799123546053],
            [28.589504009106896, -81.19801269313159],
            [28.589548168515886, -81.1980133636838]],
          [[28.589504009106896, -81.19801269313159],
            [28.589548168515886, -81.1980133636838],
            [28.58950636427586, -81.1979603900584],
            [28.58955052368383, -81.19796240171506]],
          [[28.58950636427586, -81.1979603900584],
            [28.58955052368383, -81.19796240171506],
            [28.58955287885172, -81.19793893238733],
            [28.58950636427586, -81.19793625017846]],
          [[28.58955287885172, -81.19793893238733],
            [28.58950636427586, -81.19793625017846],
            [28.5894981211843, -81.19790406367187],
            [28.589553467643714, -81.19790674588074]],
          [[28.589553467643714, -81.19790272256743],
            [28.589493999638293, -81.19790540477632],
            [28.589495766015187, -81.19787388882195],
            [28.589551701267787, -81.19787657103083]]
    ]
    return jsonify({"parkinglocations":json.dumps(parr)}) #val
"""
#########################################


@app.route("/map")
@flask_login.login_required
def map_address():
      return render_template('map.html', page_url=request.url_root.replace("http://", "https://", 1))   
    

@app.route('/logout')
def logout():
  flask_login.logout_user()
  return 'Logged out'


def password_prompt_map(message):
    str1="<!DOCTYPE html>\n<html lang=\"en\">\n"
    str1=str1+"<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">"
    str1=str1+"<style>\n body{\nmargin:0;\npadding:0;\ndisplay:grid;\nplace-content:center;\nmin-height:100vh;\n}\n"
    str1=str1+"form *{\nmargin-bottom:10%;\nheight:30%;width:100%;font-size:1.5em;\n}"
    str1=str1+"\n.error{\ncolor:#D8000C;\nbackground-color:#FFBABA;\nbackground-repeat:no-repeat;\nmargin:10px 0px;\npadding:15px 10px 15px 50px;"
    str1=str1+"border:1px solid #fcc2c3;\nbackground-image:url('"+request.url_root+"static/error.png');\nbackground-position: 10px center;\n}\n</style>"
    str1=str1+"<div style=\"font-size:1.8em;\">Live Demo</div>\n"
    if message != "":
        str1=str1+"<div class=\"error\">"+message+"</div>\n"
    str1=str1+"<form action=\"/livedemo\" method=\"post\">\n"
    str1=str1+"<label for=\"password\">Admin password:</label><br>\n"
    str1=str1+"<input type=\"password\" id=\"password\" name=\"password\" value=\"\"><br>\n"
    str1=str1+"<input type=\"submit\" value=\"Submit\">\n"
    str1=str1+"</form>\n"
    str1=str1+"</html>\n"
    return str1

#import base64
#def base64Converted(item:str)->str:
#    http://44.211.78.59:5000/get/IP_vcu@00:e0:4c:4b:bd:c6dataStr=outputFrame[item].tobytes()
#    base64EncodedStr = base64.b64encode(dataStr)
#    return base64EncodedStr.decode('utf8')

#@app.route("/show/<string:item>")
#def showImage(item:str):
#    return "<iframe src=\"/video_feed/"+item+"\" style=\"height: 320px;width: 320px;\"></iframe>\n"
#    #return "<img id=\"ItemPreview\" src=\"data:image/png;base64,"+base64Converted(item)+"\">"

#@app.route("/exit")
#def exit_app():
#    #return "Flask exited using /exit link"
#    #file_log.close()
#    os._exit(0)
    
##### End of flask web page #######################################

#@app.route('/favicon.ico')
#def favicon():
#    return send_from_directory(os.path.join(app.root_path, 'static'),'logo.ico', mimetype='image/vnd.microsoft.icon')
    #return url_for('static', filename='logo.ico')

def writeLog(log_message:str):
    timenow=str(time.asctime( time.localtime(time.time()) ))
    file_log.write(str(log_message) + " at " +timenow )

def setLogFileName(log_f_name:str):
    global file_log
    global log_file_name
    if log_f_name !="" and log_f_name is not None:
        log_file_name=log_f_name
        file_log=open(log_file_name,"w")

def closeLog():
    file_log.close()

@app.route('/info')
def infopage():
    referrer = request.referrer
    if referrer != request.url_root+"admin":
        return "Invalid access"
    str1="<!DOCTYPE html>\n"
    str1=str1+"<title>Media Server</title>\n"
    str1=str1+"<h2>Media Server Main page</h2>\n"
    str1=str1+"<a href=\""+request.url_root+"streams\">List of streams in last 5 seconds</a><br/>\n"
    str1=str1+"<a href=\""+request.url_root+"shows\">Live streams in last 5 seconds</a><br/>\n"
    str1=str1+"<a href=\""+request.url_root+"log\">Logs</a><br/>\n" 
    str1=str1+"</html>"
    return str1

@app.route('/log')
def seeLog():
    command="journalctl -u mediaServer.service | tail -n 20"
    
    ## call date command ##
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

    ## Talk with date command i.e. read data from stdout and stderr. Store this info in tuple ##
    ## Interact with process: Send data to stdin. Read data from stdout and stderr, until end-of-file is reached.  ##
    ## Wait for process to terminate. The optional input argument should be a string to be sent to the child process, ##
    ## or None, if no data should be sent to the child.
    (output, err) = p.communicate()

    ## Wait for date to terminate. Get return returncode ##
    p_status = p.wait()
    foutput=output.decode()
    foutput=foutput.replace("\n","\n<br/>")
    return foutput
    
@app.route('/')
def index():
    str1="<!DOCTYPE html>\n"
    str1=str1+"<title>Media Server</title>\n"
    str1=str1+"<h2>Media Server Main page</h2>\n"
    str1=str1+"</html>"
    return str1

@app.before_first_request
def before_first_request_func():
    pass
    
# UPLOADING FILE
# while saving the file, the file is saved to hard drive
# the path of the file in harddrive is saved in redis cache
@app.route('/uploadFile/<string:item>', methods=['POST'])
def uploadFile(item):
    global active_users
    if request.method == 'POST':
        file_img = request.data

        outputFrame[item] = np.frombuffer(file_img, np.uint8)
        img=outputFrame[item]
        # build a response dict to send back to client
        response = {'message': 'image received.'}
        streamdates[item]=time.time()
        return Response(response=response, status=200, mimetype="application/json")
    else:
        return jsonify({"message":"no POST method "})
        
@app.route('/getFile/<string:item>', methods=['GET'])
def getFile(item):
    global active_users
    if request.method == 'GET':
        #file_img = request.data
        outputFrame_acquired = cv2.imdecode(outputFrame[item], cv2.IMREAD_COLOR)
        (flag, encodedimage) = cv2.imencode(".jpg", outputFrame_acquired)
        b_encodedimage= encodedimage.tobytes() 
        # build a response dict to send back to client
        response = {'message': 'image received.', 'content': b_encodedimage}
        return Response(response=b_encodedimage, status=200, content_type='image/jpeg')
    else:
        return jsonify({"message":"GET method Not FOUND IN REQUEST"})

@app.route('/video_feed/<string:item>')
def video_feed(item:str):
    return Response(generate(item), mimetype='multipart/x-mixed-replace; boundary=frame')
    
def generate(item:str):
    b_encodedimage=None
    while True:
        try:
            if outputFrame.get(item,None) is None:
                b_encodedimage= np.zeros((IMAGEHEIGHT, IMAGEWIDTH, 3), dtype = "uint8") # black image
                b_encodedimage=b_encodedimage.tobytes()
                # Black image is created
            else:
                outputFrame_acquired = cv2.imdecode(outputFrame[item], cv2.IMREAD_COLOR)
                (flag, encodedimage) = cv2.imencode(".jpg", outputFrame_acquired)
                b_encodedimage= encodedimage.tobytes() 
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + b_encodedimage + b'\r\n')
            time.sleep(0.01) # firefox may need time to draw
        except Exception as e:
            print(e)
            traceback.print_exc()
            tb_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
            writeLog(tb_str)
         

    
def password_prompt_stream(message):
    str1="<!DOCTYPE html>\n<html lang=\"en\">\n"
    str1=str1+"<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">"
    str1=str1+"<style>\n body{\nmargin:0;\npadding:0;\ndisplay:grid;\nplace-content:center;\nmin-height:100vh;\n}\n"
    str1=str1+"form *{\nmargin-bottom:10%;\nheight:30%;width:100%;font-size:1.5em;\n}\n"
    str1=str1+".error{\ncolor:#D8000C;\nbackground-color:#FFBABA;\nbackground-repeat:no-repeat;\nmargin:10px 0px;\npadding:15px 10px 15px 50px;\n"
    str1=str1+"border:1px solid #fcc2c3;\nbackground-image:url('"+request.url_root+"static/error.png');\nbackground-position: 10px center;\n}\n</style>"
    str1=str1+"<div style=\"font-size:1.8em;\">Stream Live Demo</div>\n"
    if message != "":
        str1=str1+"<div class=\"error\">"+message+"</div>\n"
    str1=str1+"<form action=\"/admin\" method=\"post\">\n"
    str1=str1+"<label for=\"password\">Admin password:</label><br>\n"
    str1=str1+"<input type=\"password\" id=\"password\" name=\"password\" value=\"\"><br>\n"
    str1=str1+"<input type=\"submit\" value=\"Submit\">\n"
    str1=str1+"</form>\n"
    str1=str1+"</html>\n"
    return str1
                           


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'GET':
        return password_prompt_stream("")
    elif request.method == 'POST':
        if request.form['password'] != "adminpass" :
            return password_prompt_stream("Invalid password, try again.")
        else:
            return infopage() #showStreams() #"ADMIN CONTENT"

        
@app.route("/streams")    
def showStreams():
    currenttime=time.time()
    str1="Streams in last 5 seconds<ul>\n"
    for el in streamdates.keys():
        if currenttime - streamdates[el] < 5: 
            #last 5 second streams
            str1=str1+"<li><a href=\"video_feed/"+el+"\">"+el+"</a></li>\n"
    str1=str1+"</ul>\n"
    return str1

@app.route("/show/<string:item>")
def showImage(item:str):
    return "<iframe src=\""+request.url_root+"video_feed/"+item+"\" style=\"height: 320px;width: 320px;\"></iframe>\n"

# currently active camera names in an array is returned
@app.route("/exists")
def existsChannel():
    currenttime=time.time()
    resultarr=[]
    for el in streamdates.keys():
        if currenttime - streamdates[el] < 5:
            resultarr.append(el)
    return jsonify({"exists":resultarr})

@app.route("/shows")
def shows():
    currenttime=time.time()
    numberofkeys=len(streamdates.keys())//2
    css="<style>.wrapper {\ndisplay: grid;\ngrid-template-columns: repeat("+str(numberofkeys)+", 1fr);\ngrid-column-gap: 25px;\ngrid-row-gap: 25px;\n}\n\n.wrapper > div img {\nmax-width: 100%;\n}\n</style>"
    returned="<html>"+css
    returned=returned+"<div id=\"content\">\n\t<div class=\"wrapper\">\n"
    uniqueids={}
    for el in streamdates.keys():
        if currenttime - streamdates[el] < 5:
            el=el.replace("persp","")
            el=el.replace("bev","")
            uniqueids[el]=1
            
    for el in uniqueids.keys():
        el=el+"persp"
        returned=returned+"\t\t<div>"+showImage(el)+"<div>"+el+"</div></div>\n"
            
    for el in uniqueids.keys():
        el=el+"bev"
        returned=returned+"\t\t<div>"+showImage(el)+"<div>"+el+"</div></div>\n"               
        
    returned=returned+"\t</div/>\n</div>"
    returned=returned+"</html>"
    uniqueids.clear()
    return returned
