import time, socket, sys
from datetime import datetime as dt
import paho.mqtt.client as paho
import signal

# Deal with control-c
def control_c_handler(signum, frame):
	print('saw control-c')
	mqtt_client.disconnect()
	mqtt_client.loop_stop()  # waits until DISCONNECT message is sent out
	print "Now I am done."
	sys.exit(0)

signal.signal(signal.SIGINT, control_c_handler)

def on_connect(client, userdata, flags, rc):
	print('connected')

def on_message(client, userdata, msg):
	print(msg.topic)
	print(msg.payload)

def on_disconnect(client, userdata, rc):
	print("Disconnected in a normal way")
	#graceful so won't send will

# Instantiate the MQTT client
mqtt_client = paho.Client()

# set up handlers
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_disconnect = on_disconnect

mqtt_topic = 'cis650/winterfell'  # don't change this or you will screw it up for others
mqtt_client.will_set(mqtt_topic, '______________Will of The Winterfell Monitor _________________\n\n', 0, False)
broker = 'sansa.cs.uoregon.edu'  # Boyana's server
mqtt_client.connect(broker, '1883')
mqtt_client.subscribe(mqtt_topic) #subscribe to all students in class
mqtt_client.loop_start()  # just in case - starts a loop that listens for incoming data and keeps client alive

# just loop forever (or until ctrl-c)
while True:
	1==1
