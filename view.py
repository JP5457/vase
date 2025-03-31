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

from RecordingManager import RecordingManager

#url to redirect to when using jwt auth
notice_url = os.environ.get('NOTICE_URL', "http://127.0.0.1:5042/")

#key used for myradio jwt auth
myradio_key = os.environ.get('MYRADIO_SIGNING_KEY', "dev")

#key used to validate myradio api requests. This is the only thing you will need to edit for development.
myradio_api = os.environ.get('MYRADIO_API_KEY', "CHANGE_ME")

#I'm not sure if this does anything but i'm scared to delete it
log_location = os.environ.get('LOG_LOCATION', "/logs/")

#url of the myradio api, change this if you want to test with the myradio dev instance (you don't)
myradio_url = os.environ.get('MYRADIO_URL', "https://www.ury.org.uk/api/v2/")

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

folder = "/streams"
recordingmanager = RecordingManager(folder)

@scheduler.task('interval', id='do_job_1', minutes=2, misfire_grace_time=900)
def job1():
    print("cleaning stream " + str(unix_timestamp) , file=sys.stderr)

@scheduler.task('interval', id='do_job_2', seconds=1, misfire_grace_time=900)
def job2():
    recordingmanager.UpdateStates()

def verifyKey(key):
    pattern = re.compile('^[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789]+$')
    return re.search(pattern, key)

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
    return {'state' : recordingmanager.GetState(int(uid))}

@app.route("/clipper/stoprecording/<uid>")
def stoprec(uid):
    return {'info' : recordingmanager.StopRecording(int(uid))}

@app.route('/clipper/getaudio/<uid>')
def getclip(uid):
    clip = AudioSegment.from_mp3(folder + '/stream' + str(uid) + '.mp3')
    #clip = clip[(-1000*120):]
    clip.export("clip.mp3", format="mp3")
    return send_file('clip.mp3')

@app.route('/clipper/makeclip/<uid>/<start>/<end>')
def makeclip(uid,start,end):
    if verifyKey(key) and verifySession(session):
        clip = AudioSegment.from_mp3(clips_location+str(key)+"cl.mp3")
        #clip = clip[(int(start)*1000):(int(end)*1000)]
        clip.export(clips_location+str(key)+"clip.mp3", format="mp3")
        return {"status": "complete"}

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5040))
    print("Starting server on port " + str(port) , file=sys.stderr)
    app.run(debug=False, host='0.0.0.0', port=port)
