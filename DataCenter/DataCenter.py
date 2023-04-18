# -*- coding:utf-8 -*-
'''
creation time: 2021-08-07
last_modification: 2023-04-13
'''
import os
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

    root_id = bot.root_id
    bot_id = bot.bot_id

    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    message_id = message["message_id"]

    chat_type = message["chat"]["type"]

    prefix = ""
    with open(bot.path_converter(bot.plugin_dir + "DataCenter/__init__.py"), "r", encoding="utf-8") as init:
        prefix = init.readline()[1:].strip()

    if not os.path.exists(bot.path_converter(bot.plugin_dir + "DataCenter/config.ini")):
        with open(bot.path_converter(bot.plugin_dir + "DataCenter/config.ini"), "w", encoding="utf-8") as conf: pass
    proxy = ""
    with open(bot.path_converter(bot.plugin_dir + "DataCenter/config.ini"), "r", encoding="utf-8") as conf:
        proxy = conf.readline().strip()

    if "reply_to_message" in message.keys() and \
        chat_type != "private":
        reply_to_message = message["reply_to_message"]
        target_message_id = reply_to_message["message_id"]
        target_user_id = reply_to_message["from"]["id"]
        target_chat_id = reply_to_message["chat"]["id"]

        admins = administrators(bot=bot, chat_id=chat_id)
        if str(user_id) not in admins:
            bot.sendChatAction(chat_id, "typing")
            txt = "只有管理员能查询他人账户。"
            status = bot.sendMessage(chat_id=chat_id, text=txt,
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, status["chat"]["id"], status["message_id"])
            return

        if str(target_user_id) in [str(root_id), str(bot_id)]:
            bot.sendChatAction(chat_id, "typing")
            txt = "您无权查询该账户。"
            status = bot.sendMessage(chat_id=chat_id, text=txt,
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, status["chat"]["id"], status["message_id"])
            return

        if "username" in reply_to_message["from"].keys():
            username = reply_to_message["from"]["username"]
        else:
            bot.sendChatAction(chat_id, "typing")
            txt = "您要查询的账号未设置<b>用户名</b>，无法查询。"
            status = bot.sendMessage(chat_id=chat_id, text=txt,
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, status["chat"]["id"], status["message_id"])
            return

        try:
            req = requests.get(url="https://t.me/" + username, proxies={"all": proxy})
        except:
            bot.sendChatAction(chat_id, "typing")
            txt = "获取数据失败，请重试。"
            status = bot.sendMessage(chat_id=chat_id, text=txt,
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, status["chat"]["id"], status["message_id"])
            return

        soup = BeautifulSoup(req.text, "html.parser")
        profile_photo = soup.find("img", class_="tgme_page_photo_image")
        soup.decompose()

        if profile_photo is None:
            bot.sendChatAction(chat_id, "typing")
            txt = "您要查询的账号未设置<b>头像</b>，无法查询。"
            status = bot.sendMessage(chat_id=chat_id, text=txt,
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, status["chat"]["id"], status["message_id"])
            return

        profile_photo_url = profile_photo.get("src")
        dc_info = profile_photo_url.split("/")[2]
        dc = "DC" + dc_info.split(".")[0][3:]

        location = "未知"
        if dc in data_centers.keys():
            location = data_centers[dc]
        
        bot.sendChatAction(chat_id, "typing")
        txt = "您查询的账号所在数据中心为 <b>" + dc + \
            "</b>, 地理位置为 <b>" + location + "</b>"
        status = bot.sendMessage(chat_id=chat_id, text=txt,
            parse_mode="HTML", reply_to_message_id=message_id)
        bot.message_deletor(30, status["chat"]["id"], status["message_id"])
        return

    elif "reply_to_message" not in message.keys():
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
            req = requests.get(url="https://t.me/" + username, proxies={"all": proxy})
        except:
            bot.sendChatAction(chat_id, "typing")
            txt = "获取数据失败，请重试。"
            status = bot.sendMessage(chat_id=chat_id, text=txt,
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, status["chat"]["id"], status["message_id"])
            return

        soup = BeautifulSoup(req.text, "html.parser")
        profile_photo = soup.find("img", class_="tgme_page_photo_image")
        soup.decompose()

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

    else:
        bot.sendChatAction(chat_id, "typing")
        txt = "不支持的操作。"
        status = bot.sendMessage(chat_id=chat_id, text=txt,
            parse_mode="HTML", reply_to_message_id=message_id)
        bot.message_deletor(15, status["chat"]["id"], status["message_id"])


def administrators(bot, chat_id):
    admins = []
    results = bot.getChatAdministrators(chat_id=chat_id)
    if results != False:
        for result in results:
            if str(result["user"]["is_bot"]) == "False":
                admins.append(str(result["user"]["id"]))
            if str(bot.root_id) not in admins:
                admins.append(str(bot.root_id))
            if str(bot.bot_id) not in admins:
                admins.append(str(bot.bot_id))
    else:
        admins = False

    return admins