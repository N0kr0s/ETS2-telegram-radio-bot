# -*- coding: utf-8 -*-
import requests
from telegram import Bot
import asyncio
import configparser
import os

# Путь к конфигурационному файлу
CONFIG_FILE = 'config.ini'

def load_config():
    """
    Загружает настройки из конфигурационного файла.
    Если файл отсутствует, создает шаблон конфигурации.
    """
    config = configparser.ConfigParser()

    if not os.path.exists(CONFIG_FILE):
        # Создаем шаблон конфигурации, если файл не существует
        config['SETTINGS'] = {
            'STEAM_API_KEY': '<Ваш Steam API ключ>',
            'TELEGRAM_BOT_TOKEN': '<Токен вашего Telegram бота>',
            'GROUP_CHAT_ID': '<Chat ID вашей группы>',
            'STEAM_IDS': '<Steam ID друга 1>,<Steam ID друга 2>',
            'CHECK_INTERVAL': '300',
            'GAME_ID': '227300',  # ID игры ETS2
            'MESSAGE_TEXT': (
                "🚛 Эй, братва, подтягивайся — ETS2 врубил!\n"
                "Каблук на газ, фуры вразвал, а чтоб скучно не было — лови волну: "
                "[Radio7](https://radio7.ru/?region=msk)"
            )
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        print(f"Создан файл конфигурации: {CONFIG_FILE}")
        print("Заполните его перед запуском программы.")
        exit(1)

    # Читаем конфигурацию
    config.read(CONFIG_FILE, encoding='utf-8')

    return {
        'STEAM_API_KEY': config['SETTINGS']['STEAM_API_KEY'],
        'TELEGRAM_BOT_TOKEN': config['SETTINGS']['TELEGRAM_BOT_TOKEN'],
        'GROUP_CHAT_ID': config['SETTINGS']['GROUP_CHAT_ID'],
        'STEAM_IDS': [sid.strip() for sid in config['SETTINGS']['STEAM_IDS'].split(',')],
        'CHECK_INTERVAL': int(config['SETTINGS']['CHECK_INTERVAL']),
        'GAME_ID': config['SETTINGS']['GAME_ID'],  # ID игры
        'MESSAGE_TEXT': config['SETTINGS']['MESSAGE_TEXT']  # Текст сообщения
    }

def get_friends_status(steam_api_key, steam_ids):
    """
    Получает статус друзей через Steam Web API.
    Возвращает список игроков с их текущим состоянием.
    """
    url = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'
    params = {
        'key': steam_api_key,
        'steamids': ','.join(steam_ids)
    }
    response = requests.get(url, params=params).json()
    print(f"Response from Steam API: {response}")
    return response['response']['players']

async def send_message(bot_token, chat_id, message_text):
    """
    Отправляет сообщение в Telegram с уведомлением о запуске игры.
    Использует Markdown для форматирования текста.
    """
    bot = Bot(token=bot_token)
    await bot.send_message(
        chat_id=chat_id,
        text=message_text,
        parse_mode='Markdown'  # Важно: указываем Markdown для форматирования
    )
    print("Message sent to Telegram group.")

async def main():
    """
    Основной цикл программы.
    Проверяет активность друзей в Steam и отправляет уведомления в Telegram.
    """
    # Загрузка конфигурации
    config = load_config()
    STEAM_API_KEY = config['STEAM_API_KEY']
    TELEGRAM_BOT_TOKEN = config['TELEGRAM_BOT_TOKEN']
    GROUP_CHAT_ID = config['GROUP_CHAT_ID']
    STEAM_IDS = config['STEAM_IDS']
    CHECK_INTERVAL = config['CHECK_INTERVAL']
    GAME_ID = config['GAME_ID']
    MESSAGE_TEXT = config['MESSAGE_TEXT']

    global_status = False  # Глобальное состояние: играет ли кто-то в указанную игру

    while True:
        players = get_friends_status(STEAM_API_KEY, STEAM_IDS)
        print(f"Players status: {players}")

        # Проверяем, играет ли кто-то в указанную игру прямо сейчас
        current_status = any(player.get('gameid') == GAME_ID for player in players)

        # Если сейчас кто-то играет, а раньше никто не играл — отправляем сообщение
        if current_status and not global_status:
            print("Someone started playing the game. Sending message...")
            await send_message(TELEGRAM_BOT_TOKEN, GROUP_CHAT_ID, MESSAGE_TEXT)

        # Обновляем глобальное состояние
        global_status = current_status

        # Ждём перед следующей проверкой
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())