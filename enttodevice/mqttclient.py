import paho.mqtt.client
import environs
from process import sendtodev


ENT_TOPIC = 'out/+/p2d'

env = environs.Env()
with env.prefixed("ENT_MQTT_"):
    _ent_mqtt_cfg = dict(
        ent_mqtt = env("URL","localhost"),
        ent_mqtt_usr = env("USR",""),
        ent_mqtt_pass = env("PASS",""),
        ent_mqtt_port = int(env("PORT",1883, 'int')),
    )

_config = _ent_mqtt_cfg


def get_deviceid_from_ent_topic(topic):
    l  = topic.split('/')
    if len(l)==3:
        return l[1]
    return None

def decode_message(message):
    if not isinstance(message, str):
        try:
            message = message.decode('utf-8')
        except UnicodeDecodeError:
            # ToDo: how to packets with encoding issue
            return False
    return message

def on_connect(client, userdata, flags, rc):
    client.subscribe(ENT_TOPIC)


def on_message(client, userdata, msg):
    m = decode_message(msg.payload)

    if not m:
        print("Error: Message is not a valid UTF8 ", msg.payload, msg.topic)
        return

    deviceid = get_deviceid_from_ent_topic(msg.topic)

    if not deviceid:
        print("Error: Unable to get device-id from topic ", msg.topic, msg.payload)
        return
    
    # ToDo Send code to the queue
    sendtodev.delay(deviceid, m)


def create_start_client():
    client = paho.mqtt.client.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    if _config['ent_mqtt_usr']:
        client.username_pw_set(_config['ent_mqtt_usr'], _config['ent_mqtt_pass'])

    client.connect(_config['ent_mqtt'], _config['ent_mqtt_port'], 60)
    client.loop_start()
    
    return client



