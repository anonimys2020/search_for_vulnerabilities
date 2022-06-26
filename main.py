# -*- coding: utf-8 -*-
# pip install pytelegrambotapi
# pip install requests
# pip install lxml
# pip install beautifulsoup4
import telebot
from config import *
import requests
from lxml import html
from bs4 import BeautifulSoup
from time import sleep

bot = telebot.TeleBot(TOKEN)
headers = {
    'User-Agent': 'your User-Agent here'
}


def extract_arg(message): # функция получения аргументов из команды
    arg = message.split()
    arg.pop(0) # удаляем саму команду, чтобы получить только аргументы
    return arg


def query(message): # получаем запрос и заменяем пробелы на +
    arg = message.split()
    arg.pop(0)
    string = '+'.join(arg)
    return string


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, 'Здравствуйте! Этот бот создан для поиска уязвимостей.')
    bot.send_message(message.chat.id, 'Чтобы начать поиск, введите команду /search {запрос} {количество результатов для отображения} {номер страницы}')
    bot.send_message(message.chat.id, 'Пример: /search Mac OS 3 1')


@bot.message_handler(commands=["search"]) # команда поиска
def search(message): # функция поиска
    try:
        args = extract_arg(message.text) # получаем все аргументы
        if len(args) >= 3:
            page = int(extract_arg(message.text)[-1]) # получаем номер страницы
            size = int(extract_arg(message.text)[-2]) # получаем количество запросов
            if page >= 1 or size >= 1:
                if size <= 10:
                    q = query(message.text)
                    r = requests.get(f'http://bdu.fstec.ru/search?size={size}&q={q}&page={page}', headers=headers) # делаем get запрос
                    soup = BeautifulSoup(r.text, 'html.parser')
                    for div in soup.find_all('div', {'class': 'search-item'}): # проходимся по всем уязвимостям
                        soup = BeautifulSoup(str(div), 'html.parser')
                        h4 = soup.find('a') # получаем заголовок уязвимости
                        link = h4['href'] # получаем ссылку
                        h4 = h4.text # получаем текст из тега <a>
                        text = soup.get_text(strip=True, separator='\n\n') # получаем всю информацию о уязвимости
                        markup = telebot.types.InlineKeyboardMarkup()
                        button1 = telebot.types.InlineKeyboardButton("Подробнее", url=f'https://bdu.fstec.ru{link}') # Создаем кнопку со ссылкой на ресурс
                        markup.add(button1)
                        bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=markup) # Отправляем результат запроса
                        # sleep(1)
                else:
                    bot.send_message(message.chat.id, 'Запросов не должно быть больше 10!')
            else:
                bot.send_message(message.chat.id, 'Аргументы не могут быть меньше еденицы!')
        else:
            bot.send_message(message.chat.id, 'Неверно введены данные!')
    except Exception:
        bot.send_message(message.chat.id, 'Неверно введены данные!')


bot.polling(none_stop=True, interval=0)