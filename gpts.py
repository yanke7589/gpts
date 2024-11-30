import requests  
import json  
import telebot  
import os

ze = '8173144188:AAEwlC0f7zGtuOaTER7PyhGeOnOEu2yiea0'  # توكنك 
zo = telebot.TeleBot(ze)
API_URL = 'https://baithek.com/chatbee/health_ai/new_health.php'
HEADERS = {
    'Host': 'baithek.com',
    'Content-Type': 'application/json',
    'User-Agent': 'okhttp/4.9.2'
}

user_context = {}

@zo.message_handler(commands=['من انت'])
def welcome_message(message):
    text = ''' 🧠 اهلا انا مساعد المطور فيسكو كيف يمكنني مساعدتك  '''
    zo.reply_to(message, text, parse_mode='Markdown')

@zo.message_handler(func=lambda message: True)
def handle_message(message):
    """جاري الكتابة """
    user_id = message.from_user.id  
    user_message = message.text  
    loading_message = zo.reply_to(message, "💬")
    
    if user_id not in user_context:
        user_context[user_id] = []

    user_context[user_id].append({'role': 'user', 'content': user_message})

    data = {
        'name': 'Usama',
        'messages': user_context[user_id],
        'n': 1,
        'stream': True  
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=data)
        response.raise_for_status()
        json_data = response.json()
        choices = json_data.get('choices', [])

        if choices:
            result_text = choices[0].get('message', {}).get('content', '')
            user_context[user_id].append({'role': 'assistant', 'content': result_text})

            if result_text:
                vipcode_max = 4096  # تعيين قيمة vipcode_max  
                if len(result_text) > vipcode_max:
                    file_path = f'user_message_{user_id}.txt'
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(result_text)
                    with open(file_path, 'rb') as f:
                        text = ''
                        zo.send_document(chat_id=message.chat.id, document=f, caption=text, reply_to_message_id=message.message_id)
                    os.remove(file_path)
                else:
                    zo.edit_message_text(result_text, chat_id=message.chat.id, message_id=loading_message.message_id)
        else:
            text = 'لا توجد ردود متاحة.'
            zo.edit_message_text(text, chat_id=message.chat.id, message_id=loading_message.message_id)

    except requests.RequestException as e:
        text = 'حدث خطأ أثناء معالجة طلبك.'
        zo.edit_message_text(text, chat_id=message.chat.id, message_id=loading_message.message_id)
        print(f"Error: {e}")

zo.polling()
