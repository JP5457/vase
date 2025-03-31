import multiprocessing
from datetime import datetime
import requests
import sys
from pydub import AudioSegment

class RecordingProcess(multiprocessing.Process):
    def __init__(self, stream_url, queue, id, folder):
        super().__init__()
        self.stream_url = stream_url
        self.state = "loading"
        self.queue = queue
        self.id = id
        self.folder = folder
        self.file = self.folder + '/stream' + str(id) + '.mp3'
        self.exit = multiprocessing.Event()
        

    def run(self):
        r = requests.get(self.stream_url, stream=True)
        with open(self.file, 'wb') as f:
            while not self.exit.is_set():
                try:
                    for block in r.iter_content(1024):
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
                except:
                    if not self.exit.is_set():
                        r = requests.get(self.stream_url, stream=True)
        print("You exited!")

    def Shutdown(self):
        print("Shutdown initiated")
        self.exit.set()
        os.remove(self.file)
