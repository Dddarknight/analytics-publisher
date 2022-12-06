import aiohttp
import os
from dotenv import load_dotenv


load_dotenv()

HOST = os.getenv('HOST')
API_PORT = os.getenv('API_PORT')
PERIOD = 60
URL_DATASET = f'http://{HOST}:{API_PORT}/file-dataset/{PERIOD}'
URL_DYNAMICS = f'http://{HOST}:{API_PORT}/file-dynamics/{PERIOD}'


async def export_dataset_to_bot(bot, context, chat_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(
                URL_DATASET) as response:
            data = await response.read()
            context.bot.send_document(chat_id, data)


async def export_dynamics_to_bot(bot, context, chat_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(
                URL_DYNAMICS) as response:
            data = await response.read()
            context.bot.send_document(chat_id, data)
