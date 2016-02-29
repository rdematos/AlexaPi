#! /usr/bin/env python

import os
import random
import time
import alsaaudio
import wave
import random
from creds import *
import requests
import json
import re
from memcache import Client
#SenseHat Settings
from sense_hat import SenseHat

r = [255, 0, 0]
g = [0, 255, 0]
b = [0, 0, 255]
c = [0,255,255]
w = [255,255,255]
e = [0, 0, 0]  # e stands for empty/black

ready = [
e,e,e,e,e,e,e,e,
e,e,e,e,e,e,e,e,
e,e,e,e,e,e,e,e,
e,e,e,w,w,e,e,e,
e,e,e,w,w,e,e,e,
e,e,e,e,e,e,e,e,
e,e,e,e,e,e,e,e,
e,e,e,e,e,e,e,e
]

listening = [
e,e,e,e,e,e,e,e,
e,e,e,e,e,e,e,e,
e,e,e,e,e,e,e,e,
e,e,e,c,c,e,e,e,
e,e,e,c,c,e,e,e,
e,e,e,e,e,e,e,e,
e,e,e,e,e,e,e,e,
e,e,e,e,e,e,e,e
]

processing = [
e,e,e,e,e,e,e,e,
e,e,e,e,e,e,e,e,
e,e,e,e,e,e,e,e,
e,e,e,b,b,e,e,e,
e,e,e,b,b,e,e,e,
e,e,e,e,e,e,e,e,
e,e,e,e,e,e,e,e,
e,e,e,e,e,e,e,e
]

speaking = [
e,e,e,e,e,e,e,e,
e,e,e,e,e,e,e,e,
e,e,e,e,e,e,e,e,
e,e,e,g,g,e,e,e,
e,e,e,g,g,e,e,e,
e,e,e,e,e,e,e,e,
e,e,e,e,e,e,e,e,
e,e,e,e,e,e,e,e
]

error = [
e,e,e,e,e,e,e,e,
e,e,e,e,e,e,e,e,
e,e,e,e,e,e,e,e,
e,e,e,r,r,e,e,e,
e,e,e,r,r,e,e,e,
e,e,e,e,e,e,e,e,
e,e,e,e,e,e,e,e,
e,e,e,e,e,e,e,e
]

device = "plughw:1" # Name of your microphone/soundcard in arecord -L

#Setup
recorded = False
servers = ["127.0.0.1:11211"]
mc = Client(servers, debug=1)
path = os.path.realpath(__file__).rstrip(os.path.basename(__file__))

def internet_on():
    print "Checking Internet Connection"
    try:
        r =requests.get('https://api.amazon.com/auth/o2/token')
        print "Connection OK"
        sense.set_pixels(ready)
        return True
    except:
        print "Connection Failed"
        sense.set_pixels(error)
        return False


def gettoken():
    token = mc.get("access_token")
    refresh = refresh_token
    if token:
        return token
    elif refresh:
        payload = {"client_id" : Client_ID, "client_secret" : Client_Secret, "refresh_token" : refresh, "grant_type" : "refresh_token", }
        url = "https://api.amazon.com/auth/o2/token"
        r = requests.post(url, data = payload)
        resp = json.loads(r.text)
        mc.set("access_token", resp['access_token'], 3570)
        return resp['access_token']
    else:
        return False


def alexa():
    url = 'https://access-alexa-na.amazon.com/v1/avs/speechrecognizer/recognize'
    headers = {'Authorization' : 'Bearer %s' % gettoken()}
    d = {
           "messageHeader": {
               "deviceContext": [
                   {
                       "name": "playbackState",
                       "namespace": "AudioPlayer",
                       "payload": {
                           "streamId": "",
                           "offsetInMilliseconds": "0",
                           "playerActivity": "IDLE"
                       }
                   }
               ]
        },
           "messageBody": {
               "profile": "alexa-close-talk",
               "locale": "en-us",
               "format": "audio/L16; rate=16000; channels=1"
           }
    }
    with open(path+'recording.wav') as inf:
        files = [
                ('file', ('request', json.dumps(d), 'application/json; charset=UTF-8')),
                ('file', ('audio', inf, 'audio/L16; rate=16000; channels=1'))
                ]
        r = requests.post(url, headers=headers, files=files)
    sense.set_pixels(processing)
    if r.status_code == 200:
        for v in r.headers['content-type'].split(";"):
            if re.match('.*boundary.*', v):
                boundary =  v.split("=")[1]
        data = r.content.split(boundary)
        for d in data:
            if (len(d) >= 1024):
                audio = d.split('\r\n\r\n')[1].rstrip('--')
        with open(path+"response.mp3", 'wb') as f:
            f.write(audio)
        sense.set_pixels(speaking)
        os.system('mpg123 -q {}1sec.mp3 {}response.mp3'.format(path, path))
        sense.set_pixels(ready)
    else:
        for x in range(0, 3):
            time.sleep(.2)
            sense.clear()
            time.sleep(.2)
            sense.set_pixels(error)
        sense.set_pixels(ready)


def start():
    xaxis, yaxis, zaxis = sense.get_accelerometer_raw().values()
    last = round(yaxis, 0)
    while True:
        xaxis, yaxis, zaxis = sense.get_accelerometer_raw().values()
        val = round(yaxis, 0)
        if val != last:
            sense.set_pixels(listening)
            last = val
            if val == -0.0 and recorded == True:
                sense.set_pixels(processing)
                rf = open(path+'recording.wav', 'w')
                rf.write(audio)
                rf.close()
                inp = None
                alexa()
            elif val == -1.0:
                inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, device)
                inp.setchannels(1)
                inp.setrate(16000)
                inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
                inp.setperiodsize(500)
                audio = ""
                l, data = inp.read()
                if l:
                    audio += data
                recorded = True
        elif val == -1.0:
            l, data = inp.read()
            if l:
                audio += data

if __name__ == "__main__":
    sense = SenseHat()
    sense.clear()
    while internet_on() == False:
        print "."
        sense.show_message("Connect to Internet", text_colour=r, scroll_speed=0.05)
    sense.clear()
    token = gettoken()
    os.system('mpg123 -q {}1sec.mp3 {}hello.mp3'.format(path, path))
    sense.show_message("raise to speak", text_colour=w, scroll_speed=0.05)
    sense.set_pixels(ready)
    start()
