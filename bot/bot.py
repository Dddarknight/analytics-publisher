import os
import sys
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from dotenv import load_dotenv
from asgiref.sync import async_to_sync

from data_receiver import export_dataset_to_bot, export_dynamics_to_bot
from api_football import get_pl_teams


load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')


def start(update, context):
    keyboard = [[
        InlineKeyboardButton(
            'Get dynamics',
            callback_data='dynamics'),
        InlineKeyboardButton(
            'Get data set',
            callback_data='dataset')
    ], [InlineKeyboardButton('Get PL', callback_data='pl')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def button(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f"Selected option: {query.data}")
    id = query.message.chat.id
    if query.data == 'dynamics':
        async_to_sync(export_dynamics_to_bot)(update, context, id)
    elif query.data == 'dataset':
        async_to_sync(export_dataset_to_bot)(update, context, id)
    elif query.data == 'pl':
        teams = async_to_sync(get_pl_teams)()
        query.edit_message_text(text='\n'.join(teams))


def error(update, context):
    sys.stderr.write(f"ERROR: {context.error} caused by {update}")
    pass


def main():
    updater = Updater(API_TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
