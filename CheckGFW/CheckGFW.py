# -*- coding:utf-8 -*-
import datetime
import requests
import validators

def CheckGFW(bot, message):

    bot_id = bot.bot_id
    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    text = message["text"]
    chat_type = message["chat"]["type"]
    admins = []
    if chat_type != "private":
        admins = chat_admin_list(bot=bot, chat_id=chat_id)

    prefix = ""
    ok, metadata = bot.metadata.read()
    if ok:
        prefix = metadata.get("Command", "")

    if text[:len(prefix)] == prefix:
        if len(text.split(' ')) == 2:
            domain = text.split(' ')[1]
            if validators.domain(domain):
                now = datetime.datetime.now()
                ok, data = check_GFW_block(domain)
                # print(ok, data)
                if ok:
                    msg = "<b>Check GFW：</b>\n" +\
                        "\n<code>Domain: " + str(data["domain"]) +\
                        "\nStatus: </code><b>" + str(data["msg"] + "</b>") +\
                        "\n\n<code>" + str(now.strftime("%Y-%m-%d %H:%M:%S")) + "</code>"
                    bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id, text=msg,
                        parse_mode="HTML", reply_to_message_id=message_id, disable_web_page_preview=True)
                    bot.message_deletor(60, chat_id, status["message_id"])
                    if chat_type != "private" and bot_id in admins:
                        bot.message_deletor(65, chat_id, message_id)
                else:
                    bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id, text="<b>Detection failed, please try again!</b>", parse_mode="HTML", reply_to_message_id=message_id)
                    bot.message_deletor(15, chat_id, status["message_id"])
            else:
                bot.sendChatAction(chat_id=chat_id, action="typing")
                status = bot.sendMessage(chat_id=chat_id, text="<b>Domain name formatting error, please check!</b>", parse_mode="HTML", reply_to_message_id=message_id)
                bot.message_deletor(15, chat_id, status["message_id"])
        else:
            bot.sendChatAction(chat_id=chat_id, action="typing")
            status = bot.sendMessage(chat_id=chat_id, text="<b>Command formatting error, please check!</b>", parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, chat_id, status["message_id"])
    else:
        bot.sendChatAction(chat_id=chat_id, action="typing")
        status = bot.sendMessage(chat_id=chat_id, text="<b>Command error, please check!</b>", parse_mode="HTML", reply_to_message_id=message_id)
        bot.message_deletor(15, chat_id, status["message_id"])


def check_GFW_block(domain):
    """
    {
        "success": true,
        "domain": "www.google.com",
        "msg": "被墙了"
    }
    """
    url = "https://api.vvhan.com/api/qiang?url=" + str(domain)
    try:
        with requests.get(url=url, verify=False) as req:
            # print(req.text)
            if req.status_code == requests.codes.ok:
                data = req.json()
                if data.get("msg", None) == "被墙了":
                    data["msg"] = "BLOCKED"
                elif data.get("msg", None) == "正常":
                    data["msg"] = "NOT BLOCKED"
                else:
                    data["msg"] = "UNKNOWN"
                return True, data
            else:
                return False, {"success": False, "domain": domain, "msg": "ERROR: " + str(req.status_code) }
    except Exception as e:
        print(e)
        return False, {"success": False, "domain": domain, "msg": "ERROR" }
    

def chat_admin_list(bot, chat_id) -> list:
    admin_list = []

    req = bot.getChatAdministrators(chat_id=chat_id)
    if req != False:
        for r in req:
            admin_list.append(str(r["user"]["id"]))
    admin_list.append(str(bot.root_id))

    return admin_list