import asyncio
from telethon import TelegramClient, events
from datetime import datetime, timedelta
import re

# --- НАСТРОЙКИ ---
api_id = 27481215  # <-- замени на свой API ID
api_hash = '75f495f542a5beb8ba632b70fc7ebf79'  # <-- замени на свой API HASH
session_file = 'anon'  # файл сессии без .session

chat_ids = [
    -1002048172508, -1002058755890, -1002146109187,
    -1001891589065, -1001974198702, -1001840337788,
    -1002011050670, -1002084209596, -1002094849653,
    -1002193485779, -1002202792246, -1002215306818,
    -1002438264294, -1002400892367, -1002420417890
]

target_group_id = -4877016471  # <- ID твоей группы, куда бот отправляет уведомления
your_tag = '@Mytracksignal'    # <- твой Telegram @юзернейм

# --- ЛОГИКА ---
client = TelegramClient(session_file, api_id, api_hash)

# Хранилище по каждому чату: последние сигналы
chat_signal_log = {}

# Каждые 5 минут — сообщение "бот работает"
async def periodic_notify():
    while True:
        await client.send_message(target_group_id, "🤖 Бот активен и ожидает сигналов.")
        await asyncio.sleep(300)

def clean_text(text):
    return text.replace('\n', ' ').lower()

@client.on(events.NewMessage(chats=chat_ids))
async def handler(event):
    message_text = clean_text(event.raw_text)

    # Ищем сигнал без догонов
    if "дагон" in message_text:
        return  # пропускаем, если есть дагон

    if "+" not in message_text:
        return  # не плюс — не сигнал

    chat_id = event.chat_id
    now = datetime.now()

    if chat_id not in chat_signal_log:
        chat_signal_log[chat_id] = []

    # сохраняем сигнал
    chat_signal_log[chat_id].append(now)

    # оставляем только последние 15 минут
    chat_signal_log[chat_id] = [
        t for t in chat_signal_log[chat_id] if now - t < timedelta(minutes=15)
    ]

    if len(chat_signal_log[chat_id]) >= 3:
        await client.send_message(
            target_group_id,
            f"🚨 {your_tag} В чате {event.chat.title or chat_id} — 3 сигнала подряд без догонов!"
        )
        chat_signal_log[chat_id] = []  # сброс после уведомления

# --- ЗАПУСК ---
async def main():
    await client.start()
    print("Бот запущен")
    await asyncio.gather(
        client.run_until_disconnected(),
        periodic_notify()
    )

if __name__ == '__main__':
    asyncio.run(main())
