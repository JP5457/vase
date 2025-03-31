from datetime import datetime
from pydub import AudioSegment
import sys

unix_timestamp = (datetime.now() - datetime(1970, 1, 1)).total_seconds()
print("Starting at " + str(unix_timestamp))


clip = AudioSegment.from_mp3("testlong.mp3")
clip = clip[(-1000*120):]
clip.export("clip.mp3", format="mp3")

complete_timestamp = (datetime.now() - datetime(1970, 1, 1)).total_seconds()
print("Finished at " + str(complete_timestamp))
diff = complete_timestamp - unix_timestamp
print("long time taken: " + str(diff))

clip = AudioSegment.from_mp3("testshort.mp3")
clip = clip[(-1000*120):]
clip.export("newclip.mp3", format="mp3")

othercomplete_timestamp = (datetime.now() - datetime(1970, 1, 1)).total_seconds()
print("Finished at " + str(othercomplete_timestamp))
diff = othercomplete_timestamp - complete_timestamp
print("long time taken: " + str(diff))