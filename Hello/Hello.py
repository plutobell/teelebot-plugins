# -*- coding:utf-8 -*-

def Init(bot):
    print("Hello World!")

def Hello(bot, message):
    #print("你好,世界!")

    chat_id = message["chat"]["id"]
    message_id = message["message_id"]

    photo = None
    with open(bot.join_plugin_path("helloworld.png"), "rb") as p:
        photo = p.read()

    bot.sendChatAction(chat_id=chat_id, action="typing")
    bot.sendPhoto(chat_id=message["chat"]["id"], photo=photo,
                    reply_to_message_id=message_id)