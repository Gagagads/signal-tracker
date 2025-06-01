from telethon.sync import TelegramClient

api_id = 27133766
api_hash = '40d7b357c572c7fa7cbe273e050c679c'

with TelegramClient('anon', api_id, api_hash) as client:
    print("Успешно подключились к Telegram!")
