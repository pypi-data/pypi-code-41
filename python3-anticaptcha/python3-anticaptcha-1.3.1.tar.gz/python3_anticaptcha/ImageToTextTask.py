import time
import asyncio
import hashlib
import os
import base64

import requests
import aiohttp

from python3_anticaptcha import (
    create_task_url,
    app_key,
    get_sync_result,
    get_async_result,
    ParamError,
    ReadError,
)


class ImageToTextTask:
    """
    Данный метод подходит для решения капчи-изображение.
    Подробней информацию смотрите в методе 'captcha_handler' и '__init__'
    """

    def __init__(
        self,
        anticaptcha_key: str,
        sleep_time: int = 5,
        save_format: str = "temp",
        language: str = "en",
        callbackUrl: str = None,
        **kwargs,
    ):
        """
        Инициализация нужных переменных, создание папки для изображений и кэша
        После завершения работы - удаляются временные фалйы и папки
        :param anticaptcha_key:  АПИ ключ капчи из кабинета пользователя
        :param sleep_time: Вермя ожидания решения капчи
        :param save_format: Формат в котором будет сохраняться изображение, либо как временный файл - 'temp',
                            либо как обычное изображение в папку созданную библиотекой - 'const'.
        :param language: Язык капчи
        :param callbackUrl: URL для решения капчи с ответом через callback
        :param **kwargs: За подробной информацией обратитесь к документации на сайте anticaptcha.
        """
        if sleep_time < 5:
            raise ValueError(
                f"Параметр `sleep_time` должен быть не менее 5. Вы передали - {sleep_time}"
            )
        self.sleep_time = sleep_time
        # проверяем переданный параметр способа сохранения капчи
        if save_format in ["const", "temp"]:
            self.save_format = save_format
        else:
            raise ValueError(
                "\nПередан неверный формат сохранения файла изображения. "
                f"\n\tВозможные варинты: `temp` и `const`. Вы передали - `{save_format}`"
                "\nWrong `save_format` parameter. Valid params: `const` or `temp`."
                f"\n\tYour param - `{save_format}`"
            )
        # Пайлоад для создания задачи
        self.task_payload = {
            "clientKey": anticaptcha_key,
            "task": {"type": "ImageToTextTask"},
            "languagePool": language,
            "softId": app_key,
        }

        # задаём callbackUrl если передан
        if callbackUrl:
            self.task_payload.update({"callbackUrl": callbackUrl})

        # отправляем запрос на результат решения капчи, если ещё капча не решена - ожидаем 5 сек
        # если всё ок - идём дальше
        self.result_payload = {"clientKey": anticaptcha_key}

        # Если переданы ещё параметры - вносим их в payload
        if kwargs:
            for key in kwargs:
                self.task_payload["task"].update({key: kwargs[key]})

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            return False
        return True

    def __image_temp_saver(self, content: bytes):
        """
        Метод сохраняет файл изображения как временный и отправляет его сразу на сервер для расшифровки.
        :return: Возвращает ID капчи
        """
        # Создаём пайлоад, вводим ключ от сайта, выбираем метод ПОСТ и ждём ответа в JSON-формате
        self.task_payload["task"].update(
            {"body": base64.b64encode(content).decode("utf-8")}
        )
        # Отправляем на рукапча изображение капчи и другие парметры,
        # в результате получаем JSON ответ с номером решаемой капчи и получая ответ - извлекаем номер
        captcha_id = requests.post(create_task_url, json=self.task_payload).json()
        return captcha_id

    def __image_const_saver(self, content: bytes):
        """
        Метод создаёт папку и сохраняет в неё изображение, затем передаёт его на расшифровку и удалет файл.
        :return: Возвращает ID капчи
        """
        img_path = "PythonAntiCaptchaImages"

        if not os.path.exists(img_path):
            os.mkdir(img_path)

        # Высчитываем хэш изображения, для того что бы сохранить его под уникальным именем
        image_hash = hashlib.sha224(content).hexdigest()

        with open(
            os.path.join(img_path, "im-{0}.png".format(image_hash)), "wb"
        ) as out_image:
            out_image.write(content)

        with open(
            os.path.join(img_path, "im-{0}.png".format(image_hash)), "rb"
        ) as captcha_image:
            # Добавляем в пайлоад картинку и отправляем
            self.task_payload["task"].update(
                {"body": base64.b64encode(captcha_image.read()).decode("utf-8")}
            )
            # Отправляем на антикапча изображение капчи и другие парметры,
            # в результате получаем JSON ответ содержащий номер решаемой капчи
            captcha_id = requests.post(create_task_url, json=self.task_payload).json()

        # удаляем файл капчи
        os.remove(os.path.join(img_path, "im-{0}.png".format(image_hash)))

        return captcha_id

    def __read_captcha_image_file(self, content: bytes, content_type: str = "file"):
        """
        Функция отвечает за чтение уже сохранённого файла или файла в уодировке base64
        :param content: Параметр строка-путь указывающий на изображение капчи для отправки её на сервер
        :param content_type: Тип переданной переменной. Возможны варианты: `file` и `base64`
        :return: Возвращает ID капчи
        """
        try:
            if content_type == "file":
                with open(content, "rb") as captcha_image:
                    # Добавляем в пайлоад картинку и отправляем
                    self.task_payload["task"].update(
                        {"body": base64.b64encode(captcha_image.read()).decode("utf-8")}
                    )
            elif content_type == "base64":
                self.task_payload["task"].update({"body": content})
            else:
                raise ValueError(
                    "\nПередан неверный формат файла."
                    f"\n\tВозможные варинты: `file` и `base64`. Вы передали - `{content_type}`"
                    f"\nWrong `content_type` parameter. Valid params: `file` or `base64`."
                    f"\n\tYour param - `{content_type}`"
                )
            # Отправляем на антикапча изображение капчи и другие парметры,
            # в результате получаем JSON ответ содержащий номер решаемой капчи
            captcha_id = requests.post(create_task_url, json=self.task_payload).json()
        except (IOError, FileNotFoundError) as err:
            raise ReadError(err)

        return captcha_id

    # Работа с капчёй
    def captcha_handler(
        self,
        captcha_link: str = None,
        captcha_file: str = None,
        captcha_base64: str = None,
        **kwargs,
    ):
        """
        Метод получает от вас ссылку на изображение, скачивает его, отправляет изображение на сервер
        RuCaptcha, дожидается решения капчи и вовзращает вам результат
        :param captcha_link: Ссылка на изображение
        :param captcha_file: Необязательный параметр, служит для открытия уже скачанных файлов изображений.
        :param captcha_base64: Загрузка изображения в кодировке base64
        :return: Возвращает весь ответ сервера JSON-строкой.
        """
        if captcha_file:
            captcha_id = self.__read_captcha_image_file(
                captcha_file, content_type="file"
            )
        elif captcha_base64:
            captcha_id = self.__read_captcha_image_file(
                captcha_base64, content_type="base64"
            )
        elif captcha_link:
            content = requests.get(captcha_link, **kwargs).content
            # согласно значения переданного параметра выбираем функцию для сохранения изображения
            if self.save_format == "const":
                captcha_id = self.__image_const_saver(content)
            elif self.save_format == "temp":
                captcha_id = self.__image_temp_saver(content)
        else:
            raise ParamError(
                additional_info="""You must set one of param - `captcha_file/captcha_base64/captcha_link`.\n
                                                Вы должны задать один из параметров - `captcha_file/captcha_base64/captcha_link`."""
            )

        # Проверка статуса создания задачи, если создано без ошибок - извлекаем ID задачи, иначе возвращаем ответ сервера
        if captcha_id["errorId"] == 0:
            captcha_id = captcha_id["taskId"]
            self.result_payload.update({"taskId": captcha_id})
        else:
            return captcha_id

        # если передан параметр `callbackUrl` - не ждём решения капчи а возвращаем незаполненный ответ
        if self.task_payload.get("callbackUrl"):
            return self.result_payload

        else:
            # Ожидаем решения капчи
            time.sleep(self.sleep_time)
            return get_sync_result(
                result_payload=self.result_payload, sleep_time=self.sleep_time
            )


