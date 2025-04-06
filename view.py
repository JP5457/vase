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
import time

from RecordingManager import RecordingManager
from DBManager import DBManager
from forms import Forms

#I'm not sure if this does anything but i'm scared to delete it
log_location = os.environ.get('LOG_LOCATION', "/logs/")

admin_password = os.environ.get('ADMIN_PASSWORD', "dev")

vase_url = os.environ.get('VASE_URL', "localhost:5040")

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
forms = Forms(dbmanager)

@scheduler.task('interval', id='do_job_1', minutes=2, misfire_grace_time=900)
def job1():
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

def isadmin(session):
    if 'admin' in session:
        return session['admin']
    else:
        return False

def format_datetime_readable(datetime_str):
    dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    def ordinal(n):
        if 11 <= n % 100 <= 13:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
        return f"{n}{suffix}"
    readable = f"Posted at {dt.strftime('%H:%M')} on the {ordinal(dt.day)} of {dt.strftime('%B %Y')}"
    return readable

@app.route("/")
def index():
    announces = dbmanager.getannoucements(5)
    formatedannouncements = []
    seeall = False
    for i in announces:
        announce = {'title': i[1], 'content': i[2], 'datetime': format_datetime_readable(i[3])}
        formatedannouncements.append(announce)
    if len(announces) == 5:
        seeall = True
    return render_template('announcements.html', announcements=formatedannouncements, seeall = seeall)

@app.route('/announcements')
def announcements():
    announces = dbmanager.getannoucements(100)
    formatedannouncements = []
    seeall = False
    for i in announces:
        announce = {'title': i[1], 'content': i[2], 'datetime': format_datetime_readable(i[3])}
        formatedannouncements.append(announce)
    return render_template('announcements.html', announcements=formatedannouncements, seeall = False)

@app.route("/clipper")
def clipper():
    return render_template('clipper.html')

@app.route("/clipper/startrecording", methods=['POST'])
def startrec():
    if request.method == 'POST':
        info = request.get_json(silent=True)
        url = info['url']
        try:
            if url[:4] != 'http':
                url = "http://" + url
        except:
            return {'uid': 0}
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
    return {"uid": clipid}


@app.route('/clips')
def clips():
    clips = dbmanager.lastclips(10)
    formatedclips = []
    seeall = False
    for i in clips:
        clip = {'url': '/clips/'+str(i[0]), 'audiourl': '/clips/audio/'+str(i[0]), 'clipname': i[1].replace('-', ' '), 'streamname': i[2].replace('-', ' '), 'streamurl': '/clips/filter/stream/'+i[2]}
        if isadmin(session):
            clip['editurl'] = '/clips/edit/'+str(i[0])
        formatedclips.append(clip)
    if len(clips) == 10:
        seeall = True
    return render_template('cliplist.html', clips=formatedclips, searchterm = "", seeall = seeall)

@app.route('/clips/<uid>')
def viewclip(uid):
    if not verifyKeys([uid]):
        return "error"
    clipinfo = dbmanager.getclip(uid)
    name = clipinfo[1]
    stream = clipinfo[2]
    editurl = ""
    if isadmin(session):
        editurl = '/clips/edit/'+str(uid)
    url = '/clips/audio/'+str(uid)
    return render_template('clippage.html', name=name.replace('-', ' '), stream=stream.replace('-', ' '), url=url, streamurl = '/clips/filter/stream/'+stream, editurl=editurl, linkurl=vase_url+url)

@app.route('/clips/audio/<uid>')
def getclipaudio(uid):
    if not verifyKeys([uid]):
        return "error"
    clipinfo = dbmanager.getclip(uid)
    name = clipinfo[1]
    return send_file(volumefolder + name + str(uid) + '.mp3')

@app.route('/clips/filter/stream/<stream>')
def clipstreamfilter(stream):
    if not verifyKeys([stream]):
        return "error"
    clips = dbmanager.filterstream(stream)
    formatedclips = []
    for i in clips:
        clip = {'url': '/clips/'+str(i[0]), 'audiourl': '/clips/audio/'+str(i[0]), 'clipname': i[1].replace('-', ' '), 'streamname': i[2].replace('-', ' '), 'streamurl': '/clips/filter/stream/'+i[2]}
        if isadmin(session):
            clip['editurl'] = '/clips/edit/'+str(i[0])
        formatedclips.append(clip)
    return render_template('cliplist.html', clips=formatedclips, searchterm = "", seeall = False)

