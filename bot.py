import logging

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.types.input_file import InputFile
from aiogram.utils import executor

import parser as bp

logging.basicConfig(level=logging.DEBUG, format='%(levelname) -s at %(asctime) -s: %(message)s')
API_TOKEN = '5309101557:AAFO-1iGgkx8JV5cq95sdWhKdH6rW37V_Ew'
ALLOWED_FORMATS = ['txt', 'epub', 'pdf', 'fb2']

bot = Bot(token=API_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# States
class Book(StatesGroup):
    link = State()  # Will be represented in storage as 'Form:name'
    format = State()  # Will be represented in storage as 'Form:age'


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    response_message = '''
    Цей бот допоможе заватажити книжку із сайту loveread.ec

    Для того, щоб завантажити книжку, введіть команду  /get_book
        '''

    await bot.send_message(message.chat.id, response_message)


@dp.message_handler(commands='get_book')
async def cmd_get_book(message: types.Message):
    response_message = '''Введіть посилання на книжку.
    /cancel щоб відмінити'''

    # Set state
    await Book.link.set()

    await bot.send_message(message.chat.id, response_message)


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
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
    await bot.send_message(message.chat.id, 'Відмінено')


@dp.message_handler(state=Book.link)
async def process_link(message: types.Message, state: FSMContext):
    """
    Process book link
    """
    async with state.proxy() as data:
        data['link'] = message.text

    await Book.next()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(*ALLOWED_FORMATS)
    await bot.send_message(message.chat.id, 'Оберіть формат', reply_markup=markup)


@dp.message_handler(lambda message: message.text not in ALLOWED_FORMATS, state=Book.format)
async def process_format_invalid(message: types.Message):
    return await message.reply("Невірний формат.")


@dp.message_handler(state=Book.format)
async def process_format(message: types.Message, state: FSMContext):
    # Remove keyboard
    markup = types.ReplyKeyboardRemove()
    await bot.send_message(message.chat.id, 'Завантажуємо книжку. Зачекайте, будь ласка',
                           reply_markup=markup,
                           parse_mode=ParseMode.MARKDOWN)

    async with state.proxy() as data:
        data['format'] = message.text

        filename = bp.read_book_to_file(data['link'], data['format'])
        file = InputFile(filename, filename=filename)

        await bot.send_document(message.chat.id,
                                file)
        # todo delete file

    # Finish conversation
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
