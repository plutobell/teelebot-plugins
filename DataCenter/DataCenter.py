# -*- coding:utf-8 -*-
'''
creation time: 2021-08-07
last_modification: 2021-08-07
'''
import requests
from bs4 import BeautifulSoup

def DataCenter(bot, message):
    '''
    数据中心 AS号 位置
    DC1	AS59930	迈阿密
    DC2	AS62041	阿姆斯特丹
    DC3	AS59930	迈阿密
    DC4	AS62041	阿姆斯特丹
    DC5	AS62014	新加坡
    '''
    data_centers = {
        "DC1": "迈阿密",
        "DC2": "阿姆斯特丹",
        "DC3": "迈阿密",
        "DC4": "阿姆斯特丹",
        "DC5": "新加坡"
    }

    # root_id = bot.root_id
    # bot_id = bot.bot_id

    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    message_id = message["message_id"]

    message_type = message["message_type"]
    chat_type = message["chat"]["type"]

    prefix = ""
    with open(bot.path_converter(bot.plugin_dir + "DataCenter/__init__.py"), "r", encoding="utf-8") as init:
        prefix = init.readline()[1:].strip()

    if "username" in message["from"].keys():
        username = message["from"]["username"]
    else:
        bot.sendChatAction(chat_id, "typing")
        txt = "要查询您账号所在数据中心，请先设置<b>用户名</b>。"
        status = bot.sendMessage(chat_id=chat_id, text=txt,
            parse_mode="HTML", reply_to_message_id=message_id)
        bot.message_deletor(15, status["chat"]["id"], status["message_id"])
        return

    try:
        req = requests.get(url="https://t.me/" + username)
    except:
        bot.sendChatAction(chat_id, "typing")
        txt = "获取数据失败，请重试。"
        status = bot.sendMessage(chat_id=chat_id, text=txt,
            parse_mode="HTML", reply_to_message_id=message_id)
        bot.message_deletor(15, status["chat"]["id"], status["message_id"])
        return

    soup = BeautifulSoup(req.text, "html.parser")
    profile_photo = soup.find("img", class_="tgme_page_photo_image")

    if profile_photo is None:
        bot.sendChatAction(chat_id, "typing")
        txt = "要查询您账号所在数据中心，请先设置<b>头像</b>。"
        status = bot.sendMessage(chat_id=chat_id, text=txt,
            parse_mode="HTML", reply_to_message_id=message_id)
        bot.message_deletor(15, status["chat"]["id"], status["message_id"])
        return

    profile_photo_url = profile_photo.get("src")
    dc_info = profile_photo_url.split("/")[2]
    dc = "DC" + dc_info.split(".")[0][3:]
    print(dc)

    location = "未知"
    if dc in data_centers.keys():
        location = data_centers[dc]

    bot.sendChatAction(chat_id, "typing")
    txt = "您账号所在数据中心为 <b>" + dc + \
        "</b>, 地理位置为 <b>" + location + "</b>"
    status = bot.sendMessage(chat_id=chat_id, text=txt,
        parse_mode="HTML", reply_to_message_id=message_id)
    bot.message_deletor(30, status["chat"]["id"], status["message_id"])
    return