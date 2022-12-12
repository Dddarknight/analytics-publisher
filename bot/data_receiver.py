import aiohttp
import os
from dotenv import load_dotenv


load_dotenv()


HOST = os.getenv('HOST')
API_PORT = os.getenv('API_PORT')

NO_DATA = "Requested data don't exist"


async def push_task_to_api(bot, context, chat_id, url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            context.bot.send_message(chat_id, data)


async def get_celery_info(task_id):
    url = f'http://{HOST}:{API_PORT}/tasks/{task_id}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return data['status']


async def get_result(bot, context, chat_id, task_id):
    url = f'http://{HOST}:{API_PORT}/tasks/{task_id}/result'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            if response.status == 200:
                context.bot.send_document(chat_id, data)
            else:
                context.bot.send_message(chat_id, NO_DATA)
