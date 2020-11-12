# -*- coding:utf-8 -*-
'''
creation time: 2020-11-12
last_modify: 2020-11-12
'''
import time

def Speaker(bot, message):

    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    message_id = message["message_id"]
    text = message["text"]

    prefix = "/speaker"

    if prefix in text and str(user_id) != bot.config["root"]:
        status = bot.sendMessage(chat_id, text="无权限", parse_mode="HTML",
            reply_to_message_id=message_id)
        bot.message_deletor(15, status["chat"]["id"], status["message_id"])
        return

    if text.split(" ")[0] == prefix:
        if  len(text.split(" ")) == 2:
            send_msg = text.split(" ")[1]
            send_msg = send_msg.replace("#", " ")
            send_msg = send_msg + " %0A%0A<i>此消息为群发消息</i>"
            chats = bot.response_chats()
            chats_count = len(chats)


            status = bot.sendMessage(chat_id=chat_id, text="<b>发送开始</b> %0A%0A", parse_mode="HTML",
                reply_to_message_id=message_id)

            failure_count = 0
            success_count = 0
            for chat in chats:
                msg = "<b>发送开始 %0A%0A" + \
                "共 " + str(chats_count) + " 个群组 %0A" + \
                "成功个数: " + str(success_count) + " %0A" +\
                "失败个数: " + str(failure_count) + " %0A" + \
                "正在发送: " + str(chat) + " %0A </b>"
                bot.editMessageText(chat_id=status["chat"]["id"],
                message_id=status["message_id"],
                text=msg, parse_mode="HTML")

                stat = bot.sendMessage(chat_id=chat, text=send_msg,
                parse_mode="HTML")
                if not stat:
                    failure_count += 1
                else:
                    success_count += 1
                success_count = chats_count + failure_count

                time.sleep(1)

            msg = "<b>发送结束 %0A%0A" + \
                "共 " + str(chats_count) + " 个群组 %0A" + \
                "成功个数: " + str(success_count) + " %0A" +\
                "失败个数: " + str(failure_count) + " %0A </b>"
            bot.editMessageText(chat_id=status["chat"]["id"],
            message_id=status["message_id"], text=msg, parse_mode="HTML")
            bot.message_deletor(60, status["chat"]["id"], status["message_id"])

        else:
            status = bot.sendMessage(chat_id,
                text="<b>指令格式错误 (e.g.: " + prefix + " text)</b>",
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(30, status["chat"]["id"], status["message_id"])
