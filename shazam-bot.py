import logging as log
import json
from pathlib import Path
import os
import sys
import requests
from telegram import Update # python-telegram-bot
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv # python-dotenv
import hashlib


log.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=log.INFO
)

load_dotenv('./.env')

BOT_TOKEN = os.getenv('TELE_BOT_TOKEN')
BOT_USERNAME = os.getenv('BOT_USERNAME')
API_TOKEN = os.getenv('PUBLIC_API_TOKEN')


#! try catch decorator
def exception_handling(func):
    def wrapper_func(*args,**kwargs):
        try:
            func(*args,*kwargs)
        except Exception as e:
            log.error(f'{func.__name__} failed to execute. {e}')
            sys.exit()
    
    return wrapper_func


async def start_command_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = 'Hi, I am Shazam, I am here to serve you. Please Type /Help to look on the options'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

async def help_command_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = '''
        Type the option you prefer
        /password ==> To check the given password has been breached or not.😀
        /website ==> To check is the given domain has been hacked or not.
        /translator ==> Given Sentence will be translated to the specified language.
        /meaning ==> Will list the definition of the given word.
        /start ==> shazam will welcome you again. 
        /help ==> will list the above menu.
    '''
    await context.bot.send_message(chat_id=update.effective_chat, text=text)

def handle_message(text : str) -> str:
    message = text.lower()

    if 'hey' in message:
        return 'Hey 🖖 thanks for pinging me....'
    
    if 'how are you' in message:
        return 'I am fine 😊, I hope the same for you.. enjoy your day..'
    
    return 'unknown message'

async def unknow_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type : str = update.message.chat.type
    message_text : str = update.message.text

    # if the bot has been mentioned in group this block will react
    if message_type == 'group':
        # remove the bot name from the text
        if BOT_USERNAME in message_text:
            new_text : str = message_text.replace(BOT_USERNAME,'').strip()
            response : str = handle_message(new_text)
        else:
            return # We don't want the bot respond if it's not mentioned in the group
    else:
        response : str = handle_message(message_text)

    if 'unknown message' in response:
        await update.message.reply_text(f'I don\'t understand kinldy type /help in {BOT_USERNAME} to check the options')
    else:
        await update.message.reply_text(response)

# Log errors
async def bot_error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log.error(f'bot failed {update} caused error {context.error}')
    await update.message.reply_text(f'Sorry {update.effective_chat.first_name} request has been failed with Error {context.error} \n try to chat with bot after 2 mins...')


if __name__ == '__main__':

    # build the app
    log.info('Starting bot application...')
    app = ApplicationBuilder().token(BOT_TOKEN).build()

     # command
    app.add_handler(CommandHandler('start',start_command_bot))
    app.add_handler(CommandHandler('help',help_command_bot))

    # message handler
    app.add_handler(MessageHandler(filters.TEXT,unknow_message_handler))

    # error handler
    app.add_error_handler(bot_error_handler)


    log.info('Polling....')
    app.run_polling()


