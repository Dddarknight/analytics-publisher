import os
import sys
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, filters
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from dotenv import load_dotenv
from asgiref.sync import async_to_sync

from api_data_receiver import post_task, get_task_info, get_result
from api_football import get_premier_league_teams
from database import init_db
from logger import logger


load_dotenv()

API_TOKEN = os.getenv('TG_API_TOKEN')

PERIOD = 60

HOST = os.getenv('HOST')

API_PORT = os.getenv('API_PORT')

URL = f'http://{HOST}:{API_PORT}/tasks/'

NO_DATA = "Requested data don't exist"

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
        [InlineKeyboardButton(
            'Get Premier League clubs 2022', callback_data='pl')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def handle_button(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f"Selected option: {query.data}")
    chat_id = query.message.chat.id
    if query.data in ['dynamics', 'bars', 'displot']:
        cache_db.set('current_task_type', query.data)
        url = f'{URL}{query.data}/{PERIOD}'
        data = async_to_sync(post_task)(url)
        context.bot.send_message(chat_id, data)
    elif query.data == 'pl':
        teams = async_to_sync(get_premier_league_teams)()
        query.edit_message_text(text='\n'.join(teams))


def is_command(data):
    return data.startswith('/')


def handle_user_input(update, context):
    user_input = update.message.text
    if not is_command(user_input):
        cache_db.set('current_id', user_input)
    update.message.reply_text(
        async_to_sync(get_task_info)(user_input)['status'])


def handle_error(update, context):
    sys.stderr.write(f"ERROR: {context.error} caused by {update}")
    pass


def handle_result(update, context):
    task_id = cache_db.get('current_id').decode('utf-8')
    logger.info(f'task {task_id}')
    chat_id = update.message.chat.id
    status, data = async_to_sync(get_result)(task_id)
    if status == 200:
        context.bot.send_document(chat_id, data)
    else:
        context.bot.send_message(chat_id, NO_DATA)
    cache_db.set('current_id', None)
    cache_db.set('current_task_type', None)


def main():
    updater = Updater(API_TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(
        CommandHandler("result", handle_result))
    updater.dispatcher.add_handler(CallbackQueryHandler(handle_button))
    updater.dispatcher.add_handler(
        MessageHandler(filters.Filters.text, handle_user_input))
    updater.dispatcher.add_error_handler(handle_error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
