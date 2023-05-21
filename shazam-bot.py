import logging as log
import json
from pathlib import Path
import os
import sys
import requests
from telegram import Update # python-telegram-bot
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from dotenv import load_dotenv # python-dotenv
import hashlib

log.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=log.INFO
)

load_dotenv(dotenv_path='./.env')

tele_bot_token = os.getenv('TELE_BOT_TOKEN')
public_api_token = os.getenv('PUBLIC_API_TOKEN')

def error_handler(func):
    def wrapper_func(*args,**kwargs):
        try:
            func(*args,**kwargs)
        except Exception as e:
            log.error(f'{func.__name__} failed to execute {e}')
    return wrapper_func 


@error_handler
async def start_bot(update : Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hi! I am Shazam, I am here to serve your query. please type /help")

@error_handler
async def help_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = '''
        Type the option you prefer
        /password breached ==> To check the given password has been breached or not.
        /website breached ==> To check is the given domain has been hacked or not.
        /translator ==> Given Sentence will be translated to the specified language.
        /meaning ==> Will list the definition of the given word.
        /start ==> shazam will welcome you again. 
        /help ==> will list the above menu.
    '''
    await context.bot.send_message(chat_id=update.effective_chat.id,text=text)

@error_handler
def hasing_text(password : str):
    hashed_object = hashlib.sha1(password.encode('utf-8'))
    hashed_string = hashed_object.hexdigest().upper(), 
    return hashed_string

@error_handler
def get_password_check(password_text):
    pass

@error_handler
def password_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


if __name__ == '__main__':
    application = ApplicationBuilder().token(tele_bot_token).build()

    start_builder = CommandHandler('start',start_bot)
    application.add_handler(start_builder)
    application.run_polling()