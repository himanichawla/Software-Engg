import time, socket, sys, mraa
from datetime import datetime as dt
import paho.mqtt.client as paho
import signal

traveling = False
carID = ""
carLightID = -1

if len(sys.argv) != 3:
	print "Car ID and Light ID required to run a car."
	sys.exit(0)
else:
	carID = sys.argv[1]
	carLightID = int(sys.argv[2])

messageHeader = "CAR:" + carID + ":"
# Deal with control-c
def control_c_handler(signum, frame):
	print('saw control-c')
	mqtt_client.disconnect()
	mqtt_client.loop_stop()  # waits until DISCONNECT message is sent out
	led.write(1)
	print "Now I am done."
	sys.exit(0)

signal.signal(signal.SIGINT, control_c_handler)

led = mraa.Gpio(carLightID +2)
led.dir(mraa.DIR_OUT)
led.write(1)

def on_connect(client, userdata, flags, rc):
	print('connected')
        mqtt_client.publish(mqtt_topic, messageHeader + "RequestPickup")

# The callback for when a PUBLISH message is received from the server that matches any of your topics.
# However, see note below about message_callback_add.
def on_message(client, userdata, msg):
	global traveling
	# ignore all messages if traveling
	if not traveling:
		if "PickupReady" in msg.payload:
			mqtt_client.publish(mqtt_topic, messageHeader + "RequestPickup")
		if "PickupGranted" in msg.payload:
			if msg.payload.split(":")[1] == carID:
				traveling = True
				led.write(0)
				mqtt_client.publish(mqtt_topic, messageHeader + "Depart")
	# Here is where you write to file and unsubscribe

def on_disconnect(client, userdata, rc):
	print("Disconnected in a normal way")


# Instantiate the MQTT client
mqtt_client = paho.Client()

# set up handlers
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_disconnect = on_disconnect

mqtt_topic = 'cis650/winterfell'  # don't change this or you will screw it up for others

# See https://pypi.python.org/pypi/paho-mqtt#option-functions.
mqtt_client.will_set(mqtt_topic, '______________Will of Car ' + carID + '_________________\n\n', 0, False)

broker = 'sansa.cs.uoregon.edu'  # Boyana's server
mqtt_client.connect(broker, '1883')
mqtt_client.subscribe('cis650/winterfell')
mqtt_client.loop_start()

while True:
	if traveling:
		time.sleep(20)
		traveling = False
		led.write(1)
		mqtt_client.publish(mqtt_topic, messageHeader + "Arrived")
