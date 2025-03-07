import requests
from telegram import Bot
import asyncio

# Настройки
STEAM_API_KEY = '2F3CA6DB2EA1802F6C2B36BC903D5C13'
TELEGRAM_BOT_TOKEN = '7899819039:AAHodnXx0NI_o520rVU6rBzhfKKh03C3494'  # Токен вашего бота
GROUP_CHAT_ID = '-1002253163041'  # Chat ID вашей группы
STEAM_IDS = ['76561199350610044', '76561199044928778', '76561198977674430']  # Список Steam ID друзей (замените на реальные)
CHECK_INTERVAL = 300  # Проверка каждые 5 минут


def get_friends_status():
    url = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'
    params = {
        'key': STEAM_API_KEY,
        'steamids': ','.join(STEAM_IDS)
    }
    response = requests.get(url, params=params).json()
    print(f"Response from Steam API: {response}")
    return response['response']['players']


async def send_message():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    await bot.send_message(chat_id=GROUP_CHAT_ID,
                           text="🚛 Эй, братва, подтягивайся — ETS2 врубил! Каблук на газ, фуры вразвал, а чтоб скучно не было — лови волну: [Radio7](https://radio7.ru/?region=msk)")
    print("Message sent to Telegram group.")


async def main():
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