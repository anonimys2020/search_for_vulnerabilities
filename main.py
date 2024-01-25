# -*- coding: utf-8 -*-
# pip install pytelegrambotapi
# pip install requests
# pip install beautifulsoup4

import telebot
import requests
from bs4 import BeautifulSoup
from config import TOKEN

bot = telebot.TeleBot(TOKEN)
headers = {
    'User-Agent': 'your User-Agent here'
}

COMMAND_START = '/start'
COMMAND_SEARCH = '/search'
MESSAGE_WELCOME = 'Здравствуйте! Этот бот создан для поиска уязвимостей.'
MESSAGE_INSTRUCTIONS = 'Чтобы начать поиск, введите команду \
    /search (запрос) (количество результатов для отображения) (номер страницы)'
MESSAGE_EXAMPLE = 'Пример: /search Mac OS 3 1'
MESSAGE_INVALID_DATA = 'Неверно введены данные!'
MESSAGE_ARG_LIMIT = 'Запросов не должно быть больше 10!'
MESSAGE_ARG_MINIMUM = 'Аргументы не могут быть меньше единицы!'


def extract_arg(message):
    """
    Extracts arguments from the command message.

    Args:
        message (str): The command message.

    Returns:
        list: List of extracted arguments.
    """
    arg = message.split()
    arg.pop(0)  # Remove the command itself to get only arguments
    return arg


def query(message):
    """
    Generates a query string by replacing spaces with '+'.

    Args:
        message (str): The command message.

    Returns:
        str: Query string.
    """
    arg = message.split()
    arg.pop(0)
    string = "+".join(arg)
    return string


@bot.message_handler(commands=[COMMAND_START])
def start(message):
    """
    Handles the /start command by sending a welcome message.

    Args:
        message (obj): The message object.
    """
    bot.send_message(message.chat.id, MESSAGE_WELCOME)
    bot.send_message(message.chat.id, MESSAGE_INSTRUCTIONS)
    bot.send_message(message.chat.id, MESSAGE_EXAMPLE)


@bot.message_handler(commands=[COMMAND_SEARCH])
def search(message):
    """
    Handles the /search command to perform vulnerability search.

    Args:
        message (obj): The message object.
    """
    try:
        args = extract_arg(message.text)

        if len(args) < 3:
            bot.send_message(message.chat.id, MESSAGE_INVALID_DATA)
            return

        page = int(args[-1])
        size = int(args[-2])

        if page < 1 or size < 1:
            bot.send_message(message.chat.id, MESSAGE_ARG_MINIMUM)
            return

        if size > 10:
            bot.send_message(message.chat.id, MESSAGE_ARG_LIMIT)
            return

        q = query(message.text)
        r = requests.get(f'http://bdu.fstec.ru/search?\
                         size={size}&q={q}&page={page}',
                         headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')

        for div in soup.find_all('div', {'class': 'search-item'}):
            soup = BeautifulSoup(str(div), 'html.parser')
            h4 = soup.find('a')
            link = h4['href']
            h4 = h4.text
            text = soup.get_text(strip=True, separator='\n\n')
            markup = telebot.types.InlineKeyboardMarkup()
            button1 = telebot.types.InlineKeyboardButton(
                'Подробнее',
                url=f'https://bdu.fstec.ru{link}'
                )
            markup.add(button1)
            bot.send_message(message.chat.id,
                             text,
                             parse_mode='HTML',
                             reply_markup=markup)

    except Exception:
        bot.send_message(message.chat.id, MESSAGE_INVALID_DATA)


bot.polling(none_stop=True, interval=0)
