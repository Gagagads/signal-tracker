from telethon.sync import TelegramClient, events
import requests

# Авторизация для Telethon (твой Telegram-пользователь)
api_id = 27133766
api_hash = '40d7b357c572c7fa7cbe273e050c679c'

# Telegram Bot API — отправка сообщений в группу
bot_token = '7985290808:AAGle0Xeb8pHqWR-9tIqptPD_zQ-ZlahET0'
group_chat_id = -4805234441  # ID твоей Telegram-группы

# Названия каналов для отслеживания (ID + метки)
tracked_channels = {
    -1002438264294: "Сырьевые 1М",
    -1002400892367: "Сырьевые 2М",
    -1002420417890: "Сырьевые 3М",
    -1002048172508: "Валютный 1М",
    -1002058755890: "Валютный 2М",
    -1002146109187: "Валютный 3М",
    -1002011050670: "Акции ОТС 1М",
    -1002084209596: "Акции ОТС 2М",
    -1002094849653: "Акции ОТС 3М",
    -1001891589065: "Валютный OTC 1М",
    -1001974198702: "Валютный OTC 2М",
    -1001840337788: "Валютный OTC 3М",
    -1002193485779: "КРИПТА ОТС 1М",
    -1002202792246: "КРИПТА ОТС 2М",
    -1002215306818: "КРИПТА ОТС 3М"
}

# Храним историю по каждому каналу
state = {chat_id: [] for chat_id in tracked_channels}

# Инициализация Telethon клиента
client = TelegramClient('anon', api_id, api_hash)

# Функция отправки уведомлений через Telegram Bot API
def send_bot_message(text):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = {
        'chat_id': group_chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    requests.post(url, data=data)

# Обработка новых сообщений из каналов
@client.on(events.NewMessage(chats=list(tracked_channels.keys())))
async def handler(event):
    chat_id = event.chat_id
    msg = event.raw_text.strip()
    
    # 👁 Показываем всё в консоли (для отладки)
    print(f"[{tracked_channels[chat_id]}] >> {msg}")

    lower_msg = msg.lower()
    if "итог сигнала" in lower_msg and ("плюс" in lower_msg or "✅" in lower_msg):
        state[chat_id].append("plus")
    elif "итог сигнала" in lower_msg and ("догон" in lower_msg or "минус" in lower_msg):
        state[chat_id].append("fail")
    else:
        return

    state[chat_id] = state[chat_id][-5:]

    if state[chat_id][-3:] == ["plus", "plus", "plus"]:
        text = f"📢 <b>3 ПЛЮСА подряд</b> в канале: <b>{tracked_channels[chat_id]}</b>\n<i>Совет: зайти ПРОТИВ следующего сигнала.</i>"
        send_bot_message(text)
        state[chat_id] = []

# Запуск
with client:
    print("🤖 Бот запущен и слушает каналы...")
    client.run_until_disconnected()
