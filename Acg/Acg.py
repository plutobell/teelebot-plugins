# -*- coding:utf-8 -*-
from random import choice
import requests

def Acg(bot, message):
    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    text = message["text"]
    prefix = "acg"

    if text[1:len(prefix)+1] == prefix:
        img = acg_img()
        caption = str(one_said())
        if img != False and caption != False:
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendPhoto(chat_id=chat_id, photo=img, caption=caption, parse_mode="HTML", reply_to_message_id=message_id)
        else:
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id=chat_id, text="获取失败，请稍后重试!", parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, chat_id, status["message_id"])
    else:
        status = bot.sendChatAction(chat_id, "typing")
        status = bot.sendMessage(chat_id=chat_id, text="指令错误，请检查!", parse_mode="HTML", reply_to_message_id=message_id)
        bot.message_deletor(15, chat_id, status["message_id"])

def acg_img():
    urls = [
        "http://www.dmoe.cc/random.php",
        "https://api.xiaobaibk.com/api/pic/?pic=acg",
        "https://api.vvhan.com/api/acgimg",
        "https://www.loliapi.com/acg/"
    ]
    url = choice(urls)
    try:
        with requests.post(url=url, verify=False) as req:
            if not req.status_code == requests.codes.ok:
                return False
            elif type(req.content) == bytes:
                return req.content
            else:
                return False
    except:
        return False

def one_said():
    urls = [
        "https://api.vvhan.com/api/love",
        "https://api.vvhan.com/api/sao",
        "http://api.guaqb.cn/v1/onesaid/",
        "https://api.vvhan.com/api/ian"
    ]
    url = choice(urls)
    try:
        with requests.post(url, verify=False) as req:
            if not req.status_code == requests.codes.ok:
                return False
            else:
                return req.text
    except:
        return False
