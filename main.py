
import random
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from config import TOKEN, OPENWEATHERMAP_API_KEY  # Store your OpenWeatherMap API key here
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import aiohttp
from gtts import gTTS
import os


bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# Define a state class for the weather FSM
class WeatherState(StatesGroup):
    waiting_for_city = State()


@dp.message(Command("video"))
async def video(message: Message):
    await bot.send_chat_action(message.chat.id, "upload_video")
    video = FSInputFile("faq-01.mp4")
    await bot.send_video(message.chat.id, video)


@dp.message(Command("voice"))
async def voice(message: Message):
    voice = FSInputFile("Example.ogg")
    await bot.send_voice(message.chat.id, voice)


@dp.message(Command("doc"))
async def doc(message: Message):
    doc = FSInputFile("9ma0-01-que-20220608 copy.pdf")
    await bot.send_document(message.chat.id, doc)


@dp.message(Command("audio"))
async def audio(message: Message):
    audio = FSInputFile("PE15 Аудио 6.mp3")
    await bot.send_audio(message.chat.id, audio)


@dp.message(Command("training"))
async def training(message: Message):
    training_list = [
        "Тренировка 1:\n1. Скручивания: 3 подхода по 15 повторений\n2. Велосипед: 3 подхода по 20 повторений (каждая сторона)\n3. Планка: 3 подхода по 30 секунд",
        "Тренировка 2:\n1. Подъемы ног: 3 подхода по 15 повторений\n2. Русский твист: 3 подхода по 20 повторений (каждая сторона)\n3. Планка с поднятой ногой: 3 подхода по 20 секунд (каждая нога)",
        "Тренировка 3:\n1. Скручивания с поднятыми ногами: 3 подхода по 15 повторений\n2. Горизонтальные ножницы: 3 подхода по 20 повторений\n3. Боковая планка: 3 подхода по 20 секунд (каждая сторона)"
    ]
    rand_tr = random.choice(training_list)
    await message.answer(f"Тренировка на сегодня:\n {rand_tr}")
    tts = gTTS(text=rand_tr, lang="ru")
    # tts.save("training.mp3")
    # await bot.send_audio(message.chat.id, audio=FSInputFile("training.mp3"))
    # os.remove("training.mp3")
    tts.save("training.ogg")
    audio = FSInputFile("training.ogg")
    await bot.send_voice(message.chat.id, audio)
    os.remove("training.ogg")



@dp.message(Command("weather"))
async def weather(message: Message, state: FSMContext):
    await message.answer("Погода в каком городе вас интересует?")
    await state.set_state(WeatherState.waiting_for_city)  # Set state to wait for city name


@dp.message(WeatherState.waiting_for_city)
async def get_city_name(message: Message, state: FSMContext):
    city = message.text  # Get the city name provided by the user
    await fetch_weather(city, message)
    await state.clear()  # Clear state after handling the city input


async def fetch_weather(city: str, message: Message):
    """Fetch weather data from OpenWeatherMap API and send it to the user."""
    api_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric&lang=ru"

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            if response.status == 200:
                data = await response.json()
                city_name = data['name']
                weather_description = data['weather'][0]['description']
                temperature = data['main']['temp']
                humidity = data['main']['humidity']
                wind_speed = data['wind']['speed']

                # Send weather information back to the user
                weather_report = (f"Погода в {city_name}:\n"
                                  f"Описание: {weather_description.capitalize()}\n"
                                  f"Температура: {temperature}°C\n"
                                  f"Влажность: {humidity}%\n"
                                  f"Скорость ветра: {wind_speed} м/с")
                await message.answer(weather_report)
            else:
                await message.answer(
                    "Не удалось получить погоду для этого города. Пожалуйста, проверьте название города и попробуйте еще раз.")


@dp.message(Command("photo"))
async def photo(message: Message):
    photo_list = [
        'https://t3.ftcdn.net/jpg/09/41/44/72/360_F_941447278_Bh1lLtR1kaVP3lcNh11MDNrCBRcG3bu7.jpg',
        'https://media.istockphoto.com/id/93210320/photo/young-siamese-sable-ferret-kit.jpg?s=612x612&w=0&k=20&c=8-_kkouFkllyrsexTFo82su-GbrO_V3z_LbL7MX5hTU=',
        'https://media.gettyimages.com/id/97086548/photo/pet-ferret.jpg?s=612x612&w=gi&k=20&c=xp7Hs15_YVMeuRIJhbeB-09X7Hv85EIGQDWdknTu92M='
    ]
    rand_photo = random.choice(photo_list)
    await message.answer_photo(photo=rand_photo, caption="Вот такая фотка")


@dp.message(F.photo)
async def react_photo(message: Message):
    list = ['Ого, какая фотка!', 'Непонятно, что это такое', 'Не отправляй мне такое больше']
    rand_answ = random.choice(list)
    await message.answer(rand_answ)
    await bot.download(message.photo[-1], destination=f'tmp/{message.photo[-1].file_id}.jpg')


@dp.message(F.text == "Что такое ИИ?")
async def aitext(message: Message):
    await message.answer(
        "Искусственный интеллект — это свойство искусственных интеллектуальных систем выполнять творческие функции, которые традиционно считаются прерогативой человека; наука и технология создания интеллектуальных машин, особенно интеллектуальных компьютерных программ")


@dp.message(Command("help"))
async def help(message: Message):
    await message.answer("Этот бот умеет выполнять команды: \n /start \n /help \n /weather \n /photo")


@dp.message(CommandStart())
async def start(message: Message):
    await message.reply(f"Привет, {message.from_user.full_name}!")


@dp.message()
async def start(message: Message):
    if message.text.lower() == "тест":
        await message.answer("Тестируем")
    await message.send_copy(message.chat.id)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
