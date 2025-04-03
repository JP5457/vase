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
            cursor.execute(schema.read())
        conn.commit()
        conn.close()


    def addclip(self, clipname, streamname="unnamed"):
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

    def printclip(self):
        conn = sqlite3.connect(self.dbfile)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clips")
        rows = cursor.fetchall()
        print(rows, file=sys.stderr)
        conn.close()

if __name__ == "__main__":
    dbmanager = DBManager("/home/bigjimmy/Desktop/vase/vase.db")
    print(dbmanager.getclip(3))

