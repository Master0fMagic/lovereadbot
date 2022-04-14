import telebot
from telebot import types

bot = telebot.TeleBot("5309101557:AAFO-1iGgkx8JV5cq95sdWhKdH6rW37V_Ew", parse_mode=None)  # todo change token to bot tocken

ALLOWED_FORMATS = ['txt', 'epub', 'pdf', 'fb2']


@bot.message_handler(commands=['start', 'help'])
def on_start(message):
    response_message = '''
Этот бот предназначен для скачивания книг с сайта loveread.ec

Что бы скачать книгу, введите команду /get_book, вставьте ссылку на книгу и выберите фортмат книги
    '''
    bot.send_message(message.chat.id, response_message)


@bot.message_handler(commands=['get_book'])
def on_get_book(message):
    response = '''Введите ссылку на книгу'''
    bot.send_message(message.chat.id, response)


@bot.message_handler(func=lambda mes: mes.text in ALLOWED_FORMATS)
def on_file_type(message):
    pass


@bot.message_handler()
def on_book_link(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    buttons = [types.KeyboardButton(book_format) for book_format in ALLOWED_FORMATS]
    markup.add(buttons)
    bot.send_message(message.chat.id, "Выберите формат книги:", reply_markup=markup)


bot.infinity_polling()


