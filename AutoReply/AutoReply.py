# -*- coding:utf-8 -*-
'''
creation time: 2020-11-15
last_modify: 2023-05-02
'''
import os
import re
import random

def AutoReply(bot, message):
    message_type = message["message_type"]
    if message_type == "text":
        text = message["text"]

    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    message_id = message["message_id"]

    chat_type = message["chat"]["type"]

    prefix = "/autor"
    command = { #命令注册
            "/autoradd": "add",
            "/autordel": "del",
            "/autorshow": "show",
            "/autorclear": "clear"
        }

    if message_type != "text":
        return

    count = 0
    for c in command.keys():
        if c in str(text):
            count += 1

    plugin_dir = bot.plugin_dir
    root_id = bot.root_id
    data_dir = bot.path_converter(plugin_dir + "AutoReply/data.db")

    if not os.path.exists(data_dir):
        with open(data_dir, "w", encoding="utf-8") as d:
            pass

    result = {}
    with open(data_dir, "r", encoding="utf-8") as lines:
        for line in lines:
            if line != "\n":
                result[line.split(":")[0]] = line.split(":")[1]

    if text[:len(prefix)] == prefix and count == 0:
        if prefix in text and str(user_id) != root_id:
            status = bot.sendMessage(chat_id=chat_id, text="<b>无权限</b>", parse_mode="HTML",
                reply_to_message_id=message_id, allow_sending_without_reply=True)
            bot.message_deletor(15, status["chat"]["id"], status["message_id"])
            return

        msg = "<b>AutoReply 插件功能</b>" + "\n\n" + \
            "<b>/autoradd</b> 添加关键词回复 格式：指令 keyword:reply" + "\n" + \
            "<b>/autordel</b> 删除关键词回复 格式：指令 keyword" + "\n" + \
            "<b>/autorshow</b> 显示关键词回复列表" + "\n" + \
            "<b>/autorclear</b> 清空关键词回复列表" + "\n"
        status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML",
                reply_to_message_id=message_id, allow_sending_without_reply=True)
        bot.message_deletor(60, status["chat"]["id"], status["message_id"])

    elif text.split(" ")[0][:len(prefix + "add")] == prefix + "add":
        if prefix in text and str(user_id) != root_id:
            status = bot.sendMessage(chat_id=chat_id, text="<b>无权限</b>", parse_mode="HTML",
                reply_to_message_id=message_id, allow_sending_without_reply=True)
            bot.message_deletor(15, status["chat"]["id"], status["message_id"])
            return

        if len(text.split(" ")) >= 2:
            keyword_and_reply = text.split(" ", 1)[1]
            if len(keyword_and_reply.split(":")) == 2:
                keyword = keyword_and_reply.split(":")[0].strip()
                reply = keyword_and_reply.split(":")[1].strip()
                if keyword in result.keys():
                    msg = "<b>关键词存在，已更新</b>"
                else:
                    msg = "<b>添加成功</b>"
                result[keyword] = reply
                with open(data_dir, "w", encoding="utf-8") as d:
                    res = []
                    for key, rep in result.items():
                        res.append(key + ":" + rep + "\n")
                    d.writelines(res)

                status = bot.sendMessage(chat_id=chat_id,
                    text=msg, parse_mode="HTML",
                    reply_to_message_id=message_id, allow_sending_without_reply=True)
                bot.message_deletor(30, status["chat"]["id"], status["message_id"])
            else:
                status = bot.sendMessage(chat_id=chat_id,
                    text="<b>指令格式错误 (e.g.: " + prefix + " keyword:reply)</b>",
                    parse_mode="HTML", reply_to_message_id=message_id,
                    allow_sending_without_reply=True)
                bot.message_deletor(30, status["chat"]["id"], status["message_id"])
        else:
            status = bot.sendMessage(chat_id=chat_id,
                text="<b>指令格式错误 (e.g.: " + prefix + "add keyword:reply)</b>",
                parse_mode="HTML", reply_to_message_id=message_id,
                allow_sending_without_reply=True)
            bot.message_deletor(30, status["chat"]["id"], status["message_id"])

    elif text.split(" ")[0][:len(prefix + "del")] == prefix + "del":
        if prefix in text and str(user_id) != root_id:
            status = bot.sendMessage(chat_id=chat_id, text="<b>无权限</b>", parse_mode="HTML",
                reply_to_message_id=message_id, allow_sending_without_reply=True)
            bot.message_deletor(15, status["chat"]["id"], status["message_id"])
            return

        if len(text.split(" ")) == 2:
            keyword = text.split(" ")[1].strip()
            if keyword in list(result.keys()):
                result.pop(keyword)
                with open(data_dir, "w", encoding="utf-8") as d:
                    res = []
                    for key, rep in result.items():
                        res.append(key + ":" + rep + "\n")
                    d.writelines(res)
                status = bot.sendMessage(chat_id=chat_id,
                    text="<b>删除成功</b>",
                    parse_mode="HTML",
                    reply_to_message_id=message_id, allow_sending_without_reply=True)
                bot.message_deletor(30, status["chat"]["id"], status["message_id"])
            else:
                status = bot.sendMessage(chat_id=chat_id,
                    text="<b>关键词不存在</b>",
                    parse_mode="HTML",
                    reply_to_message_id=message_id, allow_sending_without_reply=True)
                bot.message_deletor(30, status["chat"]["id"], status["message_id"])
        else:
            status = bot.sendMessage(chat_id=chat_id,
                text="<b>指令格式错误 (e.g.: " + prefix + "del keyword)</b>",
                parse_mode="HTML", reply_to_message_id=message_id,
                allow_sending_without_reply=True)
            bot.message_deletor(30, status["chat"]["id"], status["message_id"])

    elif text.split(" ")[0][:len(prefix + "clear")] == prefix + "clear":
        if prefix in text and str(user_id) != root_id:
            status = bot.sendMessage(chat_id=chat_id, text="<b>无权限</b>", parse_mode="HTML",
                reply_to_message_id=message_id, allow_sending_without_reply=True)
            bot.message_deletor(15, status["chat"]["id"], status["message_id"])
            return

        with open(data_dir, "w", encoding="utf-8") as d:
            d.seek(0)
            d.truncate()
        status = bot.sendMessage(chat_id=chat_id,
            text="<b>已清空关键词回复列表</b>",
            parse_mode="HTML",
            reply_to_message_id=message_id, allow_sending_without_reply=True)
        bot.message_deletor(30, status["chat"]["id"], status["message_id"])

    elif text.split(" ")[0][:len(prefix + "show")] == prefix + "show":
        if prefix in text and str(user_id) != root_id:
            status = bot.sendMessage(chat_id=chat_id, text="<b>无权限</b>", parse_mode="HTML",
                reply_to_message_id=message_id, allow_sending_without_reply=True)
            bot.message_deletor(15, status["chat"]["id"], status["message_id"])
            return

        msg = "<b>关键词回复列表</b>\n\n"
        for key, val in result.items():
            msg += "<b>关键词:</b> <code>" + str(key) + "</code>\n" + \
                "<b>回复:</b> <code>" + str(val) + "</code>\n\n"
        status = bot.sendMessage(chat_id=chat_id,
            text=msg,
            parse_mode="HTML", reply_to_message_id=message_id,
            allow_sending_without_reply=True)
        bot.message_deletor(60, status["chat"]["id"], status["message_id"])

    elif len(result) != 0: # 自动回复
        result_washed = {}
        for keyword, reply in result.items():
            if keyword in text:
                result_washed[keyword] = reply
        text_re = re.findall('[a-zA-Z0-9]+',text)
        result = result_washed.copy()

        if len(text_re) != 0:
            for keyword, reply in result_washed.items():
                keyword_re = re.findall('[a-zA-Z0-9]+',keyword)
                if (keyword not in text_re
                    and len(keyword_re) != 0
                    and text_re != keyword_re):
                    result.pop(keyword)

        if len(list(result.values())) != 0:
            msg = random.choice(list(result.values()))
            status = bot.sendMessage(chat_id=chat_id, text=msg,
                parse_mode="HTML", reply_to_message_id=message_id,
                allow_sending_without_reply=True)
            # bot.message_deletor(30, status["chat"]["id"], status["message_id"])