# import telebot
# import requests
# import json
#
# bot = telebot.TeleBot('5625836626:AAF2GeURtc4G9rWfJnhnFyvoG-Nm9zJp-BQ', parse_mode=None)
#
#
# @bot.message_handler(commands=['start', 'help'])
# def send_welcome(message):
#     bot.reply_to(message, 'Hellowthere')
#
# @bot.message_handler(func=lambda m: True)
# def echo_all(message):
#     bot.reply_to(message, message.chat.id)
#
#     data = {
#         'message': message.text,
#         'user': message.from_user.id
#     }
#
#     json_data = json.dumps(data, indent=4)
#     requests.post('http://127.0.0.1:5000/telebotresponse', data=json_data)
#
# bot.infinity_polling()

TWITCH_BROADCASTERS = [
    {
        "id": "42078350",
        "username": "Niyatsu",
        "notification_photo": "https://static-cdn.jtvnw.net/jtv_user_pictures/49f31131-5ecd-40cb-9b5c-bd05df8a95bd-profile_image-70x70.png"
    },
    {
        "id": "48470858",
        "username": "RobotKitten",
        "notification_photo": "https://static-cdn.jtvnw.net/jtv_user_pictures/49f31131-5ecd-40cb-9b5c-bd05df8a95bd-profile_image-70x70.png"
    },
    {
        "id": "469559912",
        "username": "MASHTAGA",
        "notification_photo": "https://static-cdn.jtvnw.net/jtv_user_pictures/49f31131-5ecd-40cb-9b5c-bd05df8a95bd-profile_image-70x70.png"
    },
]


res = next((bd for bd in TWITCH_BROADCASTERS if bd['id'] == '469559912'), None)

print(str(res))