from RecordingProcess import RecordingProcess
import multiprocessing
import random
import time
import sys
import os
from pydub import AudioSegment
from datetime import datetime


class RecordingManager:
    def __init__(self, folder):
        self.threads = {}
        self.states = {}
        self.queue = multiprocessing.Queue()
        self.queue.put(self.states)
        self.folder = folder

    def StartRecording(self, url):
        for key in self.threads:
            if self.threads[key]["url"] == url:
                return key
        id = random.randint(1,65536)
        while id in self.threads:
            id = random.randint(1,65536)
        newprocess = RecordingProcess(url, self.queue, id, self.folder)
        self.threads[id] = {"process": newprocess, "url": url, "lastread": (datetime.now() - datetime(1970, 1, 1)).total_seconds()}
        process = self.threads[id]["process"]
        process.start()
        return id
        
    def GetState(self, id):
        try:
            if id in self.threads:
                self.threads[id]["lastread"] = (datetime.now() - datetime(1970, 1, 1)).total_seconds()
                return self.states[id]
            else:
                return "closed"
        except:
            return "closed"

    def GetAllStates(self):
        toret = []
        for i in self.threads:
            info = {'id': i, "url": self.threads[i]["url"], "lastread": (datetime.now() - datetime(1970, 1, 1)).total_seconds()-self.threads[i]["lastread"], "state": self.states[i], "delete": "/admin/threads/close/"+str(i)}
            toret.append(info)
        return toret

    def UpdateStates(self):
        try:
            self.states = self.queue.get()
            self.queue.put(self.states)
        except:
            pass

    def StopRecording(self, id):
        try:
            self.threads[id]["process"].Shutdown()
            self.threads[id]["process"].join()
            del self.threads[id]
            time.sleep(1)
            os.remove(self.folder + 'stream' + str(id) + '.mp3')
            return "shutdown"
        except:
            return "error"

    def CleanStreams(self):
        currenttime = (datetime.now() - datetime(1970, 1, 1)).total_seconds()
        tostop = []
        for i in self.threads:
            if (currenttime - self.threads[i]["lastread"]) > 900:
                tostop.append(i)
        for i in tostop:
            self.StopRecording(i)
        
if __name__ == "__main__":
    manager = RecordingManager('/home/bigjimmy/Desktop/vase/')
    id2 = manager.StartRecording('http://audio.ury.org.uk/jukebox')
    for i in range(1, 70):
        manager.UpdateStates()
        print(manager.GetState(id2) + " " + str(id2))
        if i > 68:
            print(manager.StopRecording(id2))      
        time.sleep(1)
    print("finished")

    