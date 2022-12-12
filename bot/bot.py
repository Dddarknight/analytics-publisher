import os
import sys
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, filters
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from dotenv import load_dotenv
from asgiref.sync import async_to_sync

from data_receiver import push_task_to_api, get_celery_info, get_result
from api_football import get_pl_teams
from database import init_db
from logger import logger


load_dotenv()

API_TOKEN = os.getenv('TG_API_TOKEN')

PERIOD = 60
HOST = os.getenv('HOST')
API_PORT = os.getenv('API_PORT')

URL_DATASET = f'http://{HOST}:{API_PORT}/file-dataset/{PERIOD}'
URL_DYNAMICS = f'http://{HOST}:{API_PORT}/file-dynamics/{PERIOD}'
URL_DISPLOT = f'http://{HOST}:{API_PORT}/file-displot/{PERIOD}'


cache_db = init_db()


def start(update, context):
    keyboard = [
        [
            InlineKeyboardButton(
                'Get dynamics',
                callback_data='dynamics'),
            InlineKeyboardButton(
                'Get data set',
                callback_data='dataset')
        ],
        [InlineKeyboardButton('Get displot', callback_data='displot')],
        [InlineKeyboardButton('Get PL clubs 2022', callback_data='pl')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def button(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f"Selected option: {query.data}")
    id = query.message.chat.id
    if query.data == 'dynamics':
        cache_db.set('current_task_type', 'dynamics')
        async_to_sync(
            push_task_to_api)(update, context, id, URL_DYNAMICS)
    elif query.data == 'dataset':
        cache_db.set('current_task_type', 'dataset')
        async_to_sync(push_task_to_api)(update, context, id, URL_DATASET)
    elif query.data == 'displot':
        cache_db.set('current_task_type', 'displot')
        async_to_sync(push_task_to_api)(update, context, id, URL_DISPLOT)
    elif query.data == 'pl':
        teams = async_to_sync(get_pl_teams)()
        query.edit_message_text(text='\n'.join(teams))


def reply(update, context):
    user_input = update.message.text
    if not user_input.startswith('/'):
        cache_db.set('current_id', user_input)
    update.message.reply_text(
        async_to_sync(get_celery_info)(user_input))


def error(update, context):
    sys.stderr.write(f"ERROR: {context.error} caused by {update}")
    pass


def result(update, context):
    task_id = cache_db.get('current_id').decode('utf-8')
    logger.info(f'task {task_id}')
    chat_id = update.message.chat.id
    async_to_sync(get_result)(update, context, chat_id, task_id)
    cache_db.set('current_id', None)
    cache_db.set('current_task_type', None)


def main():
    updater = Updater(API_TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("result", result))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(MessageHandler(filters.Filters.text, reply))
    updater.dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
