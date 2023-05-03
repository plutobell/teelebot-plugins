# -*- coding:utf-8 -*-
import requests
import random

def Dwz(bot, message):
    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    text = message["text"]
    prefix = "dwz"

    if text[1:len(prefix)+1] == prefix:
        if len(text.split(' ')) == 2:
            if "https://" in text.split(' ')[1] or "http://" in text.split(' ')[1]:
                dwz_url = dwz(text.split(' ')[1])
                if dwz_url != False:
                    msg = "<b>短网址生成：</b>\n" +\
                        "\n原网址: " + str(text.split(' ')[1]) +\
                        "\n短网址: " + str(dwz_url) +\
                        "\n\n请保存短网址，本消息不久将被销毁"
                    bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id, text=msg,
                        parse_mode="HTML", reply_to_message_id=message_id, disable_web_page_preview=True)
                    bot.message_deletor(60, chat_id, status["message_id"])
                else:
                    bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id, text="生成失败，请重试!", parse_mode="HTML", reply_to_message_id=message_id)
                    bot.message_deletor(15, chat_id, status["message_id"])
            else:
                bot.sendChatAction(chat_id=chat_id, action="typing")
                status = bot.sendMessage(chat_id=chat_id, text="网址需带上协议头，请重试!", parse_mode="HTML", reply_to_message_id=message_id)
                bot.message_deletor(15, chat_id, status["message_id"])
        else:
            bot.sendChatAction(chat_id=chat_id, action="typing")
            status = bot.sendMessage(chat_id=chat_id, text="指令格式错误，请检查!", parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, chat_id, status["message_id"])
    else:
        bot.sendChatAction(chat_id=chat_id, action="typing")
        status = bot.sendMessage(chat_id=chat_id, text="指令错误，请检查!", parse_mode="HTML", reply_to_message_id=message_id)
        bot.message_deletor(15, chat_id, status["message_id"])


def dwz(url):
    dwzapi = ["tcn", "dwzcn", "urlcn", "suoim", "mrwso"]
    url = "https://api.uomg.com/api/long2dwz?dwzapi=" + random.choice(dwzapi) + "&url=" + str(url)
    # print(url)
    try:
        with requests.post(url=url, verify=False) as req:
            if not req.status_code == requests.codes.ok:
                return False
            elif req.json().get("code") == 1:
                return req.json().get("ae_url")
            else:
                print(req.json().get("msg"))
                return False
    except:
        return False
