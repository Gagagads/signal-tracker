import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient, events
import re

api_id = 27481215  # ← Вставь свой актуальный API ID
api_hash = '75f495f542a5beb8ba632b70fc7ebf79'  # ← и API Hash
bot_token = '7639845168:AAG770ffbEQRP4W-Qk2jcnoG5x--SjyuzA0'
user_tag = '@Mytracksignal'

# Названия групп по ID
group_names = {
    -1002048172508: "💰Валютный рынок💰1М⌛️",
    -1002058755890: "💰Валютный рынок💰2М⌛️",
    -1002146109187: "💰Валютный рынок💰3М⌛️",
    -1001891589065: "💰Валютный рынок OTC💰1М⌛️",
    -1001974198702: "💰Валютный рынок OTC💰2М⌛️",
    -1001840337788: "💰Валютный рынок OTC💰3М⌛️",
    -1002011050670: "💰Акции ОТС💰1М⌛️",
    -1002084209596: "💰Акции ОТС💰2М⌛️",
    -1002094849653: "💰Акции ОТС💰3М⌛️",
    -1002193485779: "💰КРИПТА ОТС💰1М⌛️",
    -1002202792246: "💰КРИПТА ОТС💰2М⌛️",
    -1002215306818: "💰КРИПТА ОТС💰3М⌛️",
    -1002438264294: "🛢 Сырьевые товары 🛢 ОТС 1М",
    -1002400892367: "🛢 Сырьевые товары 🛢 ОТС 2М",
    -1002420417890: "🛢 Сырьевые товары 🛢 ОТС 3М"
}

client = TelegramClient('anon_session', api_id, api_hash).start(bot_token=bot_token)

plus_counter = {chat_id: 0 for chat_id in group_names}
triple_plus_log = {chat_id: 0 for chat_id in group_names}

# Варианты слова "догон"
dogon_variants = ['догон', 'догону', 'догоном', 'догонов', 'ко второму догону', 'второй догон']

# Проверка, нужно ли считать сообщение за чистый сигнал
def is_clean_signal(text):
    text = text.lower()
    if 'плюс' not in text:
        return False
    if any(d in text for d in dogon_variants):
        return False
    return True

@client.on(events.NewMessage(chats=list(group_names)))
async def handler(event):
    chat_id = event.chat_id
    message = event.raw_text.lower()

    # Если это сообщение содержит и "готовим" и "догон" — игнорируем
    if 'готовим' in message and any(d in message for d in dogon_variants):
        return

    # Если это чистый плюс
    if is_clean_signal(message):
        plus_counter[chat_id] += 1
        if plus_counter[chat_id] == 3:
            triple_plus_log[chat_id] += 1
            plus_counter[chat_id] = 0
            group = group_names.get(chat_id, "Неизвестная группа")
            await client.send_message(chat_id, f"🔥 {user_tag}, обнаружено 3 плюса подряд в группе: {group}")
    elif 'плюс' not in message:
        plus_counter[chat_id] = 0

# Сообщение "бот активен" каждые 5 минут
async def notify_alive():
    while True:
        now = datetime.now()
        for chat_id in group_names:
            try:
                await client.send_message(chat_id, "🤖 Бот активен. Ожидает сигналы...")
            except Exception:
                continue
        await asyncio.sleep(300)

# Ежедневная статистика
async def send_daily_stats():
    while True:
        now = datetime.now()
        target = now.replace(hour=23, minute=59, second=0, microsecond=0)
        if now > target:
            target += timedelta(days=1)
        await asyncio.sleep((target - now).total_seconds())

        text = "📊 Статистика за день:\n"
        for chat_id, count in triple_plus_log.items():
            name = group_names.get(chat_id, str(chat_id))
            text += f"{name} — {count} ситуаций\n"
            triple_plus_log[chat_id] = 0  # сброс
        for chat_id in group_names:
            try:
                await client.send_message(chat_id, text)
            except Exception:
                continue

async def main():
    await asyncio.gather(notify_alive(), send_daily_stats())

client.loop.create_task(main())
client.run_until_disconnected()
