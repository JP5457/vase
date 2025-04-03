from flask import Flask, render_template, redirect, session, request, send_file
from flask_apscheduler import APScheduler
from datetime import datetime
from pydub import AudioSegment
import os
import requests
import json
import random
import pytz
import sys
import secrets
import re
import jwt
import shutil

from RecordingManager import RecordingManager
from DBManager import DBManager

#I'm not sure if this does anything but i'm scared to delete it
log_location = os.environ.get('LOG_LOCATION', "/logs/")


#creates an app and scheduler thread
class Config:
    SCHEDULER_API_ENABLED = True
    PREFERRED_URL_SCHEME = 'https'

app = Flask(__name__)
app.config.from_object(Config())

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

unix_timestamp = (datetime.now() - datetime(1970, 1, 1)).total_seconds()
print("Starting at " + str(unix_timestamp) , file=sys.stderr)

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16) 

streamfolder = "/streams/"
tempclipfolder = "/clipstore/"
volumefolder = "/opt/"

recordingmanager = RecordingManager(streamfolder)
dbmanager = DBManager(volumefolder + "vase.db")

@scheduler.task('interval', id='do_job_1', minutes=2, misfire_grace_time=900)
def job1():
    print("cleaning stream " + str(unix_timestamp) , file=sys.stderr)
    recordingmanager.CleanStreams()

@scheduler.task('interval', id='do_job_2', seconds=1, misfire_grace_time=900)
def job2():
    recordingmanager.UpdateStates()

import random, string

def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

def verifyKeys(keys):
    for key in keys:
        pattern = re.compile('^[-ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789]+$')
        if not re.search(pattern, key):
            return False
    return True

def verifySession(session):
    if myradio_key == "dev":
        return True
    if ('name' in session and 'uid' in session):
        api_url = myradio_url + "/user/"+str(session["uid"])+"/permissions?" + myradio_apikey
        response = requests.get(api_url)
        officer = json.loads(response.text)
        if 221 in officer["payload"] or 234 in officer["payload"]:
            return True
    return False

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/clipper")
def clipper():
    return render_template('clipper.html')

@app.route("/clipper/startrecording", methods=['POST'])
def startrec():
    if request.method == 'POST':
        info = request.get_json(silent=True)
        url = info['url']
        uid = recordingmanager.StartRecording(url)
        return {'uid': uid}

@app.route("/clipper/getstate/<uid>")
def getstate(uid):
    if not verifyKeys([uid]):
        return "error"
    return {'state' : recordingmanager.GetState(int(uid))}

@app.route("/clipper/stoprecording/<uid>")
def stoprec(uid):
    if not verifyKeys([uid]):
        return "error"
    return {'info' : recordingmanager.StopRecording(int(uid))}

@app.route('/clipper/makeaudio/<uid>/<size>')
def makeaudio(uid, size):
    if not verifyKeys([uid]):
        return "error"
    times = {
        '1': 60,
        '2': 120,
        '3': 180,
        '4': 240,
        '5': 300,
        '30': 30
    }
    cliplen = 1000* times.get(size, 120)
    clipid = randomword(32)
    clip = AudioSegment.from_mp3(streamfolder + 'stream' + str(uid) + '.mp3')
    if len(clip) > cliplen:
        clip = clip[(-1*cliplen):]
    else:
        extralen = cliplen - len(clip) 
        try:
            bonusclip = AudioSegment.from_mp3(streamfolder + 'stream-old' + str(uid) + '.mp3')
            if len(bonusclip) > extralen:
                bonusclip = bonusclip[(-1*extralen):]
            clip = bonusclip + clip
        except:
            pass
    clip.export(tempclipfolder+clipid+".mp3", format="mp3")
    return {'uid': clipid}

@app.route('/clipper/getaudio/<uid>')
def getaudio(uid):
    if not verifyKeys([uid]):
        return "keyerror"
    try:
        return send_file(tempclipfolder+uid+".mp3")
    except:
        return "error"

@app.route('/clipper/getclip/<uid>')
def getclip(uid):
    if not verifyKeys([uid]):
        return "keyerror"
    try:
        return send_file(tempclipfolder+uid+"_clip.mp3")
    except:
        return "error"

@app.route('/clipper/makeclip/<uid>/<start>/<end>')
def makeclip(uid,start,end):
    if not verifyKeys([uid, start, end]):
        return "error"
    clip = AudioSegment.from_mp3(tempclipfolder+uid+".mp3")
    clipstart = (int(start)*1000)
    clipend = (int(end)*1000)
    if clipstart < 0 or clipstart > len(clip):
        clipstart = 0
    if clipend < 0 or clipend > len(clip):
        clipend = len(clip)-2
    clip = clip[clipstart:clipend]
    clip.export(tempclipfolder+uid+"_clip.mp3", format="mp3")
    return {"status": "complete"}

@app.route('/clipper/saveclip/<uid>/<name>/<stream>')
def saveclip(uid, name, stream):
    if not verifyKeys([uid, name, stream]):
        return "error"
    clipid = dbmanager.addclip(name, stream)
    shutil.copyfile(tempclipfolder+uid+"_clip.mp3", (volumefolder + name + str(clipid) + '.mp3'))
    dbmanager.printclip()
    return {"uid": clipid}


@app.route('/clips/<uid>')
def viewclip(uid):
    if not verifyKeys([uid]):
        return "error"
    clipinfo = dbmanager.getclip(uid)
    

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5040))
    print("Starting server on port " + str(port) , file=sys.stderr)
    app.run(debug=False, host='0.0.0.0', port=port)
