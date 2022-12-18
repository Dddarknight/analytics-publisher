import datetime
import os
import motor.motor_asyncio


DB = 'clubs'


def get_client():
    return motor.motor_asyncio.AsyncIOMotorClient(
        host=os.getenv('HOST'), port=27017)


async def create_event(data):
    mongo_client = get_client()
    mongo_data = {
        'club_id': data['club_id'],
        'club': data['club'],
        'type': data['type'],
        'date_time': data['date_time'],
        'ip': data['ip']
    }
    mongo_client[DB].records.insert_one(mongo_data)
    return mongo_data


async def adapt_mongo_data(cursor):
    adapted_data = []
    for document in await cursor.to_list(length=100):
        document['_id'] = str(document['_id'])
        adapted_data.append(document)
    return adapted_data


async def get_events():
    mongo_client = get_client()
    cursor = mongo_client[DB].records.find({})
    events = await adapt_mongo_data(cursor)
    return events


async def get_events_for_period(period_in_minutes):
    mongo_client = get_client()
    end_time = datetime.datetime.utcnow()
    start_time = end_time - datetime.timedelta(minutes=period_in_minutes)
    cursor = mongo_client[DB].records.find({
        'date_time': {
            "$gte": start_time,
            "$lt": end_time
        }
    })
    events = await adapt_mongo_data(cursor)
    return events
