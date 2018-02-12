import time, socket, sys
from datetime import datetime as dt
import paho.mqtt.client as paho
import paho.mqtt.subscribe as subscribe
import signal

MY_NAME = 'Himani' # change to your name

# Deal with control-c
def control_c_handler(signum, frame):
	print('saw control-c')
	mqtt_client.disconnect()
	mqtt_client.loop_stop()  # waits until DISCONNECT message is sent out
	print "Now I am done."
	sys.exit(0)

signal.signal(signal.SIGINT, control_c_handler)

# Get your IP address
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip_addr = str(s.getsockname()[0])
#print('IP address: {}'.format(ip_addr))
s.close()

#def on_connect(client, userdata, flags, rc):
	#print('connected')
stopSending = False
# The callback for when a PUBLISH message is received from the server that matches any of your topics.
# However, see note below about message_callback_add.
def on_message(client, userdata, msg):
        global stopSending
	if msg.payload == "FULL":
		stopSending = True
	if msg.payload == "EMPTY":
		stopSending = False
	print(msg.payload)




	# Here is where you write to file and unsubscribe

# You can also add specific callbacks that match specific topics.
# See message_callback_add at https://pypi.python.org/pypi/paho-mqtt#callbacks.
# When you have add ins, then the on_message handler just deals with topics
# you have *not* written an add in for. You can just use the single on_message
# handler for this problem.
#mqttc = paho.Client()
#mqttc.message_callback_add("cis650/winterfell", on_message)



def on_disconnect(client, userdata, rc):
	print("Disconnected in a normal way")
	#graceful so won't send will

#def on_log(client, userdata, level, buf):
	#print("log: {}".format(buf)) # only semi-useful IMHO

# Instantiate the MQTT client
mqtt_client = paho.Client()

# set up handlers
#mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_disconnect = on_disconnect
#smqtt_client.on_log = on_log

mqtt_topic = 'cis650/winterfell'  # don't change this or you will screw it up for others

# See https://pypi.python.org/pypi/paho-mqtt#option-functions.
mqtt_client.will_set(mqtt_topic, '______________Will of winterfell _________________\n\n', 0, False)

broker = 'sansa.cs.uoregon.edu'  # Boyana's server
# Public brokers: https://github.com/mqtt/mqtt.github.io/wiki/public_brokers, e.g., 'test.mosquitto.org'

mqtt_client.connect(broker, '1883')

# You can subscribe to more than one topic: https://pypi.python.org/pypi/paho-mqtt#subscribe-unsubscribe.
# If you do list more than one topic, consdier using message_callback_add for each topic as described above.
# For below, wild-card should do it.
mqtt_client.subscribe("cis650/winterfell") #subscribe to all students in class

mqtt_client.loop_start()  # just in case - starts a loop that listens for incoming data and keeps client alive

while True:
	if not stopSending:
		timestamp = dt.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f')
		mqtt_message = "TERMINAL:Passenger arrives"  # don't change this or you will screw it up for others
		mqtt_client.publish(mqtt_topic, mqtt_message)  # by doing this publish, we should keep client alive
		time.sleep(2)

# I have the loop_stop() in the control_c_handler above. A bit kludgey.
