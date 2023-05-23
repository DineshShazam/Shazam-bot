import logging as log
import os
import telebot #pip install pyTelegramBotAPI
from telebot import apihelper
import os
from dotenv import load_dotenv # python-dotenv
import utils
import re

log.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=log.INFO
)

load_dotenv('./.env')

BOT_TOKEN = os.getenv('TELE_BOT_TOKEN')


#* loading bot 
log.info('Bot started')
bot = telebot.TeleBot(BOT_TOKEN)

#* force recreation after 5 minutes without any activity.
apihelper.SESSION_TIME_TO_LIVE = 5 * 60

#* responds to the initial message
@bot.message_handler(commands=['start','hello'])
def start_command_bot(message):
    print(message.chat.type)
    text = f'Hi {message.from_user.first_name}, I am Shazam, I am here to serve you. Please Type /help to look on the options'
    bot.reply_to(message, text)


@bot.message_handler(commands=['help'])
def help_command_bot(message):
    text = '''
        Type the option you prefer
        /horoscope ==> To check on your horoscope. 
        /password ==> To check the given password has been breached or not.
        /website ==> To check is the given domain has been hacked or not.
        /translator ==> Given Sentence will be translated to the specified language.
        /meaning ==> Will list the definition of the given word.
        /start ==> shazam will welcome you again. 
        /help ==> will list the above menu.
    '''
    bot.send_message(message.chat.id, text)

#* HOROSCOPE 
# this function ask the question which sign needed from the list
@bot.message_handler(commands=['horoscope'])
def get_horoscope_sign_bot(message):
     text = "What's your zodiac sign?\nChoose one: *Aries*, *Taurus*, *Gemini*, *Cancer,* *Leo*, *Virgo*, *Libra*, *Scorpio*, *Sagittarius*, *Capricorn*, *Aquarius*, and *Pisces*."
     sent_msg = bot.send_message(message.chat.id,text, parse_mode='Markdown')
     # triggers the next handler 
     bot.register_next_step_handler(sent_msg,get_day_handler_bot)

# this function will check the given sign is valid or not 
# this function will ask for the day that need to be checked
def get_day_handler_bot(message):
    zodiac_list = ['Aries','Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    zodiac_sign = message.text

    # check the zodiac sign is valid or not 
    zodiac_check = [var for var in zodiac_list if zodiac_sign.upper() in var.upper()]
    
    if not zodiac_check:
        text = f'Invalid Option Selected {zodiac_sign}, please type /horoscope to check again'
        bot.reply_to(message, text)

    text = "What day do you want to know?\nChoose one: *TODAY*, *TOMORROW*, *YESTERDAY*, or a date in format YYYY-MM-DD."
    sent_msg = bot.send_message(message.chat.id,text)
    bot.register_next_step_handler(sent_msg,fetch_horoscope_data,zodiac_sign)

def fetch_horoscope_data(message,sign: str):
    day = message.text
    # if the day variable starts with number format check is the date valid or not
    if re.match(r'^\d', day):
       value = utils.is_valid_date(day)
       if not value: bot.send_message(message.chat.id, "Date format is invalid it should be YYY-MM-DD!, please Type /horoscope to check again")
    else:
        if day.upper() not in ['TODAY', 'TOMORROW', 'YESTERDAY']:
            bot.send_message(message.chat.id, "Invalid Option selected should be 'TODAY', 'TOMORROW', 'YESTERDAY'!, please Type /horoscope to check again")
    
    json_data = utils.get_horoscope_data(sign,day)
    if not json_data : bot.send_message(message.chat.id, "Horoscope API is not working kinldy type /help and check on other options.."); return
    data = json_data["data"]
    horoscope_message = f'*Horoscope:* \n {data["horoscope_data"]} \n*Sign:* \n{sign} \n*Day:* \n{data["date"]}'
    bot.send_message(message.chat.id, "Here's your horoscope!")
    bot.send_message(message.chat.id, horoscope_message, parse_mode="Markdown")
    bot.send_message(message.chat.id, f"Type */help* to go to the menu",parse_mode='Markdown')

#* PASSWORD BREACH CHECK
@bot.message_handler(commands=['password'])
def password_command_bot(message):
    text = f'Type the password which you want to check is it breached or not !'
    msg = bot.send_message(message.chat.id,text)
    bot.register_next_step_handler(msg, get_password_breach_count)

def get_password_breach_count(message):
    password_text = message.text
    hashed_string = utils.hashing_text(password_text)
    hashed_prefix,hashed_suffix = hashed_string[:5], hashed_string[5:]
    
    response = utils.get_password_breach_data(hashed_prefix)
    if not response : bot.send_message(message.chat.id, "Password API is not working kinldy type /help and check on other options.."); return
    
    count = utils.password_breach_count(response,hashed_suffix)

    if count:
        bot.send_message(message.chat.id, f"*Password:* '{password_text}' has been breached *{count}* times",parse_mode='Markdown')
        bot.send_message(message.chat.id, f"Click 👉 */help* to go to the menu or Click 👉 */password* to check again",parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, f"*Password:* '{password_text}' has never been breached, Good To Go 👍",parse_mode='Markdown')
        bot.send_message(message.chat.id, f"Click 👉 */help* to go to the menu or Click 👉 */password* to check again",parse_mode='Markdown')

#* Translator
@bot.message_handler(commands=['translator'])
def translator_command_bot(message):
    text = 'Enter the Text you want to translate'
    msg = bot.send_message(message.chat.id,text)
    bot.register_next_step_handler(msg,pick_language)

def pick_language(message):
    text_to_translate = message.text
    text = f'''
        Type the language code you want to translate 
        * Type *ja* for Japanese
        * Type *es* for Spanish
        * Type *hi* for Hindi
        * Type *de* for German
        * Type *pt* for portuguese 
    '''
    msg = bot.send_message(message.chat.id,text)
    bot.register_next_step_handler(msg,google_translate_text,text_to_translate)

def google_translate_text(message, text_to_translate):
    lang_code_to_translate = message.text.lower()
    if lang_code_to_translate not in ['es','de','pt','ja','hi']:
        bot.send_message(message.chat.id, f"Invalid language code given {lang_code_to_translate} Click 👉 */help* to go to the menu or Click 👉 */translator* to check again",parse_mode='Markdown')
        return
    
    translated_response = utils.get_google_translate(text_to_translate,lang_code_to_translate)
    transtated_text = translated_response['data']['translations'][0]['translatedText']

    if transtated_text:
        text = f'Given Text: *{text_to_translate}* \n Translated Text: *{transtated_text}*'
        bot.send_message(message.chat.id,text)
        bot.send_message(message.chat.id, f"Click 👉 */help* to go to the menu or Click 👉 */translator* to check again",parse_mode='Markdown')
    else:
        text = f'Given Text: *{text_to_translate}* \n *Failed* to translate'
        bot.send_message(message.chat.id,text)
        bot.send_message(message.chat.id, f"Click 👉 */help* to go to the menu or Click 👉 */translator* to check again",parse_mode='Markdown')

@bot.message_handler(func=lambda msg : True)
def echo_all_msg(message):
    text = f'sorry {message.from_user.first_name}, I am not programmed for this command yet, Click 👉 */help* to go to the menu'
    bot.reply_to(message, text)

log.info('Bot is in pooling mode')
bot.infinity_polling()