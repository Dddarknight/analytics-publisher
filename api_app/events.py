import datetime
import os
import motor.motor_asyncio


DB = 'clubs'


def get_client():
    return motor.motor_asyncio.AsyncIOMotorClient(
        host=os.getenv('HOST'), port=27017)


async def make_event(data):
    mongo_client = get_client()
    mongo_client[DB].records.insert_one({
        'club_id': data['club_id'],
        'club': data['club'],
        'type': data['type'],
        'date_time': data['date_time'],
        'ip': data['ip']})
    return


async def get_statistics():
    mongo_client = get_client()
    cursor = mongo_client[DB].records.find({})
    statistics = []
    for document in await cursor.to_list(length=100):
        document['_id'] = str(document['_id'])
        statistics.append(document)
    return statistics


async def get_filtered_statistics(period_in_minutes):
    mongo_client = get_client()
    end_time = datetime.datetime.utcnow()
    start_time = end_time - datetime.timedelta(minutes=period_in_minutes)
    cursor = mongo_client[DB].records.find({
        'date_time': {
            "$gte": start_time,
            "$lt": end_time
        }
    })
    statistics = []
    for document in await cursor.to_list(length=100):
        document['_id'] = str(document['_id'])
        statistics.append(document)
    return statistics
