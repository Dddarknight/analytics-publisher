import aiohttp
import os
from dotenv import load_dotenv


load_dotenv()


HOST = os.getenv('HOST')
API_PORT = os.getenv('API_PORT')


async def post_task(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return data


async def get_task_info(task_id):
    url = f'http://{HOST}:{API_PORT}/tasks/{task_id}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return data


async def get_result(task_id):
    url = f'http://{HOST}:{API_PORT}/result/{task_id}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            return response.status, data
