from pymongo import MongoClient
import environs

env = environs.Env()
_db_uri = env("MONGODB_URI","")

_DB_NAME = 'platbridge'
_COLLECTION_NAME = 'deviceids'
client = MongoClient(_db_uri or None)
collection = client[_DB_NAME]
db = collection[_COLLECTION_NAME]


## Add Example Data!
example_data = dict(open='OPEN-PLAT-DEVICE-ID',ent='ENT-PLAT-DEVICE-ID') 

if not db.find_one(example_data):
    db.insert_one(example_data)



def translate_to_ent_id(open_id):
    return _translate(open_id, is_open_id=True)


def translate_to_open_id(ent_id):
    return _translate(ent_id, is_open_id=False)



def _translate(dev_id, is_open_id):
    if is_open_id:
        q= dict(open=dev_id)
    else:
        q= dict(ent=dev_id)
    
    ret = db.find_one(q)

    if not ret:
        return dev_id

    if is_open_id:
        return ret['ent']
    else:
        return ret['open']
    
