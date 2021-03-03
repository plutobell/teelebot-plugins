# -*- coding:utf-8 -*-
'''
creation time: 2021-03-03
last_modify: 2021-03-03
'''
import random

def MuteMe(bot, message):

    bot_id = bot.bot_id
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    message_id = message["message_id"]
    chat_type = message["chat"]["type"]
    gap = 15

    if message["chat"]["type"] != "private":
        results = bot.getChatAdministrators(chat_id=chat_id) #判断Bot是否具管理员权限
        admin_status = False
        for admin_user in results:
            if str(admin_user["user"]["id"]) == str(bot_id):
                admin_status = True
        if admin_status != True:
            status = bot.sendChatAction(chat_id, "typing")
            msg = "权限不足，请授予全部权限以使用 MuteMe 插件。"
            status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML")
            bot.message_deletor(30, chat_id, status["message_id"])
            bot.message_deletor(gap, chat_id, message_id)
            return False


    if chat_type == "private": #判断是否为私人对话
        status = bot.sendChatAction(chat_id, "typing")
        status = bot.sendMessage(chat_id, "抱歉，该指令不支持私人会话!", parse_mode="HTML", reply_to_message_id=message_id)
        bot.message_deletor(gap, chat_id, status["message_id"])
    else:
        mute_packages = {
            "1分钟": 60,
            "2分钟": 60 * 2,
            "3分钟": 60 * 3,
            "4分钟": 60 * 4,
            "5分钟": 60 * 5,
            "6分钟": 60 * 6,
            "7分钟": 60 * 7,
            "8分钟": 60 * 8,
            "9分钟": 60 * 9,
            "10分钟": 60 * 10,
            "30分钟": 60 * 30,
            "60分钟": 60 * 60
        }

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

        admins = administrators(bot=bot, chat_id=chat_id)
        if str(user_id) in admins:
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id=chat_id,
                text="抱歉，管理员没有资格获取禁言礼包.🙄",
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, chat_id, status["message_id"])
            return

        mute_time = random.sample(mute_packages.keys(), 1)[0]
        status = bot.restrictChatMember(chat_id=chat_id, user_id=user_id,
            permissions=permissions, until_date=str(mute_packages[mute_time]))
        if status != False:
            msg = "恭喜您获得了 <b>" + mute_time + "</b> 禁言大礼包！😏"
            if mute_time == "60分钟":
                msg = "<b>您就是非酋吧？\n</b>恭喜您获得了 <b>" + mute_time + \
                    "</b> 顶级禁言大礼包！🤣😂\n"
            status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML",
                reply_to_message_id=message_id)

            sticker_path = bot.path_converter(bot.plugin_dir + r"MuteMe/smile.jpg")
            bot.sendSticker(chat_id=chat_id, sticker=sticker_path,
                reply_to_message_id=message_id)
            if mute_time == "60分钟":
                for _ in range(2):
                    bot.sendSticker(chat_id=chat_id, sticker=sticker_path,
                        reply_to_message_id=message_id)


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


