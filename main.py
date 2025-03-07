import requests
import asyncio
import configparser
from telegram import Bot
import sys
import os


def create_config_example():
    config = configparser.ConfigParser()
    config['Steam'] = {
        'api_key': 'ваш_Steam_API_ключ',
        'steam_ids': '76561199350610044,76561199044928778'
    }
    config['Telegram'] = {
        'bot_token': 'ваш_токен_бота',
        'group_chat_id': '-1002253163041'
    }
    config['Settings'] = {
        'check_interval': '300'
    }
    config['Message'] = {
        'text': '🚛 ETS2 запущен! Присоединяйтесь: [Radio7](https://radio7.ru/?region=msk)'
    }

    with open('config.txt', 'w') as configfile:
        config.write(configfile)
    print("Создан config.txt. Заполните его своими данными.")
    sys.exit()


if not os.path.exists('config.txt'):
    create_config_example()

config = configparser.ConfigParser()
config.read('config.txt')

STEAM_API_KEY = config['Steam']['api_key']
TELEGRAM_BOT_TOKEN = config['Telegram']['bot_token']
GROUP_CHAT_ID = config['Telegram']['group_chat_id']
STEAM_IDS = config['Steam']['steam_ids'].split(',')
CHECK_INTERVAL = int(config['Settings']['check_interval'])
MESSAGE_TEXT = config['Message']['text']


def get_friends_status():
    url = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'
    params = {
        'key': STEAM_API_KEY,
        'steamids': ','.join(STEAM_IDS)
    }
    response = requests.get(url, params=params).json()
    return response['response']['players']


async def send_message():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    await bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text=MESSAGE_TEXT,
        parse_mode='Markdown'
    )


async def main():
    global_status = False
    while True:
        players = get_friends_status()
        current_status = any(player.get('gameid') == '227300' for player in players)

        if current_status and not global_status:
            await send_message()
            global_status = True
        elif not current_status:
            global_status = False

        await asyncio.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())