# -*- coding:utf-8 -*-
'''
creation time: 2020-11-15
last_modify: 2020-11-18
'''
import time

def CallAdmins(bot, message):

    text = message["text"]

    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    message_id = message["message_id"]

    message_type = message["message_type"]
    chat_type = message["chat"]["type"]

    prefix = "/110"

    root_id = bot.root_id

    if text.split(" ")[0][:len(prefix)] == prefix:
        if chat_type != "private":
            if len(text.split(" ")) != 2:
                status = bot.sendMessage(chat_id=chat_id,
                    text="🤖 指令格式错误，请检查. (<b>e.g. " + str(prefix) + " reason</b>)",
                    parse_mode="HTML", reply_to_message_id=message_id)
                bot.message_deletor(15, status["chat"]["id"], status["message_id"])
                return

            reason = text.split(" ")[1]

            status = bot.sendMessage(chat_id=chat_id, text="🤖 正在为您呼叫管理员.", parse_mode="HTML",
                reply_to_message_id=message_id)

            admins_raw = administrators(bot=bot, chat_id=chat_id)
            if str(root_id) not in admins_raw:
                admins_raw.append(str(root_id)) #root permission
            admins = []
            for i, admin in enumerate(admins_raw):
                if str(admin) != str(user_id):
                    admins.append(admin)

            chat_username = message["chat"].get("username", chat_id)
            chat_title = message["chat"]["title"]
            for i, admin in enumerate(admins):

                bot.editMessageText(chat_id=status["chat"]["id"], message_id=status["message_id"],
                    text="🤖 正在为您呼叫管理员 <b>" + str(i+1) + "/" + str(len(admins)) + "</b>", parse_mode="HTML")
                inlineKeyboard = [
                    [
                        {"text": "去看看 👉🏻", "url": "https://t.me/" + str(chat_username) + "/"+ str(message_id)}
                    ]
                ]
                reply_markup = {
                    "inline_keyboard": inlineKeyboard
                }
                msg = "🤖 管理，您好，" + \
                "<b>" + str(chat_title) + "</b> " + \
                "有小伙伴在呼叫您." + \
                "\n\n<b>原因:</b> <code>" + str(reason) + "</code>"
                stat = bot.sendMessage(chat_id=admin, text=msg,
                parse_mode="HTML", reply_markup=reply_markup)

                time.sleep(1)

            bot.editMessageText(chat_id=status["chat"]["id"],
            message_id=status["message_id"], text="🤖 已通知管理员.", parse_mode="HTML")
        else:
            status = bot.sendMessage(chat_id=chat_id,
                text="🤖 抱歉，该指令不支持私人会话!",
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, status["chat"]["id"], status["message_id"])


def administrators(bot, chat_id):
    admins = []
    results = bot.getChatAdministrators(chat_id=chat_id)
    if results != False:
        for result in results:
            if str(result["user"]["is_bot"]) == "False":
                admins.append(str(result["user"]["id"]))
    else:
        admins = False

    return admins