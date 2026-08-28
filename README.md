# 🖥️ web_bot

Веб-панель для управления компьютером из браузера: текстовые команды в стиле голосового ассистента Кеша, трансляция экрана в реальном времени и загрузка файлов. Сервер написан на FastAPI, фронтенд на чистом HTML, CSS и JavaScript.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

## Возможности

- **Чат с командами.** Например: «найди в ютубе …», «погода», «открой [приложение]», «сверни окно», «громкость 50», «скриншот». Полный список с категориями есть прямо в интерфейсе.
- **Трансляция экрана.** MJPEG-поток до ~30 кадров в секунду, нужен только Pillow, OpenCV не требуется.
- **Загрузка файлов** на компьютер через браузер в папку `uploads/`.
- **Мини-игры:** камень-ножницы-бумага, виселица, викторина, крестики-нолики и другие.
- **Вход по паролю.** Каждый запрос к API проверяется по заголовку `X-Password`.

## Как устроено

```
браузер (frontend/)  ──HTTP──►  FastAPI (backend/main.py)  ──►  commands.py
  чат, трансляция,               /login, /api/command,           распознаёт команду
  загрузка файлов                /api/upload, /stream            и выполняет её на ПК
```

## Установка

Работает на Windows: для громкости и управления окнами нужны `pycaw`, `keyboard` и `mouse`.

```powershell
git clone https://github.com/Naruto456y/web_bot.git
cd web_bot
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Запуск

```powershell
$env:WEB_BOT_PASSWORD = "придумайте_пароль"
$env:OPENWEATHER_API_KEY = "ключ_openweathermap"   # необязательно, нужен для команды «погода»
python -m backend.main
```

Откройте http://localhost:8000 и войдите с этим паролем.

> ⚠️ Сервер слушает все сетевые интерфейсы (`0.0.0.0`), поэтому панель видна в локальной сети. Задайте надёжный пароль и не открывайте порт 8000 в интернет.

## Структура

```
backend/
  main.py       FastAPI: вход, API команд, загрузка файлов, трансляция экрана
  commands.py   распознавание и выполнение команд
frontend/
  login.html    страница входа
  chat.html     панель управления
  script.js     логика чата, трансляции и загрузки
  style.css     стили
```

## Автор

Yusuf ([@Naruto456y](https://github.com/Naruto456y)). Лицензия [MIT](LICENSE).
