#!/usr/bin/env python
import datetime
import json
import requests


class Schedule:
    ovenCount = 0

    def __init__(self, local):
        self.local = local
        Schedule.ovenCount += 1

    def getdefaultschedule(self):
        jsonStruct = {"mon": [{"start": 0, "end": 6.5, "setpoint": 8}, {"start": 6.5, "end": 8.5, "setpoint": "22.0"},
                              {"start": 8.5, "end": 16, "setpoint": 12}, {"start": 16, "end": 19, "setpoint": "22.0"},
                              {"start": 19, "end": 24, "setpoint": 8}],
                      "tue": [{"start": 0, "end": 6.5, "setpoint": 8}, {"start": 6.5, "end": 8.5, "setpoint": "22.0"},
                              {"start": 8.5, "end": 16, "setpoint": 12}, {"start": 16, "end": 19, "setpoint": "18.0"},
                              {"start": 19, "end": 24, "setpoint": "23.0"}],
                      "wed": [{"start": 0, "end": 6.5, "setpoint": "8.0"},
                              {"start": 6.5, "end": 8.5, "setpoint": "23.0"}, {"start": 8.5, "end": 16, "setpoint": 12},
                              {"start": 16, "end": 23.5, "setpoint": 18}, {"start": 23.5, "end": 24, "setpoint": 8}],
                      "thu": [{"start": 0, "end": 6.5, "setpoint": 8}, {"start": 6.5, "end": 8.5, "setpoint": 18},
                              {"start": 8.5, "end": 16, "setpoint": 12}, {"start": 16, "end": 23, "setpoint": 18},
                              {"start": 23, "end": 24, "setpoint": 8}],
                      "fri": [{"start": 0, "end": 7, "setpoint": 8}, {"start": 7, "end": 9, "setpoint": 18},
                              {"start": 9, "end": 16, "setpoint": 12}, {"start": 16, "end": 22.5, "setpoint": 15},
                              {"start": 22.5, "end": 24, "setpoint": 8}],
                      "sat": [{"start": 0, "end": 9, "setpoint": 8}, {"start": 9, "end": 13.5, "setpoint": 18},
                              {"start": 13.5, "end": 16, "setpoint": 12},
                              {"start": 16, "end": 22.5, "setpoint": "25.0"},
                              {"start": 22.5, "end": 24, "setpoint": 9}],
                      "sun": [{"start": 0, "end": 9, "setpoint": 8}, {"start": 9, "end": 13.5, "setpoint": 18},
                              {"start": 13.5, "end": 16, "setpoint": 12}, {"start": 16, "end": 23, "setpoint": 18},
                              {"start": 23, "end": 24, "setpoint": 8}]}
        schedule = jsonStruct
        return schedule

    def getjsonstruct(self):
        if self.local == 1:
            schedule = self.getdefaultschedule()
        elif self.local == 2:
            from database import Database
            db = Database()
            jsonStruct = db.getdbvalues()
            schedule = json.loads(jsonStruct)
        else:
            # Our resource takes longer than `read_timeout` to send a byte.
            read_timeout = 20.0
            try:
                scheduleRaw = requests.get(url="http://.../api/api.php/categories/1?name",
                                           timeout=(15.0, read_timeout))
            except requests.exceptions.RequestException as e:  # This is the correct syntax
                print e
                print 'failed to obtain any schedule, fallback to default schedule'
                schedule = self.getdefaultschedule()
                return schedule
            scheduleJson = json.loads(scheduleRaw.content)
            a = scheduleJson['name']
            schedule = json.loads(a)
        return schedule

    def getheatingschedule(self, shedule):
        heating = {}
        # set up some default dummy numbers
        days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        setpoint = 21
        # heating['state'] = 14
        heating['manualsetpoint'] = 18
        heating['mode'] = "schedule";
        heating['schedule'] = shedule

        tG = datetime.datetime.now().time()
        timenow = tG.hour + (tG.minute / 60.0)
        today = days[datetime.datetime.today().weekday()]
        for period in heating['schedule'][today]:
            if period['start'] <= timenow and period['end'] > timenow:
                if heating['mode'] == "schedule":
                    heating['manualsetpoint'] = float(period['setpoint'])

        return heating, setpoint, tG, days

    def update(self, setpoint, tG, heating, days, fbSetpoint):
        tG = datetime.datetime.now().time()
        timenow = tG.hour + (tG.minute / 60.0)
        today = days[datetime.datetime.today().weekday()]
        lastsetpoint = setpoint
        updatesetpoint = False;

        try:
            schedule = self.getjsonstruct()
            if schedule is None:
                return fbSetpoint  # failed to update setpoint, turn to default

            heating['schedule'] = schedule

        except requests.exceptions.ReadTimeout as e:
            print "Waited too long between bytes."
            pass

        for period in heating['schedule'][today]:
            if period['start'] <= timenow and period['end'] > timenow:
                if heating['mode'] == "schedule":
                    setpoint = float(period['setpoint'])

        if lastsetpoint != setpoint and heating['mode'] == "schedule":
            print  'Obtained new setpoint from schedule:  {} at time: {} '.format(str(float(setpoint)), str(tG))
            updatesetpoint = True;

        return setpoint, updatesetpoint, tG
