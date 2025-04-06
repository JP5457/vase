import sqlite3
import sys
from datetime import datetime

class DBManager:
    def __init__(self, dbfile):
        print(dbfile, file=sys.stderr)
        self.dbfile = dbfile
        conn = sqlite3.connect(self.dbfile)
        cursor = conn.cursor()
        with open("schema.sql", 'r') as schema:
            cursor.executescript(schema.read())
        conn.commit()
        conn.close()


    def addclip(self, clipname, streamname):
        conn = sqlite3.connect(self.dbfile)
        cursor = conn.cursor()
        query = "INSERT INTO clips (clipname, streamname) VALUES (?, ?) RETURNING id"
        cursor.execute(query, (clipname, streamname))
        new_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return new_id

    def getclip(self, id):
        conn = sqlite3.connect(self.dbfile)
        cursor = conn.cursor()
        query = "SELECT * FROM clips WHERE id == ?"
        cursor.execute(query, (id,))
        clipinfo = cursor.fetchone()
        conn.commit()
        conn.close()
        return clipinfo

    def filterstream(self, stream):
        conn = sqlite3.connect(self.dbfile)
        cursor = conn.cursor()
        query = "SELECT * FROM clips WHERE streamname == ? ORDER BY id DESC"
        cursor.execute(query, (stream,))
        clips = cursor.fetchall()
        conn.commit()
        conn.close()
        return clips

    def searchclip(self, search):
        conn = sqlite3.connect(self.dbfile)
        cursor = conn.cursor()
        searchcond = "'%" + search + "%'"
        query = "SELECT * FROM clips WHERE streamname LIKE "+searchcond+" OR clipname LIKE " + searchcond + " ORDER BY id DESC"
        cursor.execute(query)
        clips = cursor.fetchall()
        conn.commit()
        conn.close()
        return clips

    def allclip(self):
        conn = sqlite3.connect(self.dbfile)
        cursor = conn.cursor()
        query = "SELECT * FROM clips ORDER BY id DESC"
        cursor.execute(query)
        clips = cursor.fetchall()
        conn.commit()
        conn.close()
        return clips

    def lastclips(self, clips):
        conn = sqlite3.connect(self.dbfile)
        cursor = conn.cursor()
        query = "SELECT * FROM clips ORDER BY id DESC LIMIT ?"
        cursor.execute(query, (clips,))
        clips = cursor.fetchall()
        conn.commit()
        conn.close()
        return clips

    def editclip(self, clipid, clipname, streamname):
        conn = sqlite3.connect(self.dbfile)
        cursor = conn.cursor()
        query = "UPDATE clips SET clipname = ?, streamname = ? WHERE id = ?"
        cursor.execute(query, (clipname, streamname, clipid))
        conn.commit()
        conn.close()

    def deleteclip(self, clipid):
        conn = sqlite3.connect(self.dbfile)
        cursor = conn.cursor()
        query = "DELETE FROM clips WHERE id = ?"
        cursor.execute(query, (clipid, ))
        conn.commit()
        conn.close()

    def addannouncement(self, title, content):
        conn = sqlite3.connect(self.dbfile)
        cursor = conn.cursor()
        query = "INSERT INTO announcements (title, content, posted) VALUES (?, ?, current_timestamp) RETURNING id"
        cursor.execute(query, (title, content))
        new_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return new_id

    def getannoucements(self, num):
        conn = sqlite3.connect(self.dbfile)
        cursor = conn.cursor()
        query = "SELECT * FROM announcements ORDER BY id DESC LIMIT ?"
        cursor.execute(query, (num,))
        announcements = cursor.fetchall()
        conn.commit()
        conn.close()
        return announcements

    def addsound(self, name, library):
        conn = sqlite3.connect(self.dbfile)
        cursor = conn.cursor()
        query = "INSERT INTO sounds (soundname, library) VALUES (?, ?) RETURNING id"
        cursor.execute(query, (name, library))
        new_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return new_id

    def getsounds(self, library="All"):
        conn = sqlite3.connect(self.dbfile)
        cursor = conn.cursor()
        if library == "All":
            query = "SELECT * FROM sounds ORDER BY id DESC"#
            cursor.execute(query)
        else:
            query = "SELECT * FROM sounds WHERE library = ? ORDER BY id DESC"
            cursor.execute(query, (library,))
        sounds = cursor.fetchall()
        conn.commit()
        conn.close()
        return sounds

if __name__ == "__main__":
    dbmanager = DBManager("/home/bigjimmy/Desktop/vase/vase.db")
    print(dbmanager.getclip(3))

