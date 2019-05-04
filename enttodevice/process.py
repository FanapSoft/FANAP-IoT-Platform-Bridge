from enttodevice import app_celery
import environs
import paho.mqtt.client
import json


def build_topic(deviceid):
    return '/{}/p2d'.format(deviceid)


env = environs.Env()
with env.prefixed("OP_MQTT_"):
    _config = dict(
        mqtt = env("URL","localhost"),
        mqtt_usr = env("USR",""),
        mqtt_pass = env("PASS",""),
        mqtt_port = int(env("PORT",1883, 'int')),
    )

_use_id_translate = env("ENABLE_ID_TRANSLATE",False, 'bool')
_use_num_translate  = env("ENABLE_NUM_FIELD_TRANSLATE",False, 'bool')
_use_case_translate  = env("ENABLE_CASE_FIELD_TRANSLATE",False, 'bool')

if _use_id_translate:
    from idtranslate import translate_to_open_id

if _use_num_translate or _use_case_translate:
    from idtranslate import translate_to_upper, translate_to_num


def conv_msg_ent2dev(msg):
    l1 = json.loads(msg)
    l2 = json.loads(l1['content'])
    l3 = json.loads(l2)
    timestamp = int(l3['timeStamp'])
    data = json.loads(l3['data'])


    if _use_case_translate:
        data = translate_to_upper(data)

    if _use_num_translate:
        data = translate_to_num(data)

    ret_dict = dict(TimeStamp=int(timestamp), data=[data])
    ret = json.dumps(ret_dict)
    return ret



def create_mqtt_client():
    client = paho.mqtt.client.Client()

    if _config['mqtt_usr']:
        client.username_pw_set(_config['mqtt_usr'], _config['mqtt_pass'])

    client.connect(_config['mqtt'], _config['mqtt_port'], 60)    
    return client



def publish_to_mqtt(deviceid, msg):
    topic = build_topic(deviceid)
    client = create_mqtt_client()
    client.publish(topic, msg)
    client.disconnect()



@app_celery.task
def sendtodev(deviceid, msg):
    if _use_id_translate:
        deviceid = translate_to_open_id(deviceid)
        
    m = conv_msg_ent2dev(msg)
    publish_to_mqtt(deviceid, m)
    return 0
