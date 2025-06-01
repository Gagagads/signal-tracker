import asyncio
from telethon import TelegramClient, events
import datetime

# === Настройки ===
api_id = 27481215
api_hash = '75f495f542a5beb8ba632b70fc7ebf79'
bot_token = '7639845168:AAG770ffbEQRP4W-Qk2jcnoG5x--SjyuzA0'
channel_ids = [
    -1002048172508, -1002058755890, -1002146109187,
    -1001891589065, -1001974198702, -1001840337788,
    -1002011050670, -1002084209596, -1002094849653,
    -1002193485779, -1002202792246, -1002215306818,
    -1002438264294, -1002400892367, -1002420417890
]

# Группа, куда слать результат
report_chat_id = -4877016471
user_tag = "@Mytracksignal"

# Слова, по которым игнорируем сообщения
dogon_words = ['догон', 'дагон', 'догону', 'дагону', 'догоном', 'дагоном', 'догонам', 'дагонам', 'догонов', 'дагонов']

# Храним историю для каждого канала
history = {}

# Инициализация клиента
client = TelegramClient('anon', api_id, api_hash).start(bot_token=bot_token)

# === Обработка сообщений ===
@client.on(events.NewMessage(chats=channel_ids))
async def handler(event):
    message = event.message.message.lower()
    chat_id = event.chat_id

    if any(word in message for word in dogon_words):
        return  # есть догон, игнорируем

    if '+' not in message:
        return  # нет плюса, игнорируем

    if chat_id not in history:
        history[chat_id] = []

    history[chat_id].append(datetime.datetime.now())

    # Оставим только последние 3
    history[chat_id] = history[chat_id][-3:]

    if len(history[chat_id]) == 3:
        delta = (history[chat_id][-1] - history[chat_id][0]).total_seconds()
        if delta <= 3600:  # допустим, максимум за 1 час
            await client.send_message(report_chat_id, f"✅ В канале {event.chat.title} 3 плюса подряд без догонов\n{user_tag}")
            history[chat_id] = []

# === Периодическое сообщение ===
async def heartbeat():
    while True:
        await client.send_message(report_chat_id, "☕ Бот работает, всё под контролем. Ждём входов...")
        await asyncio.sleep(300)  # каждые 5 минут

# === Запуск ===
async def main():
    asyncio.create_task(heartbeat())
    await client.run_until_disconnected()

client.loop.run_until_complete(main())
