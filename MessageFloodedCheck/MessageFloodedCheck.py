# -*- coding:utf-8 -*-
'''
@creation date: 2021-04-26
@last modify: 2021-04-26
'''
import difflib
import time

def MessageFloodedCheck(bot, message):

    root_id = bot.root_id
    bot_id = bot.bot_id

    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    message_id = message["message_id"]

    message_type = message["message_type"]
    chat_type = message["chat"]["type"]

    prefix = ""
    with open(bot.path_converter(bot.plugin_dir + "MessageFloodedCheck/__init__.py"), "r", encoding="utf-8") as init:
        prefix = init.readline()[1:].strip()

    admins = []
    if chat_type == "private": #判断是否为私人对话
        return False
    else:
        admins = administrators(bot, chat_id) #判断Bot是否具管理员权限
        admin_status = False
        if str(bot_id) in admins:
            admin_status = True
        if admin_status is not True:
            bot.sendChatAction(chat_id, "typing")
            msg = "权限不足，请授予全部权限以使用 MessageFloodedCheck 插件。"
            status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML")
            bot.message_deletor(30, chat_id, status["message_id"])
            return False


    ok, buf = bot.buffer.read()
    buf.setdefault(str(chat_id), {}).setdefault(str(user_id), {})
    if ok:
        previous_message = buf[str(chat_id)][str(user_id)].setdefault("previous_message", "")
        repeat_times = buf[str(chat_id)][str(user_id)].setdefault("repeat_times", 0)
        timestamp = buf[str(chat_id)][str(user_id)].setdefault("timestamp", int(time.time()))
        repeat_message_ids = buf[str(chat_id)][str(user_id)].setdefault("repeat_message_ids", [])
        # print(previous_message, repeat_times, timestamp, repeat_message_ids)

        now_message = ""
        if message_type == "text":
            now_message = message["text"]
        elif message_type == "sticker":
            now_message = message["sticker"]["file_unique_id"]

        if now_message != "":
            similarity = string_similar(previous_message, now_message)
            # print(str(similarity * 100) + "%")
            if similarity > 0.75:
                repeat_times += 1
                repeat_message_ids.append(str(message_id))

            previous_message = now_message

        if (int(time.time()) - timestamp) <= 60: # 超时判断
            if repeat_times == 3:
                bot.sendChatAction(chat_id, "typing")
                user_info = "<b><a href='tg://user?id=" + str(user_id) + "'>" + str(user_id) + "</a></b>"
                if str(user_id) in admins:
                    msg = "管理员 " + user_info + ", 您似乎在重复发送相似消息\n<b>请以身作则😃</b>"
                else:
                    msg = user_info + ", 检测到您似乎在重复发送相似消息\n<b>继续发送将被禁言，请谨言慎行</b>"
                status = bot.sendMessage(
                    chat_id=chat_id, text=msg, parse_mode="HTML")
                bot.message_deletor(15, status["chat"]["id"], status["message_id"])

            if repeat_times >= 5:
                mute_time = 10 # 禁言时间，单位为分钟
                bot.sendChatAction(chat_id, "typing")
                user_info = "<b><a href='tg://user?id=" + str(user_id) + "'>" + str(user_id) + "</a></b>"
                if str(user_id) in admins:
                    msg = "🐶管理 " + user_info + ", 还在刷！?\n作为管理员，<b>您配吗?😕</b>\n<b>请以身作则</b>"
                else:
                    msg = user_info + ", 由于您重复发送相似消息\n<b>你已被禁言 " + str(mute_time) + " 分钟</b>"
                    permissions = {
                        'can_send_messages':False,
                        'can_send_media_messages':False,
                        'can_send_polls':False,
                        'can_send_other_messages':False,
                        'can_add_web_page_previews':False,
                        'can_change_info':False,
                        'can_invite_users':False,
                        'can_pin_messages':False
                    }
                    status = bot.restrictChatMember(
                        chat_id=chat_id, user_id=user_id,
                        permissions=permissions, until_date=mute_time * 60)
                status = bot.sendMessage(
                    chat_id=chat_id, text=msg, parse_mode="HTML")
                bot.message_deletor(30, status["chat"]["id"], status["message_id"])

                for msg_id in repeat_message_ids: # 删除重复消息
                    bot.deleteMessage(chat_id, msg_id)
                    time.sleep(0.5)

                timestamp = int(time.time())
                repeat_times = 0
                repeat_message_ids = []
        else:
            timestamp = int(time.time())
            repeat_times = 0
            repeat_message_ids = []

        buf[str(chat_id)][str(user_id)]["previous_message"] = previous_message
        buf[str(chat_id)][str(user_id)]["repeat_times"] = repeat_times
        buf[str(chat_id)][str(user_id)]["timestamp"] = timestamp
        buf[str(chat_id)][str(user_id)]["repeat_message_ids"] = repeat_message_ids
        ok, _ = bot.buffer.write(buf)



def string_similar(str1, str2):
    similarity = difflib.SequenceMatcher(None, str1, str2).quick_ratio()

    return round(similarity, 2)

def administrators(bot, chat_id):
    admins = []
    results = bot.getChatAdministrators(chat_id=chat_id)
    if results != False:
        for result in results:
            admins.append(str(result["user"]["id"]))

        if str(bot.root_id) not in admins:
            admins.append(str(bot.root_id))
    else:
        admins = False

    return admins