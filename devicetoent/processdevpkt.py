from devicetoent import app_celery
import environs
import paho.mqtt.client
import json

env = environs.Env()
with env.prefixed("ENT_MQTT_"):
    _config = dict(
        mqtt = env("URL","localhost"),
        mqtt_usr = env("USR",""),
        mqtt_pass = env("PASS",""),
        mqtt_port = int(env("PORT",1883, 'int')),
    )
    ENT_TOPIC = env("INPUT_TOPIC", 'input/iot')

_use_id_translate = env("ENABLE_ID_TRANSLATE",False, 'bool')

_use_num_translate  = env("ENABLE_NUM_FIELD_TRANSLATE",False, 'bool')
_use_case_translate  = env("ENABLE_CASE_FIELD_TRANSLATE",False, 'bool')

_mqtt_client_id = env("ENT_MQTT_CLIENT_ID","")

if _use_id_translate:
    from idtranslate import translate_to_ent_id

if _use_num_translate or _use_case_translate:
    from idtranslate import translate_to_lower, translate_to_str

def conv_msg_dev2open(msg, ent_devid):

    m = json.loads(msg)

    data = m['data'][0]

    if _use_case_translate:
        data = translate_to_lower(data)

    if _use_num_translate:
        
        data = translate_to_str(data)
        

    ret = dict(
        timeStamp = str(m['TimeStamp']),
        data = [data],
        deviceId = ent_devid
    )
    return json.dumps(ret)



def create_mqtt_client():
    if _mqtt_client_id:
        client = paho.mqtt.client.Client(client_id=_mqtt_client_id)
    else:
        client = paho.mqtt.client.Client()

    if _config['mqtt_usr']:
        client.username_pw_set(_config['mqtt_usr'], _config['mqtt_pass'])

    client.connect(_config['mqtt'], _config['mqtt_port'], 60)
    return client



def publish_to_mqtt(msg):
    # ToDo: Use publish.single from paho library
    topic = ENT_TOPIC
    client = create_mqtt_client()
    client.publish(topic, msg)
    print("Send to {} {} {}".format(_config['mqtt'], topic , msg))
    client.disconnect()



@app_celery.task
def sendtoplat(deviceid, msg):
    if _use_id_translate:
        deviceid = translate_to_ent_id(deviceid)
    m = conv_msg_dev2open(msg, deviceid)
    publish_to_mqtt(m)
    return 0
