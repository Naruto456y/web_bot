import os
import time
import random
import webbrowser
import threading
from datetime import datetime, timedelta, date
from pathlib import Path
import keyboard
import mouse
import AppOpener
import psutil
import requests
from urllib.parse import quote
from youtube_search import YoutubeSearch
import mouse
# Для скриншотов
try:
    from PIL import ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ---- Нейросеть (GigaChat) - опционально ----
try:
    from help_manager import GigaChat, Manager
    Manager.load_env()
    gig = GigaChat()
    GIGACHAT_AVAILABLE = True
except ImportError:
    GIGACHAT_AVAILABLE = False

# ---- Константы для команд ----
WAKE_WORDS = ['кеша', 'кеш', 'гоша', 'чебурек', 'алиса', 'кэш']
GREETINGS = [
    "Приветствую! Чем могу быть полезен?",
    "Здравствуйте! Готов к работе.",
    "Слушаю вас.",
    "Весь во внимании.",
    "Да, я здесь.",
    "Привет! Что нужно сделать?",
    "Здравствуй. Говори, что надо."
]
THANKS_RESPONSES = [
    "Рад стараться!", "Всегда пожалуйста!", "Это моя работа.", "Обращайтесь.", "Не за что.", "Для вас — что угодно."
]
OK_RESPONSES = [
    "Готово.", "Сделано.", "Исполнено.", "Уже сделал.", "Без проблем.", "Так точно."
]
SEARCH_RESPONSES = [
    "Вот что удалось найти.", "Результаты поиска перед вами.", "Ищу информацию.", "Открываю результаты.", "Секунду, ищу."
]

# ---- Функции для музыки (заглушки) ----
music_player = None
music_lock = threading.Lock()

def play_music_thread(command):
    print(f"Музыка: {command}")

# ---- Вспомогательные функции ----
BASE_DIR = Path(__file__).parent.parent

def get_random_response(lst):
    return random.choice(lst)

def get_weather(city="Москва"):
    api = os.environ.get("OPENWEATHER_API_KEY", "")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api}&units=metric&lang=ru"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        return f"{temp}°C, {desc}"
    except:
        return "Ошибка получения погоды"

def search_youtube(query):
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        if results:
            video_url = f"https://youtube.com{results[0]['url_suffix']}"
            webbrowser.open(video_url)
            return True
    except:
        return False

def set_system_volume(level):
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(max(0.0, min(1.0, level)), None)
        return True
    except:
        return False

def get_system_volume():
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        return volume.GetMasterVolumeLevelScalar()
    except:
        return 0.5

def change_volume_generic(direction, amount=0.1):
    cur = get_system_volume()
    if direction == 'up':
        new_vol = min(1.0, cur + amount)
    else:
        new_vol = max(0.0, cur - amount)
    if set_system_volume(new_vol):
        return new_vol
    return cur

def open_app_by_name(name):
    try:
        AppOpener.open(name, match_closest=True)
        return True
    except:
        return False

def remove_wake_words(text):
    for w in WAKE_WORDS:
        text = text.replace(w, '')
    return text.strip()

def start_file(name):
    full_path = BASE_DIR / name
    if full_path.exists():
        os.startfile(str(full_path))
        return True
    return False

# =============================================================================
# МАКСИМАЛЬНЫЙ ХАОС – БЕЗ НАСТРОЕК, ПРОСТО БЕЗУМИЕ
# =============================================================================
chaos_active = False
chaos_thread = None
chaos_stop_event = threading.Event()

