# -*- coding: utf-8 -*-
import requests
from telegram import Bot
import asyncio

# Настройки (замените шаблоны на реальные данные)
STEAM_API_KEY = '<Ваш Steam API ключ>'  # Получите его на https://steamcommunity.com/dev/apikey
TELEGRAM_BOT_TOKEN = '<Токен вашего Telegram бота>'  # Создайте бота через @BotFather в Telegram
GROUP_CHAT_ID = '<Chat ID вашей группы>'  # Добавьте бота в группу и получите chat_id (например, через getUpdates)
STEAM_IDS = ['<Steam ID друга 1>', '<Steam ID друга 2>']  # Укажите Steam ID ваших друзей через запятую
CHECK_INTERVAL = 300  # Интервал проверки в секундах (например, 300 для 5 минут)

def get_friends_status():
    """
    Получает статус друзей через Steam Web API.
    Возвращает список игроков с их текущим состоянием.
    """
    url = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'
    params = {
        'key': STEAM_API_KEY,
        'steamids': ','.join(STEAM_IDS)
    }
    response = requests.get(url, params=params).json()
    print(f"Response from Steam API: {response}")
    return response['response']['players']

async def send_message():
    """
    Отправляет сообщение в Telegram с уведомлением о запуске ETS2.
    Использует Markdown для форматирования текста и создания кликабельной ссылки.
    """
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    await bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text=(
            "🚛 Эй, братва, подтягивайся — ETS2 врубил!\n"
            "Каблук на газ, фуры вразвал, а чтоб скучно не было — лови волну: "
            "[Radio7](https://radio7.ru/?region=msk)"
        ),
        parse_mode='Markdown'  # Важно: указываем Markdown для форматирования
    )
    print("Message sent to Telegram group.")

async def main():
    """
    Основной цикл программы.
    Проверяет активность друзей в Steam и отправляет уведомления в Telegram.
    """
    global_status = False  # Глобальное состояние: играет ли кто-то в ETS2

    while True:
        players = get_friends_status()
        print(f"Players status: {players}")

        # Проверяем, играет ли кто-то в ETS2 прямо сейчас
        current_status = any(player.get('gameid') == '227300' for player in players)

        # Если сейчас кто-то играет, а раньше никто не играл — отправляем сообщение
        if current_status and not global_status:
            print("Someone started playing ETS2. Sending message...")
            await send_message()

        # Обновляем глобальное состояние
        global_status = current_status

        # Ждём перед следующей проверкой
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())