# exampleRedisServer
This is a media server and a database server.

**Database Server**: Python Flask web server with Redis No-SQL database integration at the back. The database server also supports IP INFORMATION Server.
If you go to the address my.database.server/learnip, this page will give requester's IP address.

**Media Server**: Pure Python Flask web server with image upload. The uploaded images are kept in Python dictionary. The images are uploaded from a username and stored in a Python dictionary with that username as key. Media server supports last active users (in last 5 seconds)

Both of those servers use a config file. That file should be named as *configserver.txt*. This is explained in **Config file field explanations** part.

Example configserver.txt is here:


LOGFILE: /home/ubuntu/log.txt

DBPASSWORD:passwordOfRedis

SIMPLE: True


## Config file field explanations ## 
If the SIMPLE entry is True, the media server will work without waitress. In this case, you will need to call waitress and give parameter as media server file. If it is not set or False, the media server will work with waitress as default. Thid field only works with media server. The database server works with waitress by default.

DBPASSWORD is used in database server. This is the plaintext of redis database password. This field only works with database server.

LOGFILE entry is the path that the output of the python code will be written to. This field is valid for both media and database servers.


## File Descriptions ##
*flaskRedis.py*  This is the daemon service for Flask Database Server. This file should be running in the server side. If we create a service, we need to run this program to create a database service. An example service file can be found under this repository.

*mediaServer.py*   This is the daemon service for Media Server. This file should be running in the server side. If we create a service, we need to run this program to create a database service. An example service file can be found under this repository.

*serverCode.py* This is the core code of the media server.

*testFiles/tester.py*     Tester functions that can be used to add/delete/entry in redis server

*testFiles/cameraSender.py*       Client of the media server, sends image from webcam to the media server

*autogit.sh*      When you clone this repository, make this file executable and copy it to one upper folder from the repository root folder. When you run that *autogit.sh* file, this file will update the repository. This will be possible only if you have cloned the repository, not downloaded the zip from github. You will need to change the folder path of this repository in your system. DO NOT call/run this file inside the repository's root folder.

*flaskredis.service*  This file is the file to be put under /etc/system.d/network/... If you want to create a service for database and media servers, you can use this file. If you create a service in Linux, that program will be run at boot and will be restarted automatically when it crashes.

*defaultNginx.conf*   This file is the file to be used in nginx web server. In order to create a proxy to port forward 5000 to 80, we were using nginx web server. This file is the configuration of the nginx web server. This file is also optional. If you don't want to port forward, you won't need this file.

## How to install Database Server? ##

`sudo apt-get install redis-server`

`pip install redis`

`sudo service redis start`

`sudo apt install -y libsm6 libxext6 ffmpeg libfontconfig1 libxrender1 libgl1-mesa-glx`

`pip install flask pillow imutils opencv-python opencv-contrib-python waitress flask_mqtt`

`sudo cp ./flaskredis.service /etc/systemd/system/flaskredis.service`

`sudo systemctl enable flaskredis`

`sudo systemctl start flaskredis`

## pages in media server ##

You can access those pages by accessing ex: my.media.server/shows.

*shows*     All the active camera feeds in one window

*streams*   All the active camera feeds shown as list with links.

*admin*     This is the admin panel. Password is *curruS101*. 

*log*        Shows the log of the service of the system. `journalctl` output is given. This is for debugging purposes 

*info*       This is the same with admin panel but the page doesn't require password.

## How to reverse proxy our page so that the weblink looks like something.com* for Media Server##

We are now serving on port 5000. We will need reverse proxy so that it will listen port 80 and forward the requests to port 5000.
For this purpose we will use nginx. Nginx is a webserver but has potential to be used as reverse proxy and file server. 
Our files will be served by nginx which will bring some speed to serving times. The nginx  *defaultNginx.conf* can be found in this repository.
Note that this part might be little though to create

The configuration file needed for nginx and https is explained below.

`sudo apt install nginx`

`cp /path/to/defaultNginx.conf /etc/nginx/sites-enabled/default`

`sudo service start nginx`

## How to enable the website for HTTPS for Media Server##

You need to enter those commands to create SSL keys so that they can be used by Nginx server later. 

`sudo add-apt-repository ppa:certbot/certbot`

`sudo apt-get update`

`sudo apt-get install python3-certbot-nginx`

`sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com`

`letsencrypt certonly -a webroot --webroot-path=/var/www/yourdomain.com/`


## How to install Media Server? ##

`sudo apt install -y libsm6 libxext6 ffmpeg libfontconfig1 libxrender1 libgl1-mesa-glx`

`pip install flask pillow imutils opencv-python opencv-contrib-python waitress`

After installing and running the file you can port forward your 5000 to 80 using ngrok. You need to modify the databasename variable in the serverCode.py file.

## How to avoid "Not use for production"? ##

- comment out the line "app.debug = True" in the flask code
- install waitress (pip install waitress)
- rather then running the flask with "python flaskRedis.py" use
*waitress-serve --host localhost flaskRedis:app*





Note:
equivalent to 'from hello import app'
waitress-serve --host 127.0.0.1 hello:app