def chaos_worker():
    """Бешеный хаос – минимальные задержки, все действия"""
    while not chaos_stop_event.is_set():
        # Случайная задержка 0.05–0.2 сек для бешеного темпа
        time.sleep(random.uniform(0.05, 0.2))
        
        action = random.randint(0, 10)  # 11 типов действий
        
        try:
            if action == 0:
                # Резкое движение мыши в случайную точку
                x = random.randint(0, 1920)
                y = random.randint(0, 1080)
                mouse.move(x, y, absolute=False, duration=0.01)
            elif action == 1:
                # Левый клик
                mouse.click('left')
            elif action == 2:
                # Правый клик
                mouse.click('right')
            elif action == 3:
                # Двойной клик
                mouse.double_click('left')
            elif action == 4:
                # Скролл вверх или вниз
                mouse.wheel(random.randint(-3, 3))
            elif action == 5:
                # Нажатие случайной клавиши
                keys = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
                        '0','1','2','3','4','5','6','7','8','9','space','enter','tab','escape','backspace','delete']
                keyboard.send(random.choice(keys))
            elif action == 6:
                # Alt+Tab (переключение окон)
                keyboard.send('alt+tab')
                time.sleep(0.05)
            elif action == 7:
                # Изменение громкости (рывками)
                try:
                    from ctypes import cast, POINTER
                    from comtypes import CLSCTX_ALL
                    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                    devices = AudioUtilities.GetSpeakers()
                    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    volume = cast(interface, POINTER(IAudioEndpointVolume))
                    cur = volume.GetMasterVolumeLevelScalar()
                    new_vol = max(0.0, min(1.0, cur + random.uniform(-0.3, 0.3)))
                    volume.SetMasterVolumeLevelScalar(new_vol, None)
                except:
                    pass
            elif action == 8:
                # Комбинация клавиш (например, Ctrl+C, Win+D)
                combos = ['ctrl+c', 'ctrl+v', 'win+d', 'win+e', 'win+i', 'alt+f4']
                keyboard.send(random.choice(combos))
            elif action == 9:
                # Перемещение мыши по спирали (быстро)
                for i in range(5):
                    if chaos_stop_event.is_set():
                        break
                    offset = i * 10
                    mouse.move(offset, 0, absolute=False, duration=0.01)
                    mouse.move(0, offset, absolute=False, duration=0.01)
                    mouse.move(-offset, 0, absolute=False, duration=0.01)
                    mouse.move(0, -offset, absolute=False, duration=0.01)
            elif action == 10:
                # Случайное нажатие правой кнопки с последующим скроллом
                mouse.click('right')
                time.sleep(0.02)
                mouse.wheel(random.randint(-2, 2))
        except Exception as e:
            print(f"Chaos error: {e}")

def start_chaos():
    global chaos_active, chaos_thread, chaos_stop_event
    if chaos_active:
        return "Хаос уже запущен (и он безумный!)"
    chaos_stop_event.clear()
    chaos_thread = threading.Thread(target=chaos_worker, daemon=True)
    chaos_thread.start()
    chaos_active = True
    return "🔥 ХАОС АКТИВИРОВАН! Компьютер сходит с ума!"

def stop_chaos():
    global chaos_active, chaos_stop_event
    if not chaos_active:
        return "Хаос не запущен"
    chaos_stop_event.set()
    chaos_active = False
    return "⏹️ Хаос остановлен"

