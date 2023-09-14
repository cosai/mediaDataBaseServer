import redis
from flask import Flask,request,jsonify,send_file, Response
import base64
import os
import json
from itertools import zip_longest
import cv2
import imutils
from PIL import Image
import io
import numpy as np
import traceback
import time
import urllib.request
from flask_mqtt import Mqtt

# sudo apt-get install redis-server
# sudo service redis start
# Redis a caching system with no sql database. Fast and easy to install/Use. Even SQL database can be installed at the back also
#after running this file as a daemon, you can add the localhost:5000 to ngrok
# The database server runs with waitress as default and the port is on 5000. No need to use nginx if you dont want to run DB on port 60
# use this command below to run
# waitress-serve --host localhost flaskRedis:app

# make redis
redis_cache = None

# serverconfig file should have a DBPASSWORD entry if the database is password protected

# make flask app
app = Flask(__name__)
#app.debug = True
configfname="serverconfig.txt"
configs={}

file_log=None
log_file_name="flask_log.txt"

currentdir=os.path.dirname(__file__)
backupfile="/home/ubuntu/redisbackup.dat"
    
outputFrame={}

def writeLog(log_message:str):
    timenow=str(time.asctime( time.localtime(time.time()) ))
    file_log.write(str(log_message) + " at " +timenow )
    
def readConfig():
    f=open(configfname,"r")
    all=f.readlines()
    for el in all:
        el=el.strip()
        arr=el.split(":")
        configs[arr[0]]=arr[1]
    f.close()
    
@app.route('/')
def index():
    str1=" <!DOCTYPE html>\n"
    str1=str1+"<title>Database Server</title>\n"
    str1=str1+"<h2>Database Server Main page</h2>\n"
    str1=str1+"</html>"
    return str1

#this page will be used in IP learning server.
# if you check ipsender repository, you will see that the code will be requesting its own IP from a server
# With this  function our database server will also serve as IP server.
@app.route('/learnip', methods=["GET"])
def learnip():
    return request.remote_addr
    #return jsonify({'ip': request.remote_addr}), 200
        
## RETRIEVING FILE
#the path of the file in redis cache is retrieved and encoded as base 64
# then shown on the browser page
@app.route('/getFileb64/<string:item>')
def getFileb64(item):
  value=None
  # if cache hit then get from redis
  if redis_cache.exists(item):
     value = redis_cache.get(item)
     value=value.decode('utf8')
     starting_pos=value.find(".")+1
     extension=value[starting_pos:]
     fullpath=os.path.join(currentdir,value)
     with open(fullpath, "rb") as image_file:
        data = base64.b64encode(image_file.read())
     value="<img src=\"data:image/"+extension+";base64,"+data.decode('utf8')+"\"/>"
  else:
     value = jsonify({"message":"Not in cache"})
  return value


## RETRIEVING FILE
#the path of the file in redis cache is retrieved
# then shown on the browser page
@app.route('/getFile/<string:item>')
def getFile(item):
  value=None
  # if cache hit then get from redis
  if redis_cache.exists(item):
     value = redis_cache.get(item)
     filename=value.decode('utf-8')
     starting_pos=filename.find(".")+1
     extension=value[starting_pos:].decode('utf-8')
     fullpath=os.path.join(currentdir,filename)
     return send_file(fullpath, mimetype='image/'+str(extension))
  else:
     value = jsonify({"message":"Not in cache"})
  return value


# UPLOADING FILE
# while saving the file, the file is saved to hard drive
# the path of the file in harddrive is saved in redis cache
@app.route('/uploadFile/<string:item>', methods=['POST'])
def uploadFile(item):
    global active_users
    if request.method == 'POST':
        if configs["STREAMING"]=="True": # this option saves the data in RAM, as avariable
            file_img = request.data
          
            outputFrame[item] = np.frombuffer(file_img, np.uint8)
            img=outputFrame[item]
            # build a response dict to send back to client
            response = {'message': 'image received.'}
            return Response(response=response, status=200, mimetype="application/json")
        else:
            f = request.files[item]
            filename=secure_filename(f.filename,item)
            redis_cache.set(item,filename)
            f.save(filename)
            return jsonify({"message":"file uploaded successfully"})
    else:
        return jsonify({"message":"no POST method "})


