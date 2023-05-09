# -*- coding:utf-8 -*-

def ID(bot, message):
    bot_id = bot.bot_id
    root_id = bot.root_id

    admins = []
    if message["chat"]["type"] != "private":
        admins = administrators(bot=bot, chat_id=message["chat"]["id"])
        if str(root_id) not in admins:
            admins.append(str(root_id)) #root permission

    if message["text"][:len("/idchat")] == "/idchat":
        if message["chat"]["type"] != "private" and str(message["from"]["id"]) not in admins:
            status = bot.sendChatAction(chat_id=message["chat"]["id"], action="typing")
            status = bot.sendMessage(chat_id=message["chat"]["id"], text="抱歉，您无权查询!", reply_to_message_id=message["message_id"])
        elif message["chat"]["type"] != "private" or len(message["text"].split(" ", 1)) > 1:
            if len(message["text"].split(" ", 1)) == 1:
                status = bot.sendChatAction(chat_id=message["chat"]["id"], action="typing")
                status = bot.sendMessage(chat_id=message["chat"]["id"],
                text="当前群组的ID为：<b><code>" + str(message["chat"]["id"]) + "</code></b>",
                    parse_mode="HTML", reply_to_message_id=message["message_id"])
            elif len(message["text"].split(" ", 1)) == 2:
                chat_username = message["text"].split(" ", 1)[1]
                if " " in chat_username or chat_username[0] != "@":
                    status = bot.sendChatAction(chat_id=message["chat"]["id"], action="typing")
                    status = bot.sendMessage(chat_id=message["chat"]["id"], text="群组用户名格式错误，请检查!",
                        reply_to_message_id=message["message_id"])
                else:
                    status = bot.getChat(chat_id=chat_username)
                    if status != False:
                        id = status["id"]
                        status = bot.sendChatAction(chat_id=message["chat"]["id"], action="typing")
                        msg = "群组 <b>" + str(chat_username) + " </b>的ID为: <code>" + str(id) + "</code>"
                        status = bot.sendMessage(chat_id=message["chat"]["id"], text=msg,
                            parse_mode="HTML", reply_to_message_id=message["message_id"])
                    else:
                        status = bot.sendChatAction(chat_id=message["chat"]["id"], action="typing")
                        msg = "获取群组 <b>" + str(chat_username) + " </b>的ID失败，请重试！"
                        status = bot.sendMessage(chat_id=message["chat"]["id"], text=msg,
                            parse_mode="HTML", reply_to_message_id=message["message_id"])
        else:
            status = bot.sendChatAction(chat_id=message["chat"]["id"], action="typing")
            status = bot.sendMessage(chat_id=message["chat"]["id"], text="抱歉，该指令不支持私人会话!",
                reply_to_message_id=message["message_id"])
        bot.message_deletor(15, status["chat"]["id"], status["message_id"])

    elif message["text"][:len("/id")] == "/id" and "reply_to_message" not in message.keys():
        status = bot.sendChatAction(chat_id=message["chat"]["id"], action="typing")
        if str(message["from"]["id"]) == root_id:
            status = bot.sendChatAction(chat_id=message["chat"]["id"], action="typing")
            status = bot.sendMessage(chat_id=message["chat"]["id"], text="您的用户ID为：<b><code>" + str(message["from"]["id"]) + "</code></b>", parse_mode="HTML", reply_to_message_id=message["message_id"])
        else:
            status = bot.sendChatAction(chat_id=message["chat"]["id"], action="typing")
            first_name = str(message["from"]["first_name"])
            status = bot.sendMessage(chat_id=message["chat"]["id"], text=first_name + "\n您的用户ID为：<b><code>" + str(message["from"]["id"]) + "</code></b>", parse_mode="HTML", reply_to_message_id=message["message_id"])
        bot.message_deletor(30, status["chat"]["id"], status["message_id"])
    elif message["text"][:len("/id")] == "/id" and "reply_to_message" in message.keys() and message["chat"]["type"] != "private":

        if str(message["from"]["id"]) in admins:
            reply_to_message = message["reply_to_message"]
            target_message_id = reply_to_message["message_id"]
            target_user_id = reply_to_message["from"]["id"]
            target_chat_id = reply_to_message["chat"]["id"]

            if str(bot_id) != str(target_user_id):
                if str(message["from"]["id"]) == root_id:
                    status = bot.sendChatAction(chat_id=message["chat"]["id"], action="typing")
                    status = bot.sendMessage(chat_id=message["chat"]["id"], text="您查询的用户的ID为：<b><code>" + str(target_user_id) + "</code></b>", parse_mode="HTML", reply_to_message_id=message["message_id"])
                else:
                    status = bot.sendChatAction(chat_id=message["chat"]["id"], action="typing")
                    first_name = str(message["from"]["first_name"])
                    status = bot.sendMessage(chat_id=message["chat"]["id"], text=first_name + "\n您查询的用户的ID为：<b><code>" + str(target_user_id) + "</code></b>", parse_mode="HTML", reply_to_message_id=message["message_id"])
                bot.message_deletor(30, status["chat"]["id"], status["message_id"])
            else:
                if str(message["from"]["id"]) == root_id:
                    status = bot.sendChatAction(chat_id=message["chat"]["id"], action="typing")
                    status = bot.sendMessage(chat_id=message["chat"]["id"], text="我的ID为：<b><code>" + str(target_user_id) + "</code></b>", parse_mode="HTML", reply_to_message_id=message["message_id"])
                else:
                    status = bot.sendChatAction(chat_id=message["chat"]["id"], action="typing")
                    status = bot.sendMessage(chat_id=message["chat"]["id"], text="抱歉，您无权查询!", reply_to_message_id=message["message_id"])
                bot.message_deletor(30, status["chat"]["id"], status["message_id"])
        else:
            status = bot.sendChatAction(chat_id=message["chat"]["id"], action="typing")
            status = bot.sendMessage(chat_id=message["chat"]["id"], text="抱歉，您无权查询!", reply_to_message_id=message["message_id"])
            bot.message_deletor(30, status["chat"]["id"], status["message_id"])
    elif message["text"][:len("/id")] == "/id" and "reply_to_message" in message.keys() and message["chat"]["type"] == "private":
        reply_to_message = message["reply_to_message"]
        target_message_id = reply_to_message["message_id"]
        target_user_id = reply_to_message["from"]["id"]
        target_chat_id = reply_to_message["chat"]["id"]

        if str(bot_id) == str(target_user_id):
            if str(message["from"]["id"]) == root_id:
                status = bot.sendChatAction(chat_id=message["chat"]["id"], action="typing")
                status = bot.sendMessage(chat_id=message["chat"]["id"], text="我的ID为：<b><code>" + str(target_user_id) + "</code></b>", parse_mode="HTML", reply_to_message_id=message["message_id"])
            else:
                status = bot.sendChatAction(chat_id=message["chat"]["id"], action="typing")
                status = bot.sendMessage(chat_id=message["chat"]["id"], text="抱歉，您无权查询!", reply_to_message_id=message["message_id"])
            bot.message_deletor(30, status["chat"]["id"], status["message_id"])
        else:
            if str(message["from"]["id"]) == root_id:
                status = bot.sendChatAction(chat_id=message["chat"]["id"], action="typing")
                status = bot.sendMessage(chat_id=message["chat"]["id"], text="您查询的用户的ID为：<b><code>" + str(target_user_id) + "</code></b>", parse_mode="HTML", reply_to_message_id=message["message_id"])
            elif message["chat"]["id"] == target_user_id:
                status = bot.sendChatAction(chat_id=message["chat"]["id"], action="typing")
                first_name = str(message["from"]["first_name"])
                status = bot.sendMessage(chat_id=message["chat"]["id"], text=first_name + "\n您的用户ID为：<b><code>" + str(target_user_id) + "</code></b>", parse_mode="HTML", reply_to_message_id=message["message_id"])
            bot.message_deletor(30, status["chat"]["id"], status["message_id"])
    else:
        status = bot.sendChatAction(chat_id=message["chat"]["id"], action="typing")
        status = bot.sendMessage(chat_id=message["chat"]["id"], text="请检查指令是否正确!", reply_to_message_id=message["message_id"])
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
