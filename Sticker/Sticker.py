# -*- coding:utf-8 -*-
import requests

def Sticker(bot, message):
    proxies = bot.proxies

    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    text = message["text"]
    prefix = "getsticker"

    if text[1:len(prefix)+1] == prefix:
        if "reply_to_message" in message.keys():
            if "sticker" in message["reply_to_message"].keys():
                file_id = message["reply_to_message"]["sticker"]["file_id"]
                file_dl_path = bot.getFileDownloadPath(file_id=file_id)

                if ".tgs" in file_dl_path:
                    status = bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id, text="暂不支持获取tgs格式的贴纸!", reply_to_message_id=message_id)
                    bot.message_deletor(15, chat_id, status["message_id"])
                    return

                req = requests.get(url=file_dl_path, proxies=proxies)
                if type(req.content) == bytes:
                    photo = req.content
                else:
                    photo = file_dl_path
                status = bot.sendChatAction(chat_id=chat_id, action="typing")
                status = bot.sendPhoto(chat_id=chat_id, photo=photo, caption="本消息不久将被销毁，请尽快保存。" , reply_to_message_id=message_id)
                bot.message_deletor(30, chat_id, status["message_id"])
            else:
                status = bot.sendChatAction(chat_id=chat_id, action="typing")
                status = bot.sendMessage(chat_id=chat_id, text="您未指定要获取的贴纸!", reply_to_message_id=message_id)
                bot.message_deletor(15, chat_id, status["message_id"])
        else:
            status = bot.sendChatAction(chat_id=chat_id, action="typing")
            status = bot.sendMessage(chat_id=chat_id, text="您未指定要获取的贴纸!", reply_to_message_id=message_id)
            bot.message_deletor(15, chat_id, status["message_id"])
