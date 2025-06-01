from telethon import TelegramClient, events
import asyncio
import re
import datetime

# Твои данные
api_id = 27133756
api_hash = '4a07d1675e7bc27fa7ceb273e05b679c'
session_name = 'anon'

# Куда присылать уведомления
target_chat_id = -4805234441
mention_username = '@Abvgd1d'  # ⚠️ Укажи свой юзернейм

# Отслеживаемые каналы
channel_ids = [
    -1002438264294, -1002400892367, -1002420417890,
    -1002048172508, -1002058755890, -1002146109187,
    -1002011050670, -1002084209596, -1002094849653,
    -1001891589065, -1001974198702, -1001840337788,
    -1002193485779, -1002202792246, -1002215306818,
]

# Хранилище для отслеживания подряд плюсов
plus_streaks = {}

# Ключевые слова догонов
dogon_keywords = ['догон', 'догона', 'догон-1', 'догон-2', 'второй догон', '1 догон', '2 догон', 'догонов', 'догону']

client = TelegramClient(session_name, api_id, api_hash)

def is_clean_plus(text):
    text_lower = text.lower()
    if 'плюс' in text_lower:
        for word in dogon_keywords:
            if word in text_lower:
                return False
        return True
    return False

@client.on(events.NewMessage(chats=channel_ids))
async def handler(event):
    text = event.raw_text.strip()
    channel = await event.get_chat()
    chat_id = event.chat_id
    channel_title = channel.title or "Без имени"

    if any(word in text.lower() for word in dogon_keywords) or 'минус' in text.lower():
        plus_streaks[chat_id] = 0
        return

    if is_clean_plus(text):
        plus_streaks[chat_id] = plus_streaks.get(chat_id, 0) + 1
        if plus_streaks[chat_id] == 3:
            await client.send_message(
                target_chat_id,
                f"{mention_username} ⚡ Плюсы: {channel_title}",
                parse_mode='html'
            )
            plus_streaks[chat_id] = 0

# Сообщение, подтверждающее, что бот жив
async def heartbeat():
    while True:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        await client.send_message(target_chat_id, f"⏰ {now} — 🤖 Бот работает и ожидает сигналы...")
        await asyncio.sleep(300)  # каждые 5 минут

async def main():
    print("🚀 Бот запущен")
    await asyncio.gather(client.run_until_disconnected(), heartbeat())

with client:
    client.loop.run_until_complete(main())
