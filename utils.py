import requests
from pathlib import Path
import json
import logging as log
import sys
import os
import hashlib
from dotenv import load_dotenv # python-dotenv
from datetime import datetime

load_dotenv('./.env')

BOT_USERNAME = os.getenv('BOT_USERNAME')
API_TOKEN = os.getenv('PUBLIC_API_TOKEN')

#! try catch decorator
def exception_handling(func):
    def wrapper_func(*args,**kwargs):
        try:
            return func(*args,*kwargs)
        except requests.exceptions.RequestException as e:
            log.error(f'{func.__name__} API request failed to execute. {e}')
            sys.exit()
        except FileNotFoundError as e:
            log.error(f'{func.__name__} File failed to execute. {e}')
            sys.exit()
        except ValueError:
            log.error(f'{func.__name__} Invalid value format.')
            sys.exit()
        except Exception as e:
            log.error(f'{func.__name__} failed to execute. {e}')
            sys.exit()
    
    return wrapper_func

#! url fetch function
@exception_handling
def get_url_by_type(type: str,url_key_name: str):
    
    url_file_path = Path('./url.json')

    with url_file_path.open(mode='r') as file:
        json_data = json.load(file)
    
    if type in json_data[0]:
         url_data = json_data[0][type]
    else: 
        return False

    if url_key_name in url_data:
        url = url_data[url_key_name]   
        return url
    else:
         return False
    
def is_valid_date(date_string):
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

@exception_handling
def hashing_text(password_text:str) -> str:
    hashed_object = hashlib.sha1(password_text.encode('utf-8'))
    hashed_string = hashed_object.hexdigest()
    return hashed_string.upper()

#* horoscope api
@exception_handling
def get_horoscope_data(sign: str, day: str) -> dict:
    horoscope_url = get_url_by_type('public_api','horoscope_url')
    if not horoscope_url : return False
    params = {"sign": sign, "day": day.upper()}
    response = requests.get(horoscope_url,params)
    return response.json()

@exception_handling
def get_password_breach_data(hashed_password_preffix : str):
    api_url = get_url_by_type('pwned','pwned_password_url')
    if not api_url : return False
    response = requests.get(f'{api_url}/{hashed_password_preffix}')
    return response.text

@exception_handling
def password_breach_count(response, hashed_string: str) -> int:
    hashed_response = [lines.split(':') for lines in response.splitlines()]
    for hashed_response_suffix, count in hashed_response:
        if hashed_response_suffix == hashed_string:
           return count
    return 0

#* google translator
@exception_handling
def get_google_translate(text_to_translate, lang_code_to_translate):
    api_url = get_url_by_type('public_api','translator_url')
  
    payload = {
        "q": text_to_translate,
        "target": lang_code_to_translate,
        "source": "en"
    }

    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "application/gzip",
        "X-RapidAPI-Key": API_TOKEN,
        "X-RapidAPI-Host": "google-translate1.p.rapidapi.com"
    }

    response = requests.post(api_url,data=payload,headers=headers)
    return response.json()
