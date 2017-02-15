#!/usr/bin/env python
import paho.mqtt.client as mqtt
import time

from schedule import Schedule


class Deamon(object):
    def __init__(self, hostname, port, local):
        self.local = local
        self.hostname = hostname
        self.port = port
        self.inputstr = {}
        self._type = self.__class__.__name__
        self.mqttc = {}
        self.Schedule = {}

    @staticmethod
    def mqttupdate(setpoint, updatesetpoint, publish_topic, mqttc):
        if updatesetpoint is True:
            mqttc.publish(publish_topic, str(float(setpoint)))

    # The mqtt callback functions for when the node receives a CONNACK response from the server.
    @staticmethod
    def on_connect(client, inputstr, rc):
        print("Connected with result code " + str(rc))
        client.subscribe(inputstr['sub_state_temp'])
        client.subscribe(inputstr['sub_state_setpoint'])

    @staticmethod
    def on_subscribe(mosq, obj, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    @staticmethod
    def on_message(client, inputstr, msg):
        global heating, tG
        state_topic_sensor = inputstr['sub_state_setpoint']
        if msg.topic == state_topic_sensor:
            heating['manualsetpoint'] = float(msg.payload)
            print 'obtained: {} {} at time: {} '.format(msg.topic, heating['manualsetpoint'], str(tG))

    @staticmethod
    def on_disconnect(client, userdata, rc):
        print "Disconnected from MQTT server with code: %s" % rc
        while rc != 0:
            RECONNECT_DELAY_SECS = 3
            time.sleep(RECONNECT_DELAY_SECS)
            print "Reconnecting..."
            try:
                rc = client.reconnect()
            except:
                print "failed to reconnect to MQTT server."
                pass

    def rundeamon(self):
        global heating, tG
        # mqtt settings
        self.mqttc = mqtt.Client(client_id="serverside_01", clean_session=False, userdata=self.inputstr,
                                 protocol="MQTTv31")
        self.mqttc.on_subscribe = self.on_subscribe
        self.mqttc.on_disconnect = self.on_disconnect
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_message = self.on_message

        self.Schedule = Schedule(self.local)
        schedule = self.Schedule.getjsonstruct()
        (heating, setpoint, tG, days) = self.Schedule.getheatingschedule(schedule)

        try:
            self.mqttc.connect(self.hostname, self.port, 60)
        except:
            print "failed to reconnect to MQTT server."
            pass
        t = 0
        lt = 0
        timeTenSec = 10.0
        fbSetpoint = 8  # fallbacksetpoint if update fails
        (setpoint, updatesetpoint, tG) = self.Schedule.update(setpoint, tG, heating, days, fbSetpoint)
        self.mqttupdate(setpoint, updatesetpoint, self.inputstr['sub_state_setpoint'], self.mqttc)

        while 1:
            self.mqttc.loop(0)
            # every 10 seconds
            if (t - lt) > timeTenSec:
                lt = t
                (setpoint, updatesetpoint, tG) = self.Schedule.update(setpoint, tG, heating, days, fbSetpoint)
                self.mqttupdate(setpoint, updatesetpoint, self.inputstr['sub_state_setpoint'], self.mqttc)
                if round(heating['manualsetpoint'], 4) != setpoint:
                    print 'attempting to set setpoint unless manual:  obtained: {} current setpoint: {} '.format(
                        heating['manualsetpoint'], str(float(setpoint)))
                    aStr = 'setpoints NOT syncronized'
                    self.mqttc.publish('outTopicAbrakadabra', aStr)
                    (setpoint, updatesetpoint, tG) = self.Schedule.update(setpoint, tG, heating, days, fbSetpoint)
                    self.mqttupdate(setpoint, updatesetpoint, self.inputstr['sub_state_setpoint'], self.mqttc)
                if round(heating['manualsetpoint'], 4) == round(setpoint, 4):
                    aStr = 'setpoints syncronized'
                    print '{}, server: {} local: {} at time {}'.format(str(aStr), heating['manualsetpoint'], str(float(setpoint)), tG)
                    self.mqttc.publish('outTopicAbrakadabra', aStr)

            time.sleep(1)
            t += 1


def main():
    local = 0 # runs schedule via REST api 2#runs via local sqlite 1-run via localhost
    hostname = "xx.xx.xx.xx" #ip or url
    port = 1883
    d = Deamon(hostname, port, local)
    d.inputstr['sub_state_temp'] = ".../temperature/degrees"
    d.inputstr['sub_state_setpoint'] = ".../settpunkt/degrees"

    d.rundeamon()


if __name__ == "__main__":
    main()
