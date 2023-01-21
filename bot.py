import logging
import os

import aiogram
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.types.input_file import InputFile
from aiogram.utils import executor

import config
import parser


# States
class Book(StatesGroup):
    link = State()  # Will be represented in storage as 'Form:link'
    format = State()  # Will be represented in storage as 'Form:format'


class LoveReadBot:
    bp: parser.Parser
    bot: aiogram.Bot
    dp: aiogram.Dispatcher
    cfg: config.Config.BotConfig

    def __init__(self, cfg: config.Config.BotConfig, bp: parser.Parser):
        self.bp = bp
        self.bot = Bot(token=cfg.token_env)
        self.cfg = cfg
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())

    def setup(self):
        self.dp.register_message_handler(self.cmd_start, commands='start')
        self.dp.register_message_handler(self.cmd_get_book, commands='get_book')
        self.dp.register_message_handler(self.cancel_handler, commands='cancel', state='*')
        self.dp.register_message_handler(self.process_link, state=Book.link)
        self.dp.register_message_handler(self.process_format_invalid,
                                         lambda message: message.text not in self.cfg.allowed_formats,
                                         state=Book.format)
        self.dp.register_message_handler(self.process_format, state=Book.format)

    async def cmd_start(self, message: types.Message):
        response_message = '''
        Цей бот допоможе заватажити книжку із сайту loveread.ec
    
        Для того, щоб завантажити книжку, введіть команду  /get_book
            '''

        await self.bot.send_message(message.chat.id, response_message)

    async def cmd_get_book(self, message: types.Message):
        response_message = '''Введіть посилання на книжку.
        /cancel щоб відмінити'''

        # Set state
        await Book.link.set()

        await self.bot.send_message(message.chat.id, response_message)

    async def cancel_handler(self, message: types.Message, state: FSMContext):
        """
        Allow user to cancel any action
        """
        current_state = await state.get_state()
        if current_state is None:
            return

        logging.info('Cancelling state %r', current_state)
        # Cancel state and inform user about it
        await state.finish()
        # And remove keyboard (just in case)
        await self.bot.send_message(message.chat.id, 'Відмінено')

    async def process_link(self, message: types.Message, state: FSMContext):
        """
        Process book link
        """
        async with state.proxy() as data:
            data['link'] = message.text

        await Book.next()

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add(*self.cfg.allowed_formats)
        await self.bot.send_message(message.chat.id, 'Оберіть формат', reply_markup=markup)

    async def process_format_invalid(self, message: types.Message):
        return await message.reply("Невірний формат.")

    async def process_format(self, message: types.Message, state: FSMContext):
        # Remove keyboard
        markup = types.ReplyKeyboardRemove()
        await self.bot.send_message(message.chat.id, 'Завантажуємо книжку. Зачекайте, будь ласка',
                                    reply_markup=markup,
                                    parse_mode=ParseMode.MARKDOWN)

        async with state.proxy() as data:
            data['format'] = message.text

            try:
                filename = self.bp.read_book_to_file(data['link'], data['format'])
                file = InputFile(filename, filename=filename)

                await self.bot.send_document(message.chat.id, file)
                os.remove(filename)
            except Exception as e:
                logging.error(f'Error downloading file: {e}')
                await self.bot.send_message(message.chat.id, 'Помилка завантаження книжки. Спробуйте пізніше')

        # Finish conversation
        await state.finish()

    def start_polling(self):
        executor.start_polling(self.dp, skip_updates=True)
