import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient, events

# ==== НАСТРОЙКИ ====
api_id = 27481215
api_hash = '75f495f542a5beb8ba632b70fc7ebf79'
bot_token = '7639845168:AAG770ffbEQRP4W-Qk2jcnoG5x--SjyuzA0'
notify_user = '@Mytracksignal'

# ID всех папок (чатов), которые отслеживаются:
chat_ids = [
    -1002048172508, -1002058755890, -1002146109187,
    -1001891589065, -1001974198702, -1001840337788,
    -1002011050670, -1002084209596, -1002094849653,
    -1002193485779, -1002202792246, -1002215306818,
    -1002438264294, -1002400892367, -1002420417890
]

dogon_words = ['догон', 'догону', 'догоном', 'догоне', 'догонов']

client = TelegramClient('anon', api_id, api_hash).start(bot_token=bot_token)

# Хранение состояния для каждого чата
signal_state = {chat_id: {'ready': False, 'is_clean': True} for chat_id in chat_ids}
plus_streaks = {chat_id: [] for chat_id in chat_ids}
daily_stats = {chat_id: 0 for chat_id in chat_ids}

@client.on(events.NewMessage(chats=chat_ids))
async def handler(event):
    message = event.message.message.lower()
    chat_id = event.chat_id
    chat_title = (await event.get_chat()).title

    # Если сообщение содержит слово "готовим"
    if 'готовим' in message:
        signal_state[chat_id] = {'ready': True, 'is_clean': True}
        return

    # Если содержит догон — сбрасываем чистоту
    if any(word in message for word in dogon_words):
        signal_state[chat_id]['is_clean'] = False
        plus_streaks[chat_id] = []
        return

    # Если чистый сигнал активен и приходит "плюс"
    if signal_state[chat_id]['ready'] and signal_state[chat_id]['is_clean']:
        if 'плюс' in message:
            plus_streaks[chat_id].append(datetime.now())
            if len(plus_streaks[chat_id]) > 3:
                plus_streaks[chat_id].pop(0)

            if len(plus_streaks[chat_id]) == 3:
                await client.send_message(chat_id,
                    f"✅ Обнаружено 3 сигнала подряд в плюсе!\n📂 Папка: {chat_title}\n🔔 {notify_user}"
                )
                daily_stats[chat_id] += 1
                plus_streaks[chat_id] = []
                signal_state[chat_id] = {'ready': False, 'is_clean': True}

# Сообщение “бот активен” каждые 5 минут
async def status_notifier():
    while True:
        now = datetime.now().strftime('%H:%M:%S')
        for chat_id in chat_ids:
            await client.send_message(chat_id, f"🤖 Бот работает и ожидает сигналы... ({now})")
        await asyncio.sleep(300)

# Статистика в 23:59
async def daily_summary():
    while True:
        now = datetime.now()
        target = datetime.combine(now.date(), datetime.strptime("23:59", "%H:%M").time())
        if now > target:
            target += timedelta(days=1)
        await asyncio.sleep((target - now).seconds)
        for chat_id in chat_ids:
            if daily_stats[chat_id] > 0:
                await client.send_message(chat_id,
                    f"📊 Статистика за сутки:\n✅ 3 плюса подряд: {daily_stats[chat_id]} раз(а)"
                )
            daily_stats[chat_id] = 0  # Сброс на новый день

# Запуск
async def main():
    await asyncio.gather(
        status_notifier(),
        daily_summary()
    )

client.loop.run_until_complete(main())
