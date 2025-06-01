import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient, events
import re

api_id = 27481215
api_hash = "75f495f542a5beb8ba632b70fc7ebf79"  # <-- сюда вставь свой API_HASH
bot_token = "7639845168:AAG770ffbEQRP4W-Qk2jcnoG5x--SjyuzA0"
group_id = -4877016471  # ID твоей группы
mention_tag = "@Mytracksignal"

client = TelegramClient("anon", api_id, api_hash).start(bot_token=bot_token)

# Список ID каналов для отслеживания
tracked_channels = [
    -1002048172508, -1002058755890, -1002146109187,
    -1001891589065, -1001974198702, -1001840337788,
    -1002011050670, -1002084209596, -1002094849653,
    -1002193485779, -1002202792246, -1002215306818,
    -1002438264294, -1002400892367, -1002420417890
]

# Все формы слова «догон»
dogon_variants = ["догон", "догону", "догоном", "догоне", "догонов", "догона", "догону!"]

pure_plus_counter = 0
daily_counter = 0
skip_next = False

@client.on(events.NewMessage(chats=tracked_channels))
async def handler(event):
    global pure_plus_counter, skip_next, daily_counter

    msg = event.message.message.lower()

    if any(word in msg for word in dogon_variants):
        skip_next = True
        return

    if "плюс" in msg and not skip_next:
        pure_plus_counter += 1
        daily_counter += 1

        if pure_plus_counter == 3:
            await client.send_message(group_id, f"{mention_tag} ⚡ Обнаружены 3 плюса подряд без догонов!")
            pure_plus_counter = 0
    elif "плюс" in msg and skip_next:
        skip_next = False
        return
    elif any(word in msg for word in ["минус", "слив", "отмена"]):
        pure_plus_counter = 0
        skip_next = False

# Каждые 5 минут — сообщение, что бот работает
async def send_status():
    while True:
        await client.send_message(group_id, "✅ Бот активен и ожидает сигналы.")
        await asyncio.sleep(300)

# В 00:00 отправка статистики
async def send_daily_report():
    global daily_counter
    while True:
        now = datetime.now()
        midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
        await asyncio.sleep((midnight - now).seconds)
        await client.send_message(group_id, f"📊 За сутки было обнаружено {daily_counter} ситуаций с 3 плюсами подряд без догонов.")
        daily_counter = 0

async def main():
    await asyncio.gather(send_status(), send_daily_report())

client.loop.create_task(main())
client.run_until_disconnected()
