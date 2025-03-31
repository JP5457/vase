from RecordingProcess import RecordingProcess
import multiprocessing
import random
import time
import sys

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
        self.threads[id] = {"process": newprocess, "url": url}
        process = self.threads[id]["process"]
        process.start()
        return id
        
    def GetState(self, id):
        try:
            if id in self.threads:
                return self.states[id]
            else:
                return "closed"
        except:
            return "closed"

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
            return "shutdown"
        except:
            return "error"
        
if __name__ == "__main__":
    manager = RecordingManager('/home/bigjimmy/Desktop/vase')
    id1 = manager.StartRecording('http://audio.ury.org.uk/OB-Line')
    id2 = manager.StartRecording('http://audio.ury.org.uk/jukebox')
    for i in range(0, 90):
        manager.UpdateStates()
        print(manager.GetState(id1) + " " + str(id1))
        print(manager.GetState(id2) + " " + str(id2))
        if i > 80:
            print(manager.StopRecording(id1))
        if i > 85:
            print(manager.StopRecording(id2))           
        time.sleep(1)
    print("finished")

    