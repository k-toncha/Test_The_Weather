import re
import asyncio
import time
import aiohttp


class Weather:
    def __init__(self, name_en):
        self.name_en = name_en

    def set_params(self, temp, humidity, wind_speed, description, name_ru):
        self.temp = temp
        self.humidity = humidity
        self.wind_speed = wind_speed
        self.description = description
        self.name_ru = name_ru

    def print_all(self):
        print(f"В городе {self.name_ru} {self.description}")
        print('%-20s' % f"Температура",  f"{self.temp} °С")
        print('%-20s' % f"Скорость ветра",  f"{self.wind_speed} м/с")
        print('%-20s' % f"Влажность",  f"{self.humidity} %")
        print()


cities = []  # список объектов класса Weather
tasks = []  # сисок задач

with open("cities.txt") as file:
    data = file.read()
    for s in re.findall(r'.{3}(\w\D+) [-\d]', data):  # создание списка с объектами класса Weather
        if '-' in s:
            t = Weather(s[:-2])
            cities.append(t)
        else:
            t = Weather(s)
            cities.append(t)


async def get_weather(obj):
    async with aiohttp.ClientSession() as session:
        url = 'http://api.openweathermap.org/data/2.5/weather'
        params = {'q': obj.name_en, "APPID": "2a4ff86f9aaa70041ec8e82db64abf56", "units": "metric", 'lang': 'ru'}

        async with session.get(url, params=params) as response:
            w_json = await response.json()
            if w_json['cod'] == 200:
                obj.set_params(w_json['main']['temp'], w_json['main']['humidity'],  # заполнение объекта основными параметрами, если ответ получен
                               w_json['wind']['speed'], w_json['weather'][0]['description'],
                               w_json['name'])


async def main(cities):

    for obj in cities:
        tasks.append(asyncio.create_task(get_weather(obj)))  # создание конкурентных задач

    for task in tasks:  # запуск задач
        await task

    for city in cities:  # вызов метода print_all у каждого объекта
        try:
            city.print_all()
        except AttributeError:  # ошибка, возникающщая, если инфа по городу не получена
            print(f"Город {city.name_en} не найден")
            print()

if __name__ == "__main__":
    start_time = time.monotonic()
    asyncio.run(main(cities))
    print(f"Время работы программы: {round(time.monotonic() - start_time, 4)} сек.")