@app.route('/clips/search/<search>')
def clipsearch(search):
    if not verifyKeys([search]):
        return "error"
    clips=dbmanager.searchclip(search)
    formatedclips = []
    for i in clips:
        clip = {'url': '/clips/'+str(i[0]), 'audiourl': '/clips/audio/'+str(i[0]), 'clipname': i[1].replace('-', ' '), 'streamname': i[2].replace('-', ' '), 'streamurl': '/clips/filter/stream/'+i[2]}
        if isadmin(session):
            clip['editurl'] = '/clips/edit/'+str(i[0])
        formatedclips.append(clip)
    return render_template('cliplist.html', clips=formatedclips, searchterm = search.replace('-', ' '), seeall = False)

@app.route('/clips/all')
def clipall():
    clips=dbmanager.allclip()
    formatedclips = []
    for i in clips:
        clip = {'url': '/clips/'+str(i[0]), 'audiourl': '/clips/audio/'+str(i[0]), 'clipname': i[1].replace('-', ' '), 'streamname': i[2].replace('-', ' '), 'streamurl': '/clips/filter/stream/'+i[2]}
        if isadmin(session):
            clip['editurl'] = '/clips/edit/'+str(i[0])
        formatedclips.append(clip)
    return render_template('cliplist.html', clips=formatedclips, searchterm = "", seeall = False)

@app.route('/clips/edit/<uid>', methods=['POST','GET'])
def editclip(uid):
    if not verifyKeys([uid]):
        return "error"
    if not isadmin(session):
        return redirect('/clips/'+str(uid), code=302)
    form = forms.buildClipEdit(uid)
    if form.is_submitted():
        clipname = form.name.data
        streamname = form.streamname.data
        dbmanager.editclip(uid, clipname, streamname)
        return redirect('/clips/'+str(uid), code=302)
    else:
        return render_template('editclip.html', form=form, deleteurl = "/clips/delete/"+str(uid))

@app.route('/clips/delete/<uid>')
def deleteclip(uid):
    if not verifyKeys([uid]):
        return "error"
    if not isadmin(session):
        return redirect('/clips/'+str(uid), code=302)
    clipinfo = dbmanager.getclip(uid)
    os.remove(volumefolder + clipinfo[1] + str(uid) + '.mp3')
    dbmanager.deleteclip(uid)
    return redirect('/clips', code=302)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == 'mp3'

@app.route('/clips/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        name = request.form['clipname'].replace(" ", "-")
        if not verifyKeys([name]):
            return "error"
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            clipid = dbmanager.addclip(name, "Upload")
            file.save(volumefolder + name + str(clipid) + '.mp3')
            return redirect('/clips/'+str(clipid), code=302)
    return render_template("uploadclip.html")


@app.route('/sounds/upload', methods=['GET', 'POST'])
def uploadsound():
    if not isadmin(session):
        return redirect('/admin', code=302)
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        name = request.form['soundname'].replace(" ", "-")
        library = request.form['library']
        if not verifyKeys([name]):
            return "error"
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            soundid = dbmanager.addsound(name, library)
            file.save(volumefolder + str(soundid) + "sound" + '.mp3')
            return redirect('/sounds/audio/'+str(soundid), code=302)
    return render_template("uploadsound.html")

@app.route('/sounds/audio/<uid>')
def getsoundaudio(uid):
    if not verifyKeys([uid]):
        return "error"
    return send_file(volumefolder + str(uid) + "sound" + '.mp3')


@app.route('/admin', methods=['POST','GET'])
def auth():
    if isadmin(session):
        return render_template('admin.html')
    form = forms.buildLoginForm()
    if form.is_submitted():
        time.sleep(5)
        inputpass = form.password.data
        if inputpass == admin_password:
            session['admin'] = True
        else:
            session['admin'] = False
            return redirect('/admin', code=302)
        return redirect('/admin', code=302)
    else:
        return render_template('login.html', form=form)

@app.route('/admin/announce', methods=['POST','GET'])
def announce():
    if not isadmin(session):
        return redirect('/admin', code=302)
    form = forms.buildAnnouncementForm()
    if form.is_submitted():
        title = form.title.data
        content = form.content.data
        id = dbmanager.addannouncement(title, content)
        return redirect('/announcements', code=302)
    else:
        return render_template("announcementform.html", form=form)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5040))
    print("Starting server on port " + str(port) , file=sys.stderr)
    app.run(debug=False, host='0.0.0.0', port=port)
