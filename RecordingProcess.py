import multiprocessing
from datetime import datetime
import requests
import sys
import shutil
import os
from pydub import AudioSegment

class RecordingProcess(multiprocessing.Process):
    def __init__(self, stream_url, queue, id, folder):
        super().__init__()
        self.stream_url = stream_url
        self.state = "loading"
        self.queue = queue
        self.id = id
        self.folder = folder
        self.file = self.folder + 'stream' + str(id) + '.mp3'
        self.exit = multiprocessing.Event()
        
    def run(self):
        r = requests.get(self.stream_url, stream=True)
        splittime = (datetime.now() - datetime(1970, 1, 1)).total_seconds()
        f = open(self.file, 'wb')
        try:
            while not self.exit.is_set():
                try:
                    for block in r.iter_content(1024):
                        #print(((datetime.now() - datetime(1970, 1, 1)).total_seconds() - splittime), file=sys.stderr)
                        try:
                            states = self.queue.get()
                            states[self.id] = self.state
                            self.queue.put(states)
                        except:
                            pass
                        if self.exit.is_set():
                            break
                        if len(block) > 120:
                            self.state = "recording"
                            f.write(block)
                        else:
                            self.state = "paused"
                            r = requests.get(self.stream_url, stream=True)
                            continue
                        if ((datetime.now() - datetime(1970, 1, 1)).total_seconds() - splittime) > 600:
                            splittime = (datetime.now() - datetime(1970, 1, 1)).total_seconds()
                            shutil.copyfile(self.file, (self.folder + 'stream-old' + str(self.id) + '.mp3'))
                            os.remove(self.file)
                            f = open(self.file, 'wb')
                except:
                    if not self.exit.is_set():
                        r = requests.get(self.stream_url, stream=True)
        finally:
            self.state = "closed"
            states = self.queue.get()
            states[self.id] = self.state
            self.queue.put(states)
            f.close()
        print("You exited!")

    def Shutdown(self):
        print("Shutdown initiated")
        self.exit.set()
        os.remove(self.file)