class aioImageToTextTask:
    """
	Данный метод подходит для всинхронного решения капчи-изображение.
	Подробней информацию смотрите в методе 'captcha_handler' и '__init__'
	"""

    def __init__(
        self,
        anticaptcha_key: str,
        sleep_time: int = 5,
        save_format: str = "temp",
        language: str = "en",
        callbackUrl: str = None,
        **kwargs,
    ):
        """
		Инициализация нужных переменных, создание папки для изображений и кэша
		После завершения работы - удаляются временные фалйы и папки
		:param anticaptcha_key:  АПИ ключ капчи из кабинета пользователя
		:param sleep_time: Вермя ожидания решения капчи
		:param save_format: Формат в котором будет сохраняться изображение, либо как временный файл - 'temp',
							либо как обычное изображение в папку созданную библиотекой - 'const'.
		:param language: Язык капчи
		:param callbackUrl: URL для решения капчи с ответом через callback
		:param **kwargs: За подробной информацией обратитесь к документации на сайте anticaptcha.
		"""
        if sleep_time < 5:
            raise ValueError(
                f"Параметр `sleep_time` должен быть не менее 10. Вы передали - {sleep_time}"
            )
        self.sleep_time = sleep_time
        # проверяем переданный параметр способа сохранения капчи
        if save_format in ["const", "temp"]:
            self.save_format = save_format
        else:
            raise ValueError(
                "\nПередан неверный формат сохранения файла изображения. "
                f"\n\tВозможные варинты: `temp` и `const`. Вы передали - `{save_format}`"
                "\nWrong `save_format` parameter. Valid params: `const` or `temp`."
                f"\n\tYour param - `{save_format}`"
            )

        # Пайлоад для создания задачи
        self.task_payload = {
            "clientKey": anticaptcha_key,
            "task": {"type": "ImageToTextTask"},
            "languagePool": language,
            "softId": app_key,
        }

        # задаём callbackUrl если передан
        if callbackUrl:
            self.task_payload.update({"callbackUrl": callbackUrl})

        # отправляем запрос на результат решения капчи, если ещё капча не решена - ожидаем 5 сек
        # если всё ок - идём дальше
        self.result_payload = {"clientKey": anticaptcha_key}

        # Если переданы ещё параметры - вносим их в payload
        if kwargs:
            for key in kwargs:
                self.task_payload["task"].update({key: kwargs[key]})

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            return False
        return True

    async def __image_temp_saver(self, captcha_link: str):
        """
		Метод сохраняет файл изображения как временный и отправляет его сразу на сервер для расшифровки.
		:return: Возвращает ID капчи
		"""
        # Скачиваем капчу
        async with aiohttp.ClientSession() as session:
            async with session.get(captcha_link) as resp:
                content = await resp.content.readany()
                # Создаём пайлоад, вводим ключ от сайта, выбираем метод ПОСТ и ждём ответа в JSON-формате
                self.task_payload["task"].update(
                    {"body": base64.b64encode(content).decode("utf-8")}
                )
                # Отправляем на рукапча изображение капчи и другие парметры,
                # в результате получаем JSON ответ с номером решаемой капчи
        async with aiohttp.ClientSession() as session:
            async with session.post(create_task_url, json=self.task_payload) as resp:
                return await resp.json()

    async def __image_const_saver(self, captcha_link: str):
        """
		Метод создаёт папку и сохраняет в неё изображение, затем передаёт его на расшифровку и удалет файл.
		:return: Возвращает ID капчи
		"""
        img_path = "PythonAntiCaptchaImages"

        if not os.path.exists(img_path):
            os.mkdir(img_path)

        # Скачиваем капчу
        async with aiohttp.ClientSession() as session:
            async with session.get(captcha_link) as resp:
                content = await resp.content.readany()

        # Высчитываем хэш изображения, для того что бы сохранить его под уникальным именем
        image_hash = hashlib.sha224(content).hexdigest()

        with open(
            os.path.join(img_path, "im-{0}.png".format(image_hash)), "wb"
        ) as out_image:
            out_image.write(content)

        with open(
            os.path.join(img_path, "im-{0}.png".format(image_hash)), "rb"
        ) as captcha_image:
            # Добавляем в пайлоад картинку и отправляем
            self.task_payload["task"].update(
                {"body": base64.b64encode(captcha_image.read()).decode("utf-8")}
            )
            # Отправляем на антикапча изображение капчи и другие парметры,
            # в результате получаем JSON ответ содержащий номер решаемой капчи

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    create_task_url, json=self.task_payload
                ) as resp:
                    captcha_id = await resp.json()

        # удаляем файл капчи
        os.remove(os.path.join(img_path, "im-{0}.png".format(image_hash)))
        return captcha_id

    async def __read_captcha_image_file(
        self, content: bytes, content_type: str = "file"
    ):
        """
        Функция отвечает за чтение уже сохранённого файла или файла в уодировке base64
        :param content: Параметр строка-путь указывающий на изображение капчи для отправки её на сервер
        :param content_type: Тип переданной переменной. Возможны варианты: `file` и `base64`
        :return: Возвращает ID капчи
        """
        try:
            if content_type == "file":
                with open(content, "rb") as captcha_image:
                    # Добавляем в пайлоад картинку и отправляем
                    self.task_payload["task"].update(
                        {"body": base64.b64encode(captcha_image.read()).decode("utf-8")}
                    )
            elif content_type == "base64":
                self.task_payload["task"].update({"body": content})
            else:
                raise ValueError(
                    "\nПередан неверный формат файла."
                    f"\n\tВозможные варинты: `file` и `base64`. Вы передали - `{content_type}`"
                    f"\nWrong `content_type` parameter. Valid params: `file` or `base64`."
                    f"\n\tYour param - `{content_type}`"
                )
            # Отправляем на антикапча изображение капчи и другие парметры,
            # в результате получаем JSON ответ содержащий номер решаемой капчи
            captcha_id = requests.post(create_task_url, json=self.task_payload).json()
        except (IOError, FileNotFoundError) as err:
            raise ReadError(err)

        return captcha_id

    # Работа с капчёй
    async def captcha_handler(
        self,
        captcha_link: str = None,
        captcha_file: str = None,
        captcha_base64: str = None,
    ):
        """
		Метод получает от вас ссылку на изображение, скачивает его, отправляет изображение на сервер
		RuCaptcha, дожидается решения капчи и вовзращает вам результат
		:param captcha_link: Ссылка на изображение
		:return: Возвращает весь ответ сервера JSON-строкой.
		"""
        # если был передан линк на локальный скачаный файл
        if captcha_file:
            captcha_id = await self.__read_captcha_image_file(
                captcha_file, content_type="file"
            )
        elif captcha_base64:
            captcha_id = await self.__read_captcha_image_file(
                captcha_base64, content_type="base64"
            )
        elif captcha_link:
            # согласно значения переданного параметра выбираем функцию для сохранения изображения
            if self.save_format == "const":
                captcha_id = await self.__image_const_saver(captcha_link)
            elif self.save_format == "temp":
                captcha_id = await self.__image_temp_saver(captcha_link)
        else:
            raise ParamError(
                additional_info="""You must set one of param - `captcha_file/captcha_base64/captcha_link`.\n
                                                Вы должны задать один из параметров - `captcha_file/captcha_base64/captcha_link`."""
            )

        # Проверка статуса создания задачи, если создано без ошибок - извлекаем ID задачи, иначе возвращаем ответ сервера
        if captcha_id["errorId"] == 0:
            captcha_id = captcha_id["taskId"]
            self.result_payload.update({"taskId": captcha_id})
        else:
            return captcha_id

        # если передан параметр `callbackUrl` - не ждём решения капчи а возвращаем незаполненный ответ
        if self.task_payload.get("callbackUrl"):
            return self.result_payload

        else:
            # Ждем решения капчи
            await asyncio.sleep(self.sleep_time)
            return await get_async_result(
                result_payload=self.result_payload, sleep_time=self.sleep_time
            )
