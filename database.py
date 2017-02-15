#!/usr/bin/env python
import sqlite3


class Database():
    def __init__(self):
        pass

    @staticmethod
    def isSQLite3(filename):
        from os.path import isfile, getsize

        if not isfile(filename):
            return False
        if getsize(filename) < 100:  # SQLite database file header is 100 bytes
            return False

        with open(filename, 'rb') as fd:
            header = fd.read(100)

        return header[:16] == 'SQLite format 3\x00'

    def getdbvalues(self):

        filedb = 'schedule.db'
        a = self.isSQLite3(filedb)

        conn = sqlite3.connect(filedb)
        cursor = conn.cursor()

        if not a:
            # create a table
            cursor.execute("""create table if not exists json
                          (jsonstruct text, linenr text) 
                       """)

            # noinspection PyPep8
            jsonStruct = '{"mon":[{"start":0,"end":6.5,"setpoint":8},{"start":6.5,"end":8.5,"setpoint":"22.0"},{"start":8.5,"end":16,"setpoint":12},{"start":16,"end":19,"setpoint":"22.0"},{"start":19,"end":24,"setpoint":8}],"tue":[{"start":0,"end":6.5,"setpoint":8},{"start":6.5,"end":8.5,"setpoint":"22.0"},{"start":8.5,"end":16,"setpoint":12},{"start":16,"end":19,"setpoint":"18.0"},{"start":19,"end":24,"setpoint":"23.0"}],"wed":[{"start":0,"end":6.5,"setpoint":"8.0"},{"start":6.5,"end":8.5,"setpoint":"23.0"},{"start":8.5,"end":16,"setpoint":12},{"start":16,"end":21.5,"setpoint":"26.0"},{"start":21.5,"end":24,"setpoint":8}],"thu":[{"start":0,"end":6.5,"setpoint":8},{"start":6.5,"end":8.5,"setpoint":18},{"start":8.5,"end":16,"setpoint":12},{"start":16,"end":23,"setpoint":18},{"start":23,"end":24,"setpoint":8}],"fri":[{"start":0,"end":7,"setpoint":8},{"start":7,"end":9,"setpoint":18},{"start":9,"end":16,"setpoint":12},{"start":16,"end":22.5,"setpoint":15},{"start":22.5,"end":24,"setpoint":8}],"sat":[{"start":0,"end":9,"setpoint":8},{"start":9,"end":13.5,"setpoint":18},{"start":13.5,"end":16,"setpoint":12},{"start":16,"end":22.5,"setpoint":"25.0"},{"start":22.5,"end":24,"setpoint":9}],"sun":[{"start":0,"end":9,"setpoint":8},{"start":9,"end":13.5,"setpoint":18},{"start":13.5,"end":16,"setpoint":12},{"start":16,"end":23,"setpoint":18},{"start":23,"end":24,"setpoint":8}]}'
            linenr = "one"
            # insert data
            cursor.execute("INSERT INTO json VALUES (?, ?);", (jsonStruct, linenr))
            # save data to database
            conn.commit()

        # safe call
        t = ('one',)
        cursor.execute('SELECT * FROM json WHERE linenr=?', t)
        values = cursor.fetchone()

        conn.close()

        jsonStruct = values[0]

        return jsonStruct
