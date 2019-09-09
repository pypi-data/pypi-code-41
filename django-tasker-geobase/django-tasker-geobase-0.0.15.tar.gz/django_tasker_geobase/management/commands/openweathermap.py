import time
import os

import requests
from django.conf import settings
from django.core.management import BaseCommand
from django_tasker_geobase import geocoder, models


class Command(BaseCommand):
    help = 'OpenWeather'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            nargs='?',
            default='download_large_city',
            type=str,
            choices=['download_large_city'],
            help='Action; download_city=Loading weather for 300 largest cities',
        )

        parser.add_argument(
            '--sleep',
            nargs='?',
            default=2.35,
            type=float,
            help='Sleep',
        )

    def handle(self, *args, **options):
        if options.get('action') == 'download_large_city':
            if options.get('verbosity'):
                self.stdout.write(self.style.SUCCESS('Loading weather for 300 largest cities'))
            self.download_large_city(options)

    def download_large_city(self, options):
        # https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D0%B3%D0%BE%D1%80%D0%BE%D0%B4%D0%BE%D0%B2_%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D0%B8_%D1%81_%D0%BD%D0%B0%D1%81%D0%B5%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5%D0%BC_%D0%B1%D0%BE%D0%BB%D0%B5%D0%B5_100_%D1%82%D1%8B%D1%81%D1%8F%D1%87_%D0%B6%D0%B8%D1%82%D0%B5%D0%BB%D0%B5%D0%B9
        # https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D1%81%D1%82%D1%80%D0%B0%D0%BD,_%D0%B3%D0%B4%D0%B5_%D1%81%D1%82%D0%BE%D0%BB%D0%B8%D1%86%D0%B0_%D0%BD%D0%B5_%D1%8F%D0%B2%D0%BB%D1%8F%D0%B5%D1%82%D1%81%D1%8F_%D0%BA%D1%80%D1%83%D0%BF%D0%BD%D0%B5%D0%B9%D1%88%D0%B8%D0%BC_%D0%B3%D0%BE%D1%80%D0%BE%D0%B4%D0%BE%D0%BC
        # https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D1%81%D1%82%D0%BE%D0%BB%D0%B8%D1%86_%D0%BC%D0%B8%D1%80%D0%B0

        list_city = [
            "Москва",
            "Санкт-Петербург",
            "Новосибирск",
            "Екатеринбург",
            "Нижний Новгород",
            "Казань",
            "Челябинск",
            "Омск",
            "Самара",
            "Ростов-на-Дону",
            "Уфа",
            "Красноярск",
            "Воронеж",
            "Пермь",
            "Волгоград",
            "Краснодар",
            "Саратов",
            "Тюмень",
            "Тольятти",
            "Ижевск",
            "Барнаул",
            "Ульяновск",
            "Иркутск",
            "Хабаровск",
            "Ярославль",
            "Владивосток",
            "Махачкала",
            "Томск",
            "Оренбург",
            "Кемерово",
            "Новокузнецк",
            "Рязань",
            "Астрахань",
            "Набережные Челны",
            "Киров",
            "Липецк",
            "Чебоксары",
            "Калининград",
            "Тула",
            "Балашиха",
            "Курск",
            "Севастополь",
            "Сочи",
            "Ставрополь",
            "Улан-Удэ",
            "Тверь",
            "Магнитогорск",
            "Брянск",
            "Иваново",
            "Белгород",
            "Сургут",
            "Владимир",
            "Нижний Тагил",
            "Архангельск",
            "Чита",
            "Симферополь",
            "Калуга",
            "Смоленск",
            "Волжский",
            "Саранск",
            "Якутск",
            "Череповец",
            "Курган",
            "Орёл",
            "Вологда",
            "Владикавказ",
            "Подольск",
            "Грозный",
            "Мурманск",
            "Тамбов",
            "Петрозаводск",
            "Стерлитамак",
            "Нижневартовск",
            "Кострома",
            "Новороссийск",
            "Йошкар-Ола",
            "Химки",
            "Таганрог",
            "Комсомольск-на-Амуре",
            "Сыктывкар",
            "Нижнекамск",
            "Нальчик",
            "Шахты",
            "Дзержинск",
            "Орск",
            "Братск",
            "Энгельс",
            "Ангарск",
            "Благовещенск",
            "Королёв",
            "Великий Новгород",
            "Старый Оскол",
            "Мытищи",
            "Псков",
            "Люберцы",
            "Южно-Сахалинск",
            "Бийск",
            "Прокопьевск",
            "Армавир",
            "Балаково",
            "Рыбинск",
            "Абакан",
            "Северодвинск",
            "Петропавловск-Камчатский",
            "Норильск",
            "Уссурийск",
            "Волгодонск",
            "Сызрань",
            "Новочеркасск",
            "Каменск-Уральский",
            "Златоуст",
            "Красногорск",
            "Электросталь",
            "Альметьевск",
            "Салават",
            "Миасс",
            "Керчь",
            "Находка",
            "Копейск",
            "Пятигорск",
            "Хасавюрт",
            "Коломна",
            "Рубцовск",
            "Березники",
            "Майкоп",
            "Одинцово",
            "Ковров",
            "Кисловодск",
            "Домодедово",
            "Нефтекамск",
            "Нефтеюганск",
            "Новочебоксарск",
            "Батайск",
            "Щёлково",
            "Серпухов",
            "Дербент",
            "Новомосковск",
            "Черкесск",
            "Первоуральск",
            "Каспийск",
            "Орехово-Зуево",
            "Кызыл",
            "Обнинск",
            "Назрань",
            "Новый Уренгой",
            "Невинномысск",
            "Раменское",
            "Димитровград",
            "Октябрьский",
            "Долгопрудный",
            "Камышин",
            "Ессентуки",
            "Муром",
            "Новошахтинск",
            "Жуковский",
            "Евпатория",
            "Северск",
            "Реутов",
            "Артём",
            "Ноябрьск",
            "Ачинск",
            "Пушкино",
            "Арзамас",
            "Бердск",
            "Сергиев Посад",
            "Елец",
            "Элиста",
            "Ногинск",
            "Новокуйбышевск",
            "Железногорск",
        ]

        for city in list_city:
            #if options.get('verbosity'):
            #    self.stdout.write(self.style.SUCCESS("город {city}".format(city=city)))

            result = geocoder.geo("город {city}".format(city=city))
            if options.get('verbosity'):
                self.stdout.write(self.style.SUCCESS("{geobase}, {latitude}, {longitude}".format(
                    latitude=result.object.latitude,
                    longitude=result.object.longitude,
                    geobase=result.object
                )))

            # openweathermap download
            openweathermap_key = getattr(
                settings, 'GEOBASE_OPENWEATHERMAP_KEY',
                os.environ.get('GEOBASE_OPENWEATHERMAP_KEY')
            )

            if openweathermap_key:
                proxies = getattr(settings, 'GEOBASE_SOCKS5_PROXY', os.environ.get('GEOBASE_SOCKS5_PROXY'))
                if proxies:
                    proxies = {'http': proxies, 'https': proxies}

                    response = requests.get(
                        url='https://api.openweathermap.org/data/2.5/weather/',
                        params={
                            'lat': result.object.latitude,
                            'lon': result.object.longitude,
                            'appid': openweathermap_key,
                            'units': 'metric',
                            'lang': 'en',
                        },
                        timeout=60,
                        proxies=proxies
                    )

                    if response.status_code == 200:
                        openweather_result = response.json()
                        weather = models.Weather(
                            geobase=result.object,
                            temperature=openweather_result.get('main').get('temp'),
                            temperature_min=openweather_result.get('main').get('temp_min'),
                            temperature_max=openweather_result.get('main').get('temp_max'),
                            pressure=openweather_result.get('main').get('pressure'),
                            humidity=openweather_result.get('main').get('humidity'),
                            visibility=openweather_result.get('visibility'),
                            wind_speed=openweather_result.get('wind').get('speed'),
                            wind_degrees=openweather_result.get('wind').get('deg'),
                            clouds=openweather_result.get('clouds').get('all'),
                        )
                        weather.save()
            time.sleep(options.get('sleep'))
