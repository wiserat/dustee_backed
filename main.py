import firebase_admin
import requests
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()



all_users = db.collection('example').get()
all_sensors = []

for user_raw in all_users:
    user = user_raw.to_dict()
    sensors = user.get('sensors')
    
    for sensor in sensors:
        if sensor not in all_sensors:
            all_sensors.append(sensor)


all_sensors_json = requests.get('https://data.sensor.community/static/v1/data.json').json()
for item_json in all_sensors_json:
    item = item_json['sensor']['id']
    if item in all_sensors:
        existing_sensor = db.collection('sensors').where('id', '==', item).get()
        for existing_sensor_raw in existing_sensor:
            existing_sensor = existing_sensor_raw.to_dict()
            
        if existing_sensor == []:
            db.collection('sensors').document().set({
                'id': item,
                'country': item_json['location']['country']
            })
            
        temporary = db.collection('sensors').where('id', '==', item).get()
        for temporary_raw in temporary:
            document_id = temporary_raw.id
            
        for value in item_json['sensordatavalues']:
            
            if existing_sensor == None:
                    
                db.collection('sensors').document(document_id).set({
                    'values.' + value['value_type']: value['value']
                }, merge=True)
                
            else:
                db.collection('sensors').document(document_id).update({
                    'values.' + value['value_type']: value['value']
                })
        

all_sensors_delete = db.collection('sensors').get()
for sensor_delete_raw in all_sensors_delete:
    sensor_delete = sensor_delete_raw.to_dict()
    if sensor_delete['id'] not in all_sensors:
        db.collection('sensors').document(sensor_delete_raw.id).delete()