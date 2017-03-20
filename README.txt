The simple code can be run as a simple deamon, to keep track of a weekly setpoint schedule (for example for controlling a heater), as described in a json structure of general size. The deamon checks for changes to the struct defined in a time interval. The shcedule can be stored externally (or internally in a simlpe sqlite table). The current setpoint is compared to the schedule and updated accordingly (over MQTT). 

main file is deamon.py

This is only a development script.
