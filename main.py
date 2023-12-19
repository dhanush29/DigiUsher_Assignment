from fastapi import FastAPI
from pymongo import MongoClient
from dotenv import dotenv_values
from models.model import Item
from datetime import datetime

app = FastAPI()
config = dotenv_values(".env")

client = MongoClient(config['ATLAS_URI'])
print(config['ATLAS_URI'])
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client.metric_db
collection_name = db['metric_collection']

@app.post('/ingest')
async def root(item: Item):
    curr_dt = datetime.now()
    item_ts = {
        'ram_consumed': item.ram_consumed,
        'cpu': item.cpu, 
        'disk_usage_percent': item.disk_usage_percent,
        'time_stamp' : int(round(curr_dt.timestamp()))
    }
    collection_name.insert_one(item_ts)
    return {"message" : 'data saved!'}


@app.get('/report')
async def root():
    curr_dt = datetime.now()
    curr_ts = int(round(curr_dt.timestamp()))
    day_ts = curr_ts - 24*60*60
    month_ts = curr_ts - 30*24*60*60

    day_list = collection_name.find({"time_stamp": {"$gt": day_ts}})
    month_list = collection_name.find({"time_stamp": {"$gt": month_ts}})
    
    day_avg = {
        'ram_consumed': 0,
        'cpu': 0, 
        'disk_usage_percent': 0,
    }
    month_avg = {
        'ram_consumed': 0,
        'cpu': 0, 
        'disk_usage_percent': 0,
    }
    
    count = 0
    for i in month_list:
        count += 1
        month_avg['ram_consumed'] += i['ram_consumed']
        month_avg['cpu'] += i['cpu']
        month_avg['disk_usage_percent'] += i['disk_usage_percent']
    
    if(count == 0):
        return { 'day': 'no data recorded today', 'month' : 'no data recorded this month'}
    
    month_avg['ram_consumed'] = month_avg['ram_consumed']/count
    month_avg['cpu'] = month_avg['cpu']/count
    month_avg['disk_usage_percent'] = month_avg['disk_usage_percent']/count
    
    count = 0 
    for i in day_list:
        count += 1
        day_avg['ram_consumed'] += i['ram_consumed']
        day_avg['cpu'] += i['cpu']
        day_avg['disk_usage_percent'] += i['disk_usage_percent']

    if(count == 0):
        return { 'day': 'no data recorded today', 'month' : month_avg}

    day_avg['ram_consumed'] = day_avg['ram_consumed']/count
    day_avg['cpu'] = day_avg['cpu']/count
    day_avg['disk_usage_percent'] = day_avg['disk_usage_percent']/count
    
    return { 'day': day_avg, 'month' : month_avg}

