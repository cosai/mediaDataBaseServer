#!/bin/bash
sudo systemctl stop flaskredis
cd ~/exampleRedisServer
#git remote add origin https://github.com/cosai/exampleRedisServer.git
rm flaskRedis.py
git reset --hard
git pull pullink main
sudo systemctl start flaskredis
