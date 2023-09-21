# импортируем необходимые библиотеки и модули
import os
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode

# загружаем переменные окружения из файла .env
load_dotenv()

# устанавливаем модель GPT-4, ключ API OpenAI и токен Telegram из переменных окружения
OPEN_MODEL = "gpt-4"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# настраиваем логирование событий на уровне INFO
logging.basicConfig(level=logging.INFO)

# создаем объект MemoryStorage для хранения состояний FSM в памяти
storage = MemoryStorage()

# создаем объект бота с использованием токена Telegram
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# создаем диспетчер для обработки сообщений и состояний FSM
dp = Dispatcher(bot, storage=storage)

# устанавливаем миддлвэр LoggingMiddleware для логирования событий
dp.middleware.setup(LoggingMiddleware())


# определяем состояния FSM с использованием StatesGroup
class MyStates(StatesGroup):
    some_state = State()


# обработчик команды "/start"
@dp.message_handler(commands=['start'], state="*")
async def on_start(message: types.Message):
    await message.answer("Привет! Этот бот предназначен для продажи автомобилей. "
                         "Введите текстовое сообщение, чтобы начать разговор.")
    # устанавливаем состояние some_state
    await MyStates.some_state.set()


# обработчик команды "/help"
@dp.message_handler(commands=['help'], state="*")
async def on_help(message: types.Message):
    await message.answer("Доступные команды:\n"
                         "/start - Начать разговор\n"
                         "/help - Помощь")


# обработчик текстовых сообщений в состоянии some_state
@dp.message_handler(lambda message: message.text, state=MyStates.some_state)
async def process_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        # создаем объект ChatOpenAI
        llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model_name=OPEN_MODEL)
        user_message = message.text
        try:
            # запускаем gpt-4
            result = llm.predict(user_message)
            # отправляем ответ пользователю
            await message.reply(result, parse_mode=ParseMode.HTML)
        except Exception as e:
            # логируем ошибку
            logging.error(f"An error occurred: {e}")
            await message.reply("Произошла ошибка при обработке вашего запроса.")


# запуск бота
def main():
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)


# точка входа
if __name__ == "__main__":
    main()
