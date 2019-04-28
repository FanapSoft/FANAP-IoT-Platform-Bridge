from devicetoent import app_celery
import environs
import paho.mqtt.client
import json


ENT_TOPIC = 'as/ingate'


env = environs.Env()
with env.prefixed("ENT_MQTT_"):
    _config = dict(
        mqtt = env("URL","localhost"),
        mqtt_usr = env("USR",""),
        mqtt_pass = env("PASS",""),
        mqtt_port = int(env("PORT",1883, 'int')),
    )

def conv_msg_dev2open(msg, ent_devid):
    m = json.loads(msg)
    ret = dict(
        timeStamp = m['TimeStamp'],
        data = m['data'],
        deviceId = ent_devid
    )
    return json.dumps(ret)



def create_mqtt_client():
    client = paho.mqtt.client.Client()

    if _config['mqtt_usr']:
        client.username_pw_set(_config['mqtt_usr'], _config['mqtt_pass'])

    client.connect(_config['mqtt'], _config['mqtt_port'], 60)
    return client



def publish_to_mqtt(msg):
    topic = ENT_TOPIC
    client = create_mqtt_client()
    client.publish(topic, msg)
    print("Send to {} {} {}".format(_config['mqtt'], topic , msg))
    client.disconnect()



@app_celery.task
def sendtoplat(deviceid, msg):
    m = conv_msg_dev2open(msg, deviceid)
    publish_to_mqtt(m)
    return 0
