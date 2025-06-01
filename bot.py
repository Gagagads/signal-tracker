import asyncio
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

# 🔐 ЗАМЕНИ ЭТИ ДАННЫЕ НА СВОИ
API_ID = 12345678  # ← твой API ID
API_HASH = 'your_api_hash_here'  # ← твой API Hash
BOT_TOKEN = '7639845168:AAG770ffbEQRP4W-Qk2jcnoG5x--SjyuzA0'
TARGET_GROUP_ID = -4877016471
MENTION_USERNAME = '@Mytracksignal'

# Отслеживаемые каналы
CHANNEL_IDS = [
    -1002438264294, -1002400892367, -1002420417890,
    -1002048172508, -1002058755890, -1002146109187,
    -1002011050670, -1002084209596, -1002094849653,
    -1001891589065, -1001974198702, -1001840337788,
    -1002193485779, -1002202792246, -1002215306818
]

client = TelegramClient('anon', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
last_success = {}

async def check_signals():
    while True:
        for channel_id in CHANNEL_IDS:
            try:
                history = await client(GetHistoryRequest(
                    peer=channel_id,
                    limit=10,
                    offset_date=None,
                    offset_id=0,
                    max_id=0,
                    min_id=0,
                    add_offset=0,
                    hash=0
                ))

                messages = history.messages
                recent = [m.message for m in messages if m.message]

                if len(recent) < 3:
                    continue

                valid = 0
                for msg in recent:
                    msg_upper = msg.upper()
                    if 'ДАГОН' in msg_upper:
                        valid = 0
                    elif 'ПЛЮС' in msg_upper:
                        valid += 1
                    else:
                        valid = 0

                    if valid >= 3:
                        break

                if valid >= 3 and last_success.get(channel_id) != messages[0].id:
                    last_success[channel_id] = messages[0].id
                    await client.send_message(
                        TARGET_GROUP_ID,
                        f"✅ В канале ID {channel_id} зафиксировано 3 плюса подряд без догонов. {MENTION_USERNAME}"
                    )

            except Exception as e:
                print(f"Ошибка в канале {channel_id}: {e}")

        await asyncio.sleep(60)

async def heartbeat():
    while True:
        await client.send_message(
            TARGET_GROUP_ID,
            "🤖 Бот активен. Ожидает сигналы..."
        )
        await asyncio.sleep(300)  # 5 минут

async def main():
    await asyncio.gather(check_signals(), heartbeat())

with client:
    client.loop.run_until_complete(main())
