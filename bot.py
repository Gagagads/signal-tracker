import asyncio
from telethon import TelegramClient, events
from datetime import datetime, time, timedelta

# ДАННЫЕ
api_id = 27481215
api_hash = '75f495f542a5beb8ba632b70fc7ebf79'
bot_token = '7639845168:AAG770ffbEQRP4W-Qk2jcnoG5x--SjyuzA0'
user_nickname = '@Mytracksignal'

# ID всех чатов
chat_ids = {
    -1002048172508: '💰Валютный рынок💰1М⌛️',
    -1002058755890: '💰Валютный рынок💰2М⌛️',
    -1002146109187: '💰Валютный рынок💰3М⌛️',
    -1001891589065: '💰Валютный рынок OTC💰1М⌛️',
    -1001974198702: '💰Валютный рынок OTC💰2М⌛️',
    -1001840337788: '💰Валютный рынок OTC💰3М⌛️',
    -1002011050670: '💰Акции ОТС💰1М⌛️',
    -1002084209596: '💰Акции ОТС💰2М⌛️',
    -1002094849653: '💰Акции ОТС💰3М⌛️',
    -1002193485779: '💰КРИПТА ОТС💰1М⌛️',
    -1002202792246: '💰КРИПТА ОТС💰2М⌛️',
    -1002215306818: '💰КРИПТА ОТС💰3М⌛️',
    -1002438264294: '🛢 Сырьевые товары 🛢 ОТС 1М',
    -1002400892367: '🛢 Сырьевые товары 🛢 ОТС 2М',
    -1002420417890: '🛢 Сырьевые товары 🛢 ОТС 3М',
}

# СЛОВА-ДОГОНЫ
dogon_words = ['догон', 'догона', 'догону', 'догоном', 'готовимся', 'готовимся ко']

# Счетчики
signal_counts = {chat_id: [] for chat_id in chat_ids}
triple_successes = []

# Клиент
client = TelegramClient('anon', api_id, api_hash).start(bot_token=bot_token)

# Проверка сообщений
def is_valid_signal(text):
    lowered = text.lower()
    return (
        'готовим' in lowered
        and not any(word in lowered for word in dogon_words)
    )

def is_positive_signal(text):
    return 'плюс' in text.lower()

@client.on(events.NewMessage(chats=list(chat_ids.keys())))
async def handler(event):
    chat_id = event.chat_id
    message = event.message.message

    if is_valid_signal(message):
        signal_counts[chat_id] = []
    elif is_positive_signal(message):
        signal_counts[chat_id].append(datetime.now())
        if len(signal_counts[chat_id]) >= 3:
            name = chat_ids.get(chat_id, 'Неизвестно')
            triple_successes.append((chat_id, datetime.now()))
            await client.send_message(
                chat_id,
                f'{user_nickname} 🚀 Обнаружено 3 плюса подряд в папке: {name}'
            )
            signal_counts[chat_id] = []

# Сообщение каждые 5 минут
async def periodic_message():
    while True:
        for chat_id in chat_ids:
            try:
                await client.send_message(chat_id, "🤖 Бот активен. Ожидает сигналы...")
            except:
                pass
        await asyncio.sleep(300)  # 5 минут

# Статистика в 23:59
async def send_daily_report():
    while True:
        now = datetime.now()
        target = datetime.combine(now.date(), time(23, 59))
        if now > target:
            target += timedelta(days=1)
        await asyncio.sleep((target - now).total_seconds())

        count = len(triple_successes)
        for chat_id in chat_ids:
            try:
                await client.send_message(
                    chat_id,
                    f"📊 За сутки обнаружено {count} ситуаций с 3+ сигналами подряд."
                )
            except:
                pass
        triple_successes.clear()

async def main():
    await asyncio.gather(
        periodic_message(),
        send_daily_report()
    )

client.loop.create_task(main())
client.run_until_disconnected()
