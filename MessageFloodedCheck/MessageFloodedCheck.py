# -*- coding:utf-8 -*-
'''
@creation date: 2021-04-26
@last modify: 2021-05-29
'''
import difflib
import time
from langconv import Converter

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

    if str(user_id) == bot_id:
        return
    elif message_type not in ["text", "sticker"]:
        if "caption" not in message.keys():
            return

    ok, buf = bot.buffer.read()
    buf.setdefault(str(chat_id), {}).setdefault(str(user_id), {})
    if ok:
        chat_record_messages = buf[str(chat_id)] # 清除群组范围内的无效数据
        for user_id, value in dict(chat_record_messages).items():
            timestamp_ = value.setdefault("timestamp", int(time.time()))
            if (int(time.time()) - timestamp_) > 60:
                buf[str(chat_id)].pop(str(user_id))

        record_messages = buf[str(chat_id)][str(user_id)].setdefault("record_messages", {})
        timestamp = buf[str(chat_id)][str(user_id)].setdefault("timestamp", int(time.time()))

        message_text = ""
        if message_type == "text":
            message_text = message["text"]
        elif "caption" in message.keys():
            message_text += message["caption"]
        elif message_type == "sticker":
            message_text = message["sticker"]["file_unique_id"]
        message_text = message_text.strip()
        message_text = message_text.replace(" ", "")
        message_text = Traditional2Simplified(sentence=message_text)

        if message_text != "":
            record_messages[str(message_id)] = message_text
        record_messages_no_repeat = set(record_messages.values())

        no_repeat_msg_repeat_ids = {}
        for no_repeat_msg in record_messages_no_repeat:
            repeat_times = 0
            no_repeat_msg_dict = {}
            no_repeat_msg_dict["repeat_ids"] = []
            for msg_id in list(record_messages.keys()):
                msg = record_messages[msg_id]
                similarity = string_similar(no_repeat_msg, msg)
                # print(str(similarity * 100) + "%")
                if similarity > 0.65:
                    repeat_times += 1
                    no_repeat_msg_dict["repeat_ids"].append(msg_id)
            no_repeat_msg_dict["repeat_times"] = repeat_times
            no_repeat_msg_repeat_ids[no_repeat_msg] = no_repeat_msg_dict

        if (int(time.time()) - timestamp) <= 60: # 超时判断
            period = int(time.time()) - timestamp
            msg_count = len(record_messages.keys())
            if period == 0 or msg_count == 0:
                send_rate = 0
            else:
                send_rate = period / msg_count

            if  send_rate < 1.5 and msg_count >= 5: # 频率判断 n秒一条
                mute_time = 10 # 禁言时间，单位为分钟
                user_info = "<b><a href='tg://user?id=" + str(user_id) + "'>" + str(user_id) + "</a></b>"
                if str(user_id) in admins:
                    msg = "🐶管理 " + user_info + ", 请注意您的发言频率！\n作为管理员，<b>您配吗?😕</b>\n<b>请以身作则</b>"
                else:
                    msg = user_info + ", 由于您的发言频率过高\n<b>你已被禁言 " + str(mute_time) + " 分钟</b>"
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
                bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(
                    chat_id=chat_id, text=msg, parse_mode="HTML")
                bot.message_deletor(30, status["chat"]["id"], status["message_id"])

                for msg_id in list(record_messages.keys()): # 删除重复消息
                    status = bot.deleteMessage(chat_id, msg_id)
                    time.sleep(0.5)

                timestamp = int(time.time())
                record_messages = {}

                buf[str(chat_id)][str(user_id)]["record_messages"] = record_messages
                buf[str(chat_id)][str(user_id)]["timestamp"] = timestamp
                ok, _ = bot.buffer.write(buf)
                return

            for msg_dict in list(no_repeat_msg_repeat_ids.values()):
                repeat_times = msg_dict["repeat_times"]
                repeat_ids = msg_dict["repeat_ids"]
                if repeat_times == 3:
                    user_info = "<b><a href='tg://user?id=" + str(user_id) + "'>" + str(user_id) + "</a></b>"
                    if str(user_id) in admins:
                        msg = "管理员 " + user_info + ", 您似乎在重复发送相似消息\n<b>请以身作则😃</b>"
                    else:
                        msg = user_info + ", 检测到您似乎在重复发送相似消息\n<b>继续发送将被禁言，请谨言慎行</b>"
                    bot.sendChatAction(chat_id, "typing")
                    status = bot.sendMessage(
                        chat_id=chat_id, text=msg, parse_mode="HTML")
                    bot.message_deletor(15, status["chat"]["id"], status["message_id"])

                if repeat_times >= 5:
                    mute_time = 10 # 禁言时间，单位为分钟
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
                    bot.sendChatAction(chat_id, "typing")
                    status = bot.sendMessage(
                        chat_id=chat_id, text=msg, parse_mode="HTML")
                    bot.message_deletor(30, status["chat"]["id"], status["message_id"])

                    for msg_id in repeat_ids: # 删除重复消息
                        status = bot.deleteMessage(chat_id, msg_id)
                        if msg_id in record_messages.keys():
                            record_messages.pop(msg_id)
                        time.sleep(0.5)

                    timestamp = int(time.time())
        else:
            timestamp = int(time.time())
            record_messages = {}

        buf[str(chat_id)][str(user_id)]["record_messages"] = record_messages
        buf[str(chat_id)][str(user_id)]["timestamp"] = timestamp
        ok, _ = bot.buffer.write(buf)


def string_similar(str1, str2):
    similarity = difflib.SequenceMatcher(None, str1, str2).quick_ratio()

    return round(similarity, 2)

def Traditional2Simplified(sentence):
    '''
    将sentence中的繁体字转为简体字
    :param sentence: 待转换的句子
    :return: 将句子中繁体字转换为简体字之后的句子
    '''
    sentence = Converter('zh-hans').convert(sentence)
    return sentence

def Simplified2Traditional(sentence):
    '''
    将sentence中的简体字转为繁体字
    :param sentence: 待转换的句子
    :return: 将句子中简体字转换为繁体字之后的句子
    '''
    sentence = Converter('zh-hant').convert(sentence)
    return sentence

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