# =============================================================================
# ОСНОВНАЯ ЛОГИКА КОМАНД
# =============================================================================
def find_command(text: str) -> str:
    clean = text.lower().strip()
    
    # Приветствия и прощания
    if any(w in clean for w in ['пока', 'выход', 'стоп бот', 'выключись']):
        if 'комп' in clean:
            os.system("shutdown /s /t 10")
            return "Выключаю компьютер через 10 секунд"
        else:
            return "До свидания!"
    if any(w in clean for w in ['привет', 'здравствуй', 'добрый день', 'добрый вечер', 'доброе утро', 'приветствую', 'хай', 'хелло', 'здарова']):
        return get_random_response(GREETINGS)
    if any(w in clean for w in ['как дела', 'как жизнь', 'как сам', 'как настроение', 'как поживаешь', 'как оно']):
        return "Всё отлично! Готов к работе. Жду ваших команд!"
    if any(w in clean for w in ['молодец', 'красава', 'респект', 'спасибо', 'благодарю']):
        return get_random_response(THANKS_RESPONSES)
    if any(w in clean for w in ['скриншот', 'сделай скрин', 'заскринь', 'сфоткай экран']):
        if PIL_AVAILABLE:
            screenshot = ImageGrab.grab()
            filename = f"screenshot_{int(time.time())}.png"
            path = BASE_DIR / "uploads" / filename
            screenshot.save(path)
            return f"Скриншот сохранён: /uploads/{filename}"
        else:
            return "Библиотека Pillow не установлена"

    # ---------- Управление мышью (стрелки) ----------
    try:
        if 'вверх' in clean and 'скролл' not in clean:
            mouse.move(0, -50, absolute=False, duration=0.1)
            return "Мышь вверх"
        if 'вниз' in clean and 'скролл' not in clean:
            mouse.move(0, 50, absolute=False, duration=0.1)
            return "Мышь вниз"
        if 'влево' in clean:
            mouse.move(-50, 0, absolute=False, duration=0.1)
            return "Мышь влево"
        if 'вправо' in clean:
            mouse.move(50, 0, absolute=False, duration=0.1)
            return "Мышь вправо"
        if 'левый клик' in clean:
            mouse.click('left')
            return "Левый клик"
        if 'правый клик' in clean:
            mouse.click('right')
            return "Правый клик"
        if 'скролл вверх' in clean:
            mouse.wheel(1)
            return "Скролл вверх"
        if 'скролл вниз' in clean:
            mouse.wheel(-1)
            return "Скролл вниз"
    except Exception as e:
        return f"Ошибка мыши: {e}"

    # ---------- Напечатай текст ----------
    if clean.startswith('напечатай'):
        text_to_type = clean.replace('напечатай', '').strip()
        if text_to_type:
            keyboard.write(text_to_type)
            return f"Напечатал: {text_to_type}"
        else:
            return "Что напечатать?"

    # ---------- Нажми клавишу ----------
    if clean.startswith('нажми клавишу'):
        key = clean.replace('нажми клавишу', '').strip()
        if key:
            keyboard.send(key)
            return f"Нажал клавишу: {key}"
        else:
            return "Какую клавишу нажать?"

    # ---------- МУЗЫКА ----------
    if any(w in clean for w in ['музык', 'музыка', 'музон', 'трек', 'песня']) and not any(w in clean for w in ['волна', 'волну', 'избранное', 'лайк', 'дизлайк']):
        query = clean
        for w in ['музык', 'музыка', 'музон', 'трек', 'песня']:
            query = query.replace(w, '')
        query = query.strip()
        if query:
            threading.Thread(target=play_music_thread, args=(f"track:{query}",), daemon=True).start()
            return f"Ищу и включаю: {query}"
        else:
            threading.Thread(target=play_music_thread, args=("wave",), daemon=True).start()
            return "Включаю..."
    if any(w in clean for w in ['волна', 'волну', 'избранное', 'любимое']):
        threading.Thread(target=play_music_thread, args=("wave",), daemon=True).start()
        return "Загружаю..."

    # Поиск
    if any(w in clean for w in ['найди в ютуби', 'поищи в ютубе', 'видео в ютубе']):
        query = clean
        for w in ['найди в ютуби', 'поищи в ютубе', 'видео в ютубе']:
            query = query.replace(w, '')
        query = query.strip()
        if query:
            search_youtube(query)
            return "Вот что удалось найти на YouTube"
        return "Что искать?"
    if 'youtube' in clean and not any(w in clean for w in ['найди', 'поищи', 'видео']):
        webbrowser.open('https://youtube.com')
        return get_random_response(OK_RESPONSES)
    if any(w in clean for w in ['найди', 'поищи', 'погугли', 'загугли', 'поиск']):
        query = clean
        for w in ['найди', 'поищи', 'погугли', 'загугли', 'поиск']:
            query = query.replace(w, '')
        query = query.strip()
        if query:
            webbrowser.open(f'https://yandex.ru/search/?text={query}')
            return get_random_response(SEARCH_RESPONSES)
        return "Что искать?"
    if any(w in clean for w in ['погода', 'какая погода', 'что на улице', 'температура']):
        return get_weather()
    if any(w in clean for w in ['выключи компьютер', 'шатдаун', 'выруби комп']):
        os.system("shutdown /s /t 10")
        return "Выключаю компьютер через 10 секунд"
    if any(w in clean for w in ['перезагрузка', 'ребут', 'рестарт']):
        os.system("shutdown /r /t 5")
        return "Перезагружаю компьютер"
    if any(w in clean for w in ['спящий режим', 'уснуть', 'спать']):
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return "Ухожу в спящий режим"
    if any(w in clean for w in ['заблокируй компьютер', 'блокировка', 'блокни']):
        os.system("rundll32.exe user32.dll,LockWorkStation")
        return "Экран заблокирован"
    if any(w in clean for w in ['время', 'который час', 'сколько время', 'времени']):
        return f"Сейчас {datetime.now().strftime('%H:%M')}"
    if any(w in clean for w in ['батарея', 'заряд', 'уровень батареи', 'cостояние']):
        battery = psutil.sensors_battery()
        if battery:
            status = "заряжается" if battery.power_plugged else "от батареи"
            return f"Батарея {status}. Уровень: {battery.percent}%"
        return "Информация о батарее недоступна"
    if any(w in clean for w in ['bluetooth', 'блютуз']):
        keyboard.send('win+a')
        time.sleep(0.2)
        keyboard.send('right')
        time.sleep(0.1)
        keyboard.send('enter')
        time.sleep(0.1)
        keyboard.send('win+a')
        return "Переключаю Bluetooth"
    if any(w in clean for w in ['игры', 'поиграть', 'яндекс игры']):
        webbrowser.open('https://yandex.ru/games/')
        return "Открываю Яндекс Игры"
    if any(w in clean for w in ['открой вс код', 'открой visual studio code', 'открой vs code', 'открой визуалку']):
        keyboard.send('win+1')
        return "Открываю Visual Studio Code"
    if 'открой' in clean:
        app = clean.replace('открой', '').strip()
        if app:
            if open_app_by_name(app):
                return f"Открываю {app}"
            return "Не удалось открыть"
        return "Что открыть?"
    if 'закрой' in clean:
        app = clean.replace('закрой', '').strip()
        if app:
            try:
                AppOpener.close(app, match_closest=True)
                return f"Закрываю {app}"
            except:
                return "Не удалось закрыть"
        return "Что закрыть?"
    if any(w in clean for w in ['браузер', 'интернет', 'яндекс']):
        if 'яндекс' in clean:
            try:
                os.startfile(os.path.join(os.path.expanduser("~"), "OneDrive", "Рабочий стол", "Yandex.lnk"))
            except:
                webbrowser.open('https://yandex.ru')
        else:
            webbrowser.open('https://yandex.ru')
        time.sleep(0.3)
        keyboard.send('win+up')
        return "Браузер открыт"
    if any(w in clean for w in ['проводник', 'файловый менеджер', 'папка']):
        keyboard.send('win+e')
        return "Проводник открыт"
    if any(w in clean for w in ['настройки', 'параметры']):
        keyboard.send('win+i')
        return "Настройки открыты"
    if any(w in clean for w in ['сверни', 'свернуть']):
        keyboard.send('win+down')
        return get_random_response(OK_RESPONSES)
    if any(w in clean for w in ['закрой окно', 'закрыть окно']):
        keyboard.send('alt+f4')
        return get_random_response(OK_RESPONSES)
    if any(w in clean for w in ['камера', 'селфи', 'сделай фото']):
        keyboard.send('win+2')
        time.sleep(1.5)
        keyboard.send('space')
        return "Селфи сделано"
    if 'громкость' in clean and not any(w in clean for w in ['громче', 'тише']):
        if 'макс' in clean:
            set_system_volume(1.0)
            return "Максимальная громкость"
        elif 'мин' in clean:
            set_system_volume(0.0)
            return "Минимальная громкость"
        else:
            try:
                vol = int(''.join(filter(str.isdigit, clean)))
                set_system_volume(vol / 100)
                return f"Громкость {vol}%"
            except:
                return "Не удалось установить громкость"
    if 'громче' in clean:
        change_volume_generic('up')
        return "Громче"
    if 'тише' in clean:
        change_volume_generic('down')
        return "Тише"
    # Переводы
    if any(w in clean for w in ['переведи на английский']):
        query = clean.replace('переведи на английский', '').strip()
        if query:
            if GIGACHAT_AVAILABLE:
                ans = gig.ask_gigachat(f'Переведи на английский: {query}. Без объяснений.')
                return ans
            else:
                return "Модуль GigaChat не установлен."
        return "Что перевести?"
    if any(w in clean for w in ['переведи на русский']):
        query = clean.replace('переведи на русский', '').strip()
        if query:
            if GIGACHAT_AVAILABLE:
                ans = gig.ask_gigachat(f'Переведи на русский: {query}. Без объяснений.')
                return ans
            else:
                return "Модуль GigaChat не установлен."
        return "Что перевести?"
    if any(w in clean for w in ['нарисуй', 'покажи картинку', 'изображение']):
        query = clean
        for w in ['нарисуй', 'покажи картинку', 'изображение']:
            query = query.replace(w, '')
        query = query.strip()
        if query:
            webbrowser.open(f'https://yandex.ru/images/search?text={quote(query)}')
            return "Ищу картинки"
        return "Что нарисовать?"
    # Умный дом
    if any(w in clean for w in ['включи свет', 'свет включи']):
        webbrowser.open('https://alice.yandex.ru/')
        time.sleep(2)
        mouse.click(737, 503)
        time.sleep(0.1)
        keyboard.write('Включи светильник')
        keyboard.send('Enter')
        return "Свет включён"
    if any(w in clean for w in ['выключи свет', 'свет выключи']):
        webbrowser.open('https://alice.yandex.ru/')
        time.sleep(2)
        mouse.click(737, 503)
        time.sleep(0.1)
        keyboard.write('Выключи светильник')
        keyboard.send('Enter')
        return "Свет выключен"
    # Таймер
    if any(w in clean for w in ['поставь таймер', 'таймер', 'засеки время']):
        duration = clean
        for w in ['поставь таймер на', 'поставь таймер', 'таймер', 'засеки время']:
            duration = duration.replace(w, '')
        duration = duration.replace('минуту', '').replace('минут', '').replace('минуты', '').strip()
        if duration.isdigit():
            if start_file('Media/timer.py'):
                time.sleep(3)
                keyboard.write(duration)
                keyboard.send('Enter')
                return f"Таймер на {duration} минут запущен"
            else:
                return "Файл таймера не найден"
        return "На сколько минут?"
    if any(w in clean for w in ['телефон', 'звонок', 'позвони']):
        keyboard.send('win+3')
        time.sleep(4)
        mouse.move(299, 180)
        time.sleep(0.1)
        mouse.click('left')
        time.sleep(0.1)
        mouse.move(350, 129)
        time.sleep(0.1)
        mouse.click('left')
        return "Звоню..."
    if any(w in clean for w in ['дипси', 'deepseek', 'чат gpt']):
        webbrowser.open('https://chat.deepseek.com/')
        return "Открываю DeepSeek"
    if any(w in clean for w in ['переводчик', 'перевести']):
        webbrowser.open('https://translate.yandex.ru/')
        return get_random_response(OK_RESPONSES)
    if any(w in clean for w in ['дз', 'домашнее задание', 'домашка']):
        webbrowser.open('https://school.mos.ru/diary/homeworks/')
        return "Домашнее задание открыто"
    if any(w in clean for w in ['оценки', 'отметки']):
        webbrowser.open('https://school.mos.ru/diary/marks/current-marks')
        return "Оценки открыты"
    if any(w in clean for w in ['расписание', 'уроки на завтра']):
        tomorrow = date.today() + timedelta(days=1)
        webbrowser.open(f'https://school.mos.ru/diary/schedules/day/?date={tomorrow.strftime("%d-%m-%Y")}')
        return "Расписание на завтра"

    # ---- ХАОС (максимальный, без настроек) ----
    if 'хаос' in clean:
        if 'стоп' in clean:
            return stop_chaos()
        else:
            return start_chaos()

    # Если ничего не подошло – возвращаем пустую строку
    return ""

