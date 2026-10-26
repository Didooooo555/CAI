import requests
import sys

name = sys.argv[1]

# Токен твоего бота
TOKEN = "8096893571:AAGE0vhoa3ZWRObTA5kMTd3p_CFJXny_s1M"

# Твой chat_id
CHAT_ID = "7875346189"

# Текст сообщения
message = f"CAI:Экологическое нарушение подтверждено. Личность установлена: {name}. Последствия - вопрос времени!"

# URL Telegram API
url = f"https://api.telegram.org/bot8096893571:AAGE0vhoa3ZWRObTA5kMTd3p_CFJXny_s1M/sendMessage"

# Параметры запроса
payload = {
    "chat_id": CHAT_ID,
    "text": message
}

# Отправляем POST-запрос
r = requests.post(url, json=payload)

print(f"Сообщение отправлено: {name}")
