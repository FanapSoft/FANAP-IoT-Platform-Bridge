from pymongo import MongoClient
import environs

env = environs.Env()
_db_uri = env("MONGODB_URI","")

_DB_NAME = 'platbridge'
_COLLECTION_NAME = 'deviceids'
_NUM_FIELDS= 'fields'
client = MongoClient(_db_uri or None)
collection = client[_DB_NAME]
db = collection[_COLLECTION_NAME]
db_num = collection[_NUM_FIELDS]

## Add Example Data!
example_data = dict(open='OPEN-PLAT-DEVICE-ID',ent='ENT-PLAT-DEVICE-ID') 

if not db.find_one(example_data):
    db.insert_one(example_data)


n_help = dict(help='Define a document with {"nums":[LIST OF NUM FIELDS]} and a document with {"case":[LIST OF FIELDS FOR CASE CHANGE]}')
if not db_num.find_one(n_help):
    db_num.insert_one(n_help)



def translate_to_num(field_dict):
    return translate_map(field_dict, int,'nums')

def translate_to_str(field_dict):
    return translate_map(field_dict, str,'nums')

def translate_to_upper(field_dict):
    return translate_map(field_dict, lambda x: x.upper(), 'case')

def translate_to_lower(field_dict):
    return translate_map(field_dict, lambda x: x.lower(), 'case')

def translate_map(field_dict, func, db_key):
    # Get field list
    r = db_num.find_one({db_key:{'$exists':True}})
    if not r:
        return field_dict

    for field_name in r[db_key]:
        if field_name in field_dict:
            field_dict[field_name] = func(field_dict[field_name])

    return field_dict


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
    