def handle_command(text: str) -> str:
    text = text.lower().strip()
    try:
        if text.startswith("ответь") or text.startswith("спроси") or text.startswith("скажи"):
            if GIGACHAT_AVAILABLE:
                query = text.replace("ответь", "").replace("спроси", "").replace("скажи", "").strip()
                if query:
                    try:
                        ans = gig.ask_gigachat(f'Кратко ответь: {query}')
                        return ans
                    except:
                        return "Ошибка нейросети"
                else:
                    return "Что спросить?"
            else:
                return "Модуль GigaChat не установлен."

        cleant = remove_wake_words(text)
        command = find_command(cleant)
        if command:
            return command

        if GIGACHAT_AVAILABLE:
            try:
                fixed = gig.ask_gigachat(f"Исправь все ошибки, очисти текст и пойми смысл. Вот текст: {cleant}. Верни только исправленный текст.")
                command2 = find_command(fixed)
                if command2:
                    return command2
            except:
                pass
        return "Не понял команду. Попробуйте другую."

    except Exception as e:
        print(f"[error] {e}")
        return "Ошибка обработки команды"

# ---- Функция execute_command, вызываемая из main.py ----
def execute_command(text: str):
    result = handle_command(text)
    image_url = None
    if result.startswith("Скриншот сохранён"):
        parts = result.split(": ")
        if len(parts) > 1:
            image_url = parts[1]
    return result, image_url