# iterate a list in batches of size n
# used in getkeys method
def batcher(iterable, n):
    args = [iter(iterable)] * n
    return zip_longest(*args)
    
def secure_filename(name,idf):
    return idf+"_"+name
    
#GET ALL THE KEYS
@app.route('/all/')
def getAllKeys():
    counter = 0
    dictItem={}
    ignorelist=["parkinglocations","rsus"]
    
    for key in redis_cache.keys():
        decodedkey=key.decode('utf8')
        if decodedkey not in ignorelist:
            val_key=redis_cache.get(key)
            try:
                dictItem[decodedkey]=val_key.decode('utf8')
            except UnicodeError:
                dictItem[decodedkey]="STREAM_CAMERA_IMAGE"
            counter += 1
    return jsonify(dictItem)
  
  
#GET ALL KEYS MATCHING the parameter, If empty parameter all of them will be returned
@app.route('/keys/<string:item>')
def getKeys(item:str):
    counter = 0
    dictItem={}
    
    if item=="":
        item="*"
        for key in redis_cache.keys():
          dictItem[key.decode('utf8')]=redis_cache.get(key).decode('utf8')
          counter += 1
    else:
      batch_counter = 0
      for keybatch in batcher(redis_cache.scan_iter(item), 12):
          batch_counter +=1
          for key in keybatch:
              if key != None:
                  counter += 1
                  dictItem[key.decode('utf8')]=redis_cache.get(key).decode('utf8')
                  # print("  ", counter, "key=" + key, " value=" + redisObj.get(key))
    return jsonify(dictItem)


#RETRIEVE
@app.route('/get/<string:item>')
def retrieveValue(item:str):
  # if cache hit then get from redis
  returnedValue=None
  if redis_cache.exists(item):
     value = redis_cache.get(item).decode('utf8')
     returnedValue = value #jsonify({item:value})  the values are stored as json already.
  else:
     returnedValue = jsonify({"message":"Not in cache"})
  return returnedValue  #"+item+":\""+value+"\"}" 

# SET VALUE
@app.route('/setElem/<string:item1>/<string:item2>', methods=['GET'])
def setElemValue(item1,item2):
  redis_cache.set(item1,item2)
  return jsonify({"message":"ADDED"})

# SET VALUE
@app.route('/set/<string:item>', methods=['POST'])
def setValue(item):
  if request.method == 'POST':
    content = request.data.decode('utf8')
    redis_cache.set(item,content)
    return jsonify({"message":"ADDED"})   
  else:
    return jsonify({"message":"NO DATA IN POST!"})

#RETRIEVE BATCH
@app.route('/getBatch/', methods=['POST'])
def retrieveBatchValues():
  if request.method == 'POST':
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        jtopy=request.get_json() #json.dumps(request.get_json()) 
        itemlist=json.loads(jtopy) 
        alldict={}
        for item in itemlist:
            value={}
            if redis_cache.exists(item):
                value = redis_cache.get(item).decode('utf8')
            alldict[item]=value
        return jsonify(alldict)  ## "{"+item+":\""+value+"\"}" 
    else:
        return jsonify({"message":"Content-Type not supported!"}) 
  else:
    return jsonify({"message":"NO DATA IN POST!"}) 

# SET VALUE BATCH
@app.route('/setBatch/', methods=['POST'])
def setBatchValues():
  if request.method == 'POST':
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        #dictarr = json.loads(json.loads(request.data))
        dictarr=json.loads(request.data)
        #if type(dictarr) is str:
        #    dictarr=json.loads(dictarr)
        for el in dictarr.keys(): #traversing list
            redis_cache.set( el,dictarr[el] )
        return jsonify({"message":"ALL BATCHES ADDED"})
    else:
        return jsonify({"message":"Content-Type not supported!"})
  else:
    return jsonify({"message":"NO DATA IN POST!"})

