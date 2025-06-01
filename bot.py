from telethon import TelegramClient, events
import asyncio

# 👉 ВСТАВЬ свои данные:
api_id = 27133756
api_hash = '4a07d1675e7bc27fa7ceb273e05b679c'
session_name = 'anon'  # не трогай, это файл авторизации
target_chat_id = -4805234441  # Куда бот будет отправлять уведомления

# 👉 Каналы, которые слушаем (ID или username)
channel_ids = [
    -1002438264294,  # 🛢 Сырьевые товары 🛢 ОТС 1М
    -1002400892367,  # 🛢 Сырьевые товары 🛢 ОТС 2М
    -1002420417890,  # и так далее...
    -1002048172508,
    -1002058755890,
    -1002146109187,
    -1002011050670,
    -1002084209596,
    -1002094849653,
    -1001891589065,
    -1001974198702,
    -1001840337788,
    -1002193485779,
    -1002202792246,
    -1002215306818,
]

client = TelegramClient(session_name, api_id, api_hash)


@client.on(events.NewMessage(chats=channel_ids))
async def handler(event):
    text = event.raw_text.strip()
    channel = await event.get_chat()
    channel_name = channel.title or "Без имени"

    print(f"[{channel_name}] >> {text}")

    message_to_send = f"📥 <b>{channel_name}</b>\n\n{text}"
    await client.send_message(target_chat_id, message_to_send, parse_mode='html')


async def main():
    print("🤖 Бот запущен. Слушаю каналы...")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