# ---- Категории команд (для справки) ----
COMMAND_CATEGORIES = {
    "🤝 Основные": [
        "привет – поздороваться",
        "как дела – узнать состояние",
        "молодец – похвалить"
    ],
    "🌐 Интернет и поиск": [
        "найди [запрос] – поиск в Яндексе",
        "найди в ютубе [запрос] – видео на YouTube",
        "youtube – открыть YouTube",
        "погода – погода в Москве",
        "переводчик – открыть переводчик"
    ],
    "🎮 Игры": [
        "камень ножницы бумага – запустить игру",
        "виселица – запустить игру",
        "викторина – запустить игру",
        "квест – запустить игру",
        "крестики-нолики – запустить игру",
        "угадай число – запустить игру"
    ],
    "💻 Система": [
        "открой [приложение] – открыть программу",
        "закрой [приложение] – закрыть программу",
        "открой проводник – открыть файловый менеджер",
        "открой настройки – открыть настройки Windows",
        "сверни окно – свернуть текущее окно",
        "закрой окно – закрыть текущее окно",
        "вниз – скролл вниз",
        "верх – скролл вверх",
        "левый клик – клик левой кнопкой",
        "правый клик – клик правой кнопкой",
        "селфи – сделать снимок с веб-камеры",
        "дай скрин – сделать скриншот экрана"
    ],
    "🎵 Музыка": [
        "музыка [название] – поиск и включение в Яндекс.Музыке",
        "моя волна – включить плейлист",
        "дальше – следующий трек",
        "стоп – пауза",
        "предыдущий – предыдущий трек",
        "лайк – добавить в избранное",
        "дизлайк – убрать из рекомендаций"
    ],
    "🔊 Громкость": [
        "громче – увеличить громкость",
        "тише – уменьшить громкость",
        "громкость [0-100] – установить громкость"
    ],
    "🕒 Информация": [
        "время – текущее время",
        "дата – сегодняшняя дата",
        "батарея – состояние батареи"
    ],
    "⚙️ Управление ПК": [
        "выключи компьютер – выключение через 10 сек",
        "перезагрузка – перезагрузка",
        "спящий режим – спящий режим",
        "заблокируй компьютер – блокировка"
    ],
    "📚 Учёба": [
        "дз – открыть домашнее задание (школа)",
        "оценки – открыть оценки",
        "расписание – расписание на завтра"
    ],
    "🔧 Специальные": [
        "переведи на английский [текст] – перевод",
        "переведи на русский [текст] – перевод",
        "нарисуй [запрос] – поиск картинок",
        "включи свет – включить светильник (умный дом)",
        "выключи свет – выключить светильник",
        "поставь таймер на [минуты] – запустить таймер",
        "телефон – позвонить (требуется настройка)",
        "bluetooth – переключить Bluetooth",
        "трансляция – включить прямую трансляцию экрана",
        "хаос – АКТИВИРОВАТЬ МАКСИМАЛЬНЫЙ ХАОС (без настроек!)",
        "стоп хаос – остановить хаос",
        "напечатай [текст] – напечатать текст",
        "нажми клавишу [клавиша] – нажать клавишу"
    ]
}

FLAT_COMMANDS = []
for cat, cmds in COMMAND_CATEGORIES.items():
    for cmd in cmds:
        FLAT_COMMANDS.append(cmd)