def is_image(filename:str):
  if ".png" in filename or ".webp" in filename or ".jpeg" in filename or ".jpg" in filename:
    return True
  return False

# DELETE 
@app.route('/delete/<string:item>')
def deleteValue(item:str):
  if redis_cache.exists(item):
    val= redis_cache.get(item).decode('utf8')
    if is_image(val):
      if os.path.exists(val):
         os.remove(val)
      else:
         redis_cache.delete(item)
         return jsonify({"message":"The file "+str(val)+" does not exist but entry is deleted"}) 
    redis_cache.delete(item)
    return jsonify({"message":"DELETED"}) 
  return jsonify({"message":"KEY DOES NOT EXIST"})

################################################
@app.before_first_request
def before_first_request_func():
    pass
    ##restore(backupfile)

#those methods are not used
@app.route('/backup/')
def backup():
    backupfile="/home/ubuntu/redisbackup.dat"
    out = {}
    # in batches of 500 delete keys matching:*
    for key in redis_cache.scan_iter(count=100):
        out[key.decode('utf8')]= redis_cache.get(key).decode('utf8')
    if len(out) > 0:
        try:
            with open(backupfile, 'w') as outfile:
                json.dump(out, outfile)
                writeLog("Backup successfull")
                return jsonify({"message":"BACKUP SUCCESSFUL!"})
        except Exception as e:
            tb_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
            writeLog(tb_str)
            return jsonify({"message":"Exception: !"+str(e)})
    else:
        return jsonify({"message":"NO KEYS IN BACKUP!"})

def backup2():
    backupfile="/home/ubuntu/redisbackup.dat"
    out = {}
    for key in redis_cache.scan_iter():
        out.update({key: redis.get(key)})
    if len(out) > 0:
        try:
            with open(backupfile, 'w') as outfile:
                json.dump(out, outfile)
                writeLog("Backup successfull")
                return jsonify({"message":"BACKUP SUCCESSFUL!"})
        except Exception as e:
            tb_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
            writeLog(tb_str)
            return jsonify({"message":"Exception: !"+str(e)})
    else:
        return jsonify({"message":"NO KEYS IN BACKUP!"})

#@app.route('/restore/')
def restore():
    try:
        with open(backupfile) as f:
            data = json.load(f)
            for key in data:
                r.set(key, data.get(key), cache_timeout)
            writeLog("Restore successfull")
            return jsonify({"message":"DATA RESTORED SUCCESSFULY"})
    except Exception as e:
        tb_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
        writeLog(tb_str)
        return jsonify({"message":"Exception: !"+str(e)})

"""
CHUNK_SIZE = 5000
@app.route('/destroyAllRecords')
def clear_ns(ns=""):
    cursor = '0'
    ns_keys = ns + '*'
    while cursor != 0:
        cursor, keys = redis_cache.scan(cursor=cursor, match=ns_keys, count=CHUNK_SIZE)
        if keys:
            redis_cache.delete(*keys)
    writeLog("All Entries deleted using /destroyAllRecords")
    return jsonify({"message":"ALL DELETED"})  
"""
################################################   

try:
    from waitress import serve
    from os.path import exists
    file_exists = exists(configfname)
    if not file_exists:
        print(configfname," does not exist")
        quit()
    readConfig()
    if configs.get("LOGFILE",None) is not None:
        log_file_name=configs["LOGFILE"]
    file_log=open(log_file_name,"w")
    if configs.get("DBPASSWORD",None) is not None:
        redis_cache = redis.StrictRedis(password=configs["DBPASSWORD"])
    else:
        redis_cache = redis.StrictRedis()
    with app.app_context():
        serve(app,host="0.0.0.0",port=5000,connection_limit=200,threads=8)
        #app.run(port=5000,host="localhost")
    
    # Option 2 : if you use this option you can run the file by just "python flaskredis.py"
    # from waitress import serve
    # with app.app_context():
    #     serve(app,host="localhost",port=5000)
except KeyboardInterrupt:
    print("Exited")
    writeLog("Flask Exited because of keyboard Interrupt")

file_log.close()
