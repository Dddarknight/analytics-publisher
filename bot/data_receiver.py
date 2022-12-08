import aiohttp
from dotenv import load_dotenv


load_dotenv()


async def export_data_to_bot(bot, context, chat_id, url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            context.bot.send_document(chat_id, data)
