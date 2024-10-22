import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN, OPENWEATHERMAP_API_KEY
import sqlite3
import aiohttp
import logging

bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)


class Form(StatesGroup):
    name = State()
    age = State()
    city = State()

def init_db():
    conn = sqlite3.connect('user_data.db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  age INTEGER NOT NULL,
                  city TEXT NOT NULL)""")
    conn.commit()
    conn.close()


init_db()


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer(f"Привет, как тебя зовут?")
    await state.set_state(Form.name)


@dp.message(Form.name)
async def name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(f"Сколько тебе лет?")
    await state.set_state(Form.age)


@dp.message(Form.age)
async def age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer(f"В каком городе ты живешь?")
    await state.set_state(Form.city)


@dp.message(Form.city)
async def city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    user_data = await state.get_data()

    conn = sqlite3.connect('user_data.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO users (name, age, city) VALUES (?, ?, ?)", (user_data['name'], user_data['age'], user_data['city']))
    conn.commit()
    conn.close()

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.openweathermap.org/data/2.5/weather?q={user_data['city']}&appid={OPENWEATHERMAP_API_KEY}&units=metric&lang=ru") as response:
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
                await message.answer("Не удалось получить погоду для этого города. Пожалуйста, проверьте название города и попробуйте еще раз.")

    await state.clear()
















async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

