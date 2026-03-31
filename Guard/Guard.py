# -*- coding:utf-8 -*-
'''
creation time: 2020-05-28
last_modify: 2026-03-31
'''
import re
import os
import string
import sqlite3
import time
from cerebras.cloud.sdk import Cerebras
from random import shuffle, randint
from threading import Timer
from captcha.image import ImageCaptcha
from random import randint
from io import BytesIO

restrict_permissions = {
    'can_send_messages': False,
    'can_send_media_messages': False,
    'can_send_polls': False,
    'can_send_other_messages': False,
    'can_add_web_page_previews': False,
    'can_change_info': False,
    'can_invite_users': False,
    'can_pin_messages': False
}

def Guard(bot, message):

    if message["chat"]["type"] == "channel" or message["chat"]["type"] == "private":
        return

    bot_id = bot.bot_id
    root_id = bot.root_id
    plugin_dir = bot.plugin_dir
    message_id = message["message_id"]
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    message_type = message["message_type"]

    gap = 60
    timestamp = time.time() + 5
    db = SqliteDB(bot, plugin_dir)

    if not os.path.exists(bot.path_converter(plugin_dir + "Guard/config.ini")):
        print("Guard: configuration file not found.")
        msg = "要使用 Guard 插件，请bot管理员先设置 config.ini 文件。"
        bot.sendChatAction(chat_id=chat_id, action="typing")
        status = bot.sendMessage(
            chat_id=chat_id, text=msg, parse_mode="HTML")
        bot.message_deletor(15, chat_id, status["message_id"])
        db.close()
        return

    with open(bot.join_plugin_path("config.ini"), "r", encoding="utf-8") as conf:
        lines = conf.readlines()
        if len(lines) >= 3:
            API_KEY = lines[0].strip()
            MODEL = lines[1].strip()
            LOG_GROUP_ID = lines[2].strip()
        else:
            status = bot.sendChatAction(chat_id=chat_id, action="typing")
            msg = "要使用 Guard 插件，请bot管理员先设置 config.ini 文件。"
            status = bot.sendMessage(
                chat_id=chat_id, text=msg, parse_mode="HTML")
            bot.message_deletor(30, status["chat"]["id"], status["message_id"])
            db.close()
            return False

    if message_type == "chat_join_request_data":
        bot.approveChatJoinRequest(chat_id=chat_id, user_id=user_id)

    user_status = "member"
    result = db.select(chat_id=chat_id, user_id=user_id)
    if "reply_markup" in message.keys() and \
        message["message_type"] == "callback_query_data" and \
        message["chat"]["type"] != "private":

        admins = administrators(bot=bot, chat_id=chat_id)
        if str(root_id) not in admins:
            admins.append(str(root_id))

        user = message["click_user"]
        user_id = user["id"]  # 未处理：多用户同时点击的情况
        result = db.select(chat_id=chat_id, user_id=user_id)

        if "first_name" in user.keys():  # Optional (first_name or last_name)
            first_name = user["first_name"].strip()
        else:
            first_name = ""
        if "last_name" in user.keys():
            last_name = user["last_name"].strip()
        else:
            last_name = ""

        if result != False and "/guardupdatingcaptcha" in message["callback_query_data"] and result[2] == str(user_id) and result[1] == str(chat_id):
            if message["callback_query_data"] == "/guardupdatingcaptcha-restricted":
                user_status = "restricted"

            msg = "<b><a href='tg://user?id=" + str(user_id) + "'>" + first_name + " " + last_name + \
                "</a></b> 验证码已手动刷新，请于 <b>" + \
                str((gap + result[5])-int(time.time())) + \
                "</b> 秒内从下方选出与图片一致的验证码。"
            bytes_image, captcha_text = captcha_img()
            reply_markup = reply_markup_dict(captcha_text=captcha_text,
                user_status=user_status, user_id=user_id)
            db.update(
                message_id=result[3], authcode=captcha_text, chat_id=chat_id, user_id=user_id)
            media = {
                "type": "photo",
                "media": "attach://captcha",
                "caption": msg,
                "parse_mode": "HTML"
            }
            files = {"captcha": bytes_image}
            status = bot.editMessageMedia(
                chat_id=chat_id, message_id=result[3],
                media=media, files=files,
                reply_markup=reply_markup)
            if status != False:
                status = bot.answerCallbackQuery(
                    callback_query_id=message["callback_query_id"], text="刷新成功")
            else:
                status = bot.answerCallbackQuery(
                    callback_query_id=message["callback_query_id"], text="刷新失败")

        elif result != False and "/guardcaptchatrue" in message["callback_query_data"] and result[2] == str(user_id) and result[1] == str(chat_id):
            if message["callback_query_data"] == "/guardcaptchatrue-restricted":
                user_status = "restricted"

            status = bot.answerCallbackQuery(
                callback_query_id=message["callback_query_id"], text="正确")
            status = bot.getChat(chat_id=chat_id)
            chat_title = status["title"]

            permissions = status.get("permissions")

            if user_status != "restricted":
                status = bot.restrictChatMember(
                    chat_id=chat_id, user_id=result[2],
                    permissions=permissions, until_date=timestamp+gap+10)

            status = bot.deleteMessage(chat_id=chat_id, message_id=result[3])
            db.delete(chat_id=chat_id, user_id=user_id)
            rr = db.user_insert(chat_id=chat_id, user_id=user_id)
            msg = "<b><a href='tg://user?id=" + \
                str(user_id) + "'>" + first_name + " " + last_name + \
                "</a></b>, 欢迎加入 <b>" + str(chat_title) + "</b>，前3条消息将被检测，请您慎言。"
            status = bot.sendChatAction(chat_id=chat_id, action="typing")
            status = bot.sendMessage(
                chat_id=chat_id, text=msg, parse_mode="HTML")

            bot.message_deletor(30, status["chat"]["id"], status["message_id"])

            log_status, reply_markup = handle_logging(bot,
                content=None, log_group_id=LOG_GROUP_ID,
                user_id=user_id, chat_id=chat_id,
                message_id=message_id,
                reason="人机检测", handle="准许入境")

        elif result != False and "/guardcaptchafalse" in message["callback_query_data"] and result[2] == str(user_id) and result[1] == str(chat_id):
            if "restricted" in message["callback_query_data"]:
                user_status = "restricted"

            status = bot.answerCallbackQuery(
                callback_query_id=message["callback_query_id"], text="不正确")
            msg = "<b><a href='tg://user?id=" + str(user_id) + "'>" + first_name + " " + last_name + \
                "</a></b> 验证码不正确，已刷新，请于 <b>" + \
                str((gap + result[5])-int(time.time())) + \
                "</b> 秒内从下方选出与图片一致的验证码。"
            bytes_image, captcha_text = captcha_img()
            reply_markup = reply_markup_dict(captcha_text=captcha_text,
                user_status=user_status, user_id=user_id)
            db.update(
                message_id=result[3], authcode=captcha_text, chat_id=chat_id, user_id=user_id)
            media = {
                "type": "photo",
                "media": "attach://captcha",
                "caption": msg,
                "parse_mode": "HTML"
            }
            files = {"captcha": bytes_image}
            status = bot.editMessageMedia(
                chat_id=chat_id, message_id=result[3],
                media=media, files=files,
                reply_markup=reply_markup)
            if status != False:
                status = bot.answerCallbackQuery(
                    callback_query_id=message["callback_query_id"], text="刷新成功")
            else:
                status = bot.answerCallbackQuery(
                    callback_query_id=message["callback_query_id"], text="刷新失败")

        elif "/guardmanual" in message["callback_query_data"] and str(user_id) in admins:
            origin_user_id = message["callback_query_data"].split("-")[1]
            result = db.select(chat_id=chat_id, user_id=origin_user_id)

            if result == False: # 消息过期
                status = bot.answerCallbackQuery(
                    callback_query_id=message["callback_query_id"], text="点啥点，关你啥事？", show_alert=True)
                db.close()
                return

            origin_user_info = bot.getChatMember(chat_id=chat_id, user_id=origin_user_id)["user"]
            if "first_name" in origin_user_info.keys():  # Optional (first_name or last_name)
                origin_first_name = origin_user_info["first_name"].strip()
            else:
                origin_first_name = ""
            if "last_name" in origin_user_info.keys():
                origin_last_name = origin_user_info["last_name"].strip()
            else:
                origin_last_name = ""

            if "/guardmanualpass" in message["callback_query_data"]:
                status = bot.deleteMessage(chat_id=chat_id, message_id=result[3])

                status = bot.answerCallbackQuery(
                    callback_query_id=message["callback_query_id"], text="放行成功")
                status = bot.getChat(chat_id=chat_id)
                chat_title = status["title"]

                permissions = status.get("permissions")
                if user_status != "restricted":
                    status = bot.restrictChatMember(
                        chat_id=chat_id, user_id=result[2],
                        permissions=permissions, until_date=timestamp+gap+10)

                db.delete(chat_id=chat_id, user_id=origin_user_id)
                rr = db.user_insert(chat_id=chat_id, user_id=origin_user_id)
                admin_msg = "<b><a href='tg://user?id=" + \
                    str(user_id) + "'>" + first_name + " " + last_name + "</a></b>"
                msg = "<b><a href='tg://user?id=" + \
                    str(origin_user_id) + "'>" + origin_first_name + " " + origin_last_name + \
                    "</a></b>, 您已被管理员 " + admin_msg + " 放行。\n欢迎加入 <b>" + str(chat_title) + "</b>，前3条消息将被检测，请您慎言。"
                status = bot.sendChatAction(chat_id=chat_id, action="typing")
                status = bot.sendMessage(
                    chat_id=chat_id, text=msg, parse_mode="HTML")

                bot.message_deletor(30, status["chat"]["id"], status["message_id"])

                log_status, reply_markup = handle_logging(bot,
                    content="由管理员 " + admin_msg + " 放行", log_group_id=LOG_GROUP_ID,
                    user_id=origin_user_id, chat_id=chat_id,
                    message_id=message_id,
                    reason="人机检测", handle="准许入境")
            elif "/guardmanualkick" in message["callback_query_data"]:
                status = bot.deleteMessage(chat_id=chat_id, message_id=result[3])

                status = bot.answerCallbackQuery(
                    callback_query_id=message["callback_query_id"], text="驱逐成功")

                db.delete(chat_id=chat_id, user_id=origin_user_id)
                status = bot.banChatMember(
                    chat_id=chat_id, user_id=origin_user_id, until_date=timestamp+90)
                #status = bot.unbanChatMember(chat_id=chat_id, user_id=user_id)
                admin_msg = "<b><a href='tg://user?id=" + \
                    str(user_id) + "'>" + first_name + " " + last_name + "</a></b>"
                msg = "<b><a href='tg://user?id=" + \
                    str(origin_user_id) + "'>" + origin_first_name + " " + \
                    origin_last_name + "</a></b> 已被管理员 " + admin_msg + " 驱逐, 没能通过人机检测。"
                status = bot.sendMessage(
                    chat_id=chat_id, text=msg, parse_mode="HTML")

                bot.message_deletor(30, status["chat"]["id"], status["message_id"])

                log_status, reply_markup = handle_logging(bot,
                    content="由管理员 " + admin_msg + " 驱逐", log_group_id=LOG_GROUP_ID,
                    user_id=origin_user_id, chat_id=chat_id,
                    message_id=message_id,
                    reason="人机检测", handle="拒绝入境")

        # 防止接收来自其他插件的CallbackQuery
        elif "/guardupdatingcaptcha" in message["callback_query_data"] or "/guardcaptcha" in message["callback_query_data"]:
            status = bot.answerCallbackQuery(
                callback_query_id=message["callback_query_id"], text="点啥点，关你啥事？", show_alert=True)
        elif "/guardmanual" in message["callback_query_data"]:
            status = bot.answerCallbackQuery(
                callback_query_id=message["callback_query_id"], text="想啥呢？只有管理员可以操作！", show_alert=True)

    # 兼容 Bot API version < 5.3
    elif "new_chat_members" in message.keys() or \
        "left_chat_member" in message.keys():
        bot.deleteMessage(chat_id=chat_id, message_id=message_id)

    # 入群
    elif message_type == "chat_member_data" and \
        message["old_chat_member"]["status"] in ["left", "kicked"] and \
        message["new_chat_member"]["status"] in ["creator", "administrator", "member", "restricted"]:

        new_chat_member = message["new_chat_member"]
        user_id = new_chat_member["user"]["id"]

        results = bot.getChatAdministrators(chat_id=chat_id)  # 判断Bot是否具管理员权限
        admin_status = False
        for admin_user in results:
            if str(admin_user["user"]["id"]) == str(bot_id):
                admin_status = True
        if admin_status != True:
            status = bot.sendChatAction(chat_id=chat_id, action="typing")
            msg = "权限不足，请授予删除消息及封禁用户权限以使用 Guard 插件。"
            status = bot.sendMessage(
                chat_id=chat_id, text=msg, parse_mode="HTML")
            bot.message_deletor(30, status["chat"]["id"], status["message_id"])
            db.close()
            return False

        if new_chat_member["status"] != "restricted":
            status = bot.restrictChatMember(
                chat_id=chat_id, user_id=user_id,
                permissions=restrict_permissions,
                until_date=timestamp+gap+10)

        if "first_name" in new_chat_member["user"].keys():  # Optional (first_name or last_name)
            first_name = new_chat_member["user"]["first_name"].strip()
        else:
            first_name = ""
        if "last_name" in new_chat_member["user"].keys():
            last_name = new_chat_member["user"]["last_name"].strip()
        else:
            last_name = ""
        name = str(first_name + last_name).strip()
        #print("New Member：", user_id, first_name)
        name_demoji = filter_emoji(name)
        is_spam = isSpamMessage(API_KEY=API_KEY, message=name_demoji, MODEL=MODEL)
        if is_spam == "yes":
            status = bot.banChatMember(
                chat_id=chat_id, user_id=user_id, until_date=timestamp+90)
            # status = bot.deleteMessage(chat_id=chat_id, message_id=message_id)
            log_status, reply_markup = handle_logging(bot,
                content=name, log_group_id=LOG_GROUP_ID,
                user_id=user_id, chat_id=chat_id,
                message_id=message_id,
                reason="名字违规", handle="驱逐出境")
            #status = bot.unbanChatMember(chat_id=chat_id, user_id=user_id)
            msg = "<b><a href='tg://user?id=" + \
                str(user_id) + "'>" + str(user_id) + \
                "</a></b> 的名字<b> 违规</b>，已驱逐出境。"
            status = bot.sendChatAction(chat_id=chat_id, action="typing")
            status = bot.sendMessage(
                chat_id=chat_id, text=msg, parse_mode="HTML",
                reply_markup=reply_markup, del_msg_after=60)

            # bot.message_deletor(
            #     30, status["chat"]["id"], status["message_id"])
        else:
            # status = bot.deleteMessage(
            #     chat_id=chat_id, message_id=message_id)
            msg = "<b><a href='tg://user?id=" + \
                str(user_id) + "'>" + first_name + " " + last_name + \
                "</a></b> 您好，本群已启用人机检测，请于 <b>" + \
                str(gap) + "</b> 秒内从下方选出与图片一致的验证码。"
            bytes_image, captcha_text = captcha_img()
            reply_markup = reply_markup_dict(captcha_text=captcha_text,
                user_status=user_status, user_id=user_id)
            status = bot.sendPhoto(chat_id=chat_id, photo=bytes_image,
                                    caption=msg, parse_mode="HTML", reply_markup=reply_markup)
            db.insert(chat_id=chat_id, user_id=user_id,
                        message_id=status["message_id"], authcode=captcha_text)
            timer = Timer(
                gap + 1, timer_func, args=[bot, plugin_dir, gap, chat_id, user_id, first_name, last_name, message_id, LOG_GROUP_ID])
            timer.start()

    # 离群
    elif message_type == "chat_member_data" and \
        message["old_chat_member"]["status"] in ["creator", "administrator", "member", "restricted"] and \
        message["new_chat_member"]["status"] in ["left", "kicked"]:
        results = bot.getChatAdministrators(chat_id=chat_id)  # 判断Bot是否具管理员权限
        admin_status = False
        for admin_user in results:
            if str(admin_user["user"]["id"]) == str(bot_id):
                admin_status = True
        if admin_status != True:
            status = bot.sendChatAction(chat_id=chat_id, action="typing")
            msg = "权限不足，请授予删除消息及封禁用户权限以使用 Guard 插件。"
            status = bot.sendMessage(
                chat_id=chat_id, text=msg, parse_mode="HTML")
            bot.message_deletor(30, status["chat"]["id"], status["message_id"])
            db.close()
            return False

        new_chat_member = message["new_chat_member"]
        req = db.user_select(
            chat_id=message["chat"]["id"], user_id=new_chat_member["user"]["id"])
        time.sleep(2)
        if req != False:
            db.user_delete(
                chat_id=message["chat"]["id"], user_id=new_chat_member["user"]["id"])

        result = db.select(
            chat_id=message["chat"]["id"], user_id=new_chat_member["user"]["id"])
        if result != False and result[2] == str(user_id) and result[1] == str(chat_id) and message["chat"]["type"] != "private":
            status = bot.deleteMessage(
                chat_id=message["chat"]["id"], message_id=result[3])
            db.delete(chat_id=message["chat"]["id"],
                    user_id=new_chat_member["user"]["id"])

        user_id = new_chat_member["user"]["id"]
        if "first_name" in new_chat_member["user"].keys():  # Optional (first_name or last_name)
            first_name = new_chat_member["user"]["first_name"].strip()
        else:
            first_name = ""
        if "last_name" in new_chat_member["user"].keys():
            last_name = new_chat_member["user"]["last_name"].strip()
        else:
            last_name = ""
        name = str(first_name + last_name).strip()

        name_demoji = filter_emoji(name)
        is_spam = isSpamMessage(API_KEY=API_KEY, message=name_demoji, MODEL=MODEL)
        if is_spam == "yes":
            # status = bot.deleteMessage(chat_id=chat_id, message_id=message_id)
            pass
        else:
            # status = bot.deleteMessage(chat_id=chat_id, message_id=message_id)
            msg = "<b><a href='tg://user?id=" + \
                str(user_id) + "'>" + first_name + " " + last_name + \
                "</a></b>" + " 离开了我们。"
            status = bot.sendChatAction(chat_id=chat_id, action="typing")
            status = bot.sendMessage(
                chat_id=chat_id, text=msg, parse_mode="HTML")

            bot.message_deletor(30, status["chat"]["id"], status["message_id"])

    elif "text" in message.keys() or "caption" in message.keys():
        text = ""
        if "text" in message.keys():
            text += message["text"]
        if "caption" in message.keys():
            text += message["caption"]
        gap = 15

        if message["chat"]["type"] != "private":  # 监测群链接广告
            req = db.user_select(chat_id, user_id)
            if req != False:
                req = list(req)
                if req[3] < 2: # 监测前三条消息
                    req[3] += 1
                    db.user_update(chat_id=chat_id, user_id=user_id,
                                message_times=req[3], spam_times=req[4])
                    text_demoji = filter_emoji(text.strip())
                    is_spam = isSpamMessage(API_KEY=API_KEY, message=text_demoji, MODEL=MODEL)
                    if is_spam == "yes":
                        req[4] += 2
                        db.user_update(chat_id=chat_id, user_id=user_id,
                                    message_times=req[3], spam_times=req[4])
                    if req[3] == 1 and "forward_from_message_id" in message.keys():
                        req[4] += 2
                        db.user_update(chat_id=chat_id, user_id=user_id,
                                    message_times=req[3], spam_times=req[4])
                    if "t.me/" in text.strip().replace('"', "").replace("'", ""):
                        req[4] += 1
                        db.user_update(chat_id=chat_id, user_id=user_id,
                                    message_times=req[3], spam_times=req[4])
                    if (req[3] == 1 and req[4] == 1) or req[4] >= 2:
                        bot.banChatMember(
                            chat_id=req[1], user_id=req[2], until_date=timestamp+90)
                        bot.deleteMessage(
                            chat_id=req[1], message_id=message_id)
                        log_status, reply_markup = handle_logging(bot,
                            content=text, log_group_id=LOG_GROUP_ID,
                            user_id=user_id, chat_id=chat_id,
                            message_id=message_id,
                            reason="消息违规", handle="驱逐出境")
                        msg = "<b><a href='tg://user?id=" + \
                            str(user_id) + "'>" + str(user_id) + \
                            "</a></b> 的消息<b> 违规</b>，已驱逐出境。"
                        status = bot.sendChatAction(chat_id=chat_id, action="typing")
                        status = bot.sendMessage(
                            chat_id=chat_id, text=msg, parse_mode="HTML",
                            reply_markup=reply_markup, del_msg_after=60)
                        #bot.message_deletor(30, status["chat"]["id"], status["message_id"])
                        db.user_delete(chat_id, user_id)
                else:
                    db.user_delete(chat_id, user_id)

        if message["chat"]["type"] != "private":
            admins = administrators(bot=bot, chat_id=chat_id)
            if str(root_id) not in admins:
                admins.append(str(root_id))  # root permission

    db.close()


def timer_func(bot, plugin_dir, gap, chat_id, user_id, first_name, last_name, message_id, LOG_GROUP_ID):
    timestamp = time.time() + 5
    db = SqliteDB(bot, plugin_dir)
    result = db.select(chat_id=chat_id, user_id=user_id)
    if result != False and result[2] == str(user_id) != "private":
        if int(time.time()) > result[5] + gap:
            status = bot.deleteMessage(chat_id=chat_id, message_id=result[3])
            db.delete(chat_id=chat_id, user_id=user_id)
            status = bot.banChatMember(
                chat_id=chat_id, user_id=user_id, until_date=timestamp+90)
            #status = bot.unbanChatMember(chat_id=chat_id, user_id=user_id)
            msg = "<b><a href='tg://user?id=" + \
                str(user_id) + "'>" + first_name + " " + \
                last_name + "</a></b> 没能通过人机检测。"
            status = bot.sendMessage(
                chat_id=chat_id, text=msg, parse_mode="HTML")

            bot.message_deletor(30, status["chat"]["id"], status["message_id"])

            log_status, reply_markup = handle_logging(bot,
                content=None, log_group_id=LOG_GROUP_ID,
                user_id=user_id, chat_id=chat_id,
                message_id=message_id,
                reason="人机检测", handle="拒绝入境")
            
    db.close()


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


def shuffle_str(s):
    str_list = list(s)
    shuffle(str_list)

    return ''.join(str_list)

def filter_emoji(desstr, restr=''):
    try:
        co = re.compile(u'[\U00010000-\U0010ffff]')
    except re.error:
        co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')

    return co.sub(restr, desstr)

def captcha_img(width=160, height=60, font_sizes=(50, 55, 60), fonts=None):

    captcha_len = 5
    # captcha_range = string.digits + string.ascii_letters #大小写+数字
    captcha_range = string.ascii_lowercase
    captcha_range_len = len(captcha_range)
    captcha_text = ""
    for i in range(captcha_len):
        captcha_text += captcha_range[randint(0, captcha_range_len-1)]

    img = ImageCaptcha(width=width, height=height, font_sizes=font_sizes)
    image = img.generate_image(captcha_text)

    # save to bytes
    bytes_image = BytesIO()
    image.save(bytes_image, format='png')
    bytes_image = bytes_image.getvalue()

    return bytes_image, captcha_text


def reply_markup_dict(captcha_text, user_status, user_id):
    answer = randint(0, 3)
    options = []
    while True:
        for i in range(4):  # 生成答案列表
            if answer == i:
                options.append(captcha_text)
            else:
                options.append(shuffle_str(captcha_text))
        if len(options) == len(set(options)):
            break
        else:  # 存在重复的情况下清空options，防止死循环
            options = []

    callback_data = []
    for i in range(4):  # 生成callback_data列表
        if answer == i:
            if user_status == "restricted":
                callback_data.append("/guardcaptchatrue-restricted")
            else:
                callback_data.append("/guardcaptchatrue")
        else:
            if user_status == "restricted":
                callback_data.append("/guardcaptchafalse" + str(i) + "-restricted")
            else:
                callback_data.append("/guardcaptchafalse" + str(i))

        if user_status == "restricted":
            update_captcha = "/guardupdatingcaptcha-restricted"
        else:
            update_captcha = "/guardupdatingcaptcha"


    inlineKeyboard = [
        [
            {"text": options[0], "callback_data":callback_data[0]},
            {"text": options[1], "callback_data":callback_data[1]},
        ],
        [
            {"text": options[2], "callback_data":callback_data[2]},
            {"text": options[3], "callback_data":callback_data[3]},
        ],
        [
            {"text": "看不清，换一张", "callback_data": update_captcha},
        ],
        [
            {"text": "放行", "callback_data":"/guardmanualpass-" + str(user_id)},
            {"text": "驱逐", "callback_data":"/guardmanualkick-" + str(user_id)},
        ]
    ]
    reply_markup = {
        "inline_keyboard": inlineKeyboard
    }
    # print(inlineKeyboard)

    return reply_markup


def handle_logging(bot, content, log_group_id, user_id, chat_id, message_id, reason, handle):
    status = bot.getChat(chat_id=log_group_id)
    log_chat_username = status["username"]

    status = bot.getChat(chat_id=chat_id)
    chat_username = status.get("username", "nullusername,/")
    chat_title = ""

    if chat_username == "nullusername,/" or len(chat_username) == 0:
        chat_username = chat_id
        chat_title = chat_id
    else:
        chat_title = "@" + chat_username

    content_len_limit = 200
    if content is not None and len(content) > content_len_limit:
        content = content[:content_len_limit] + "..."

    timestamp = time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(time.time()))

    msg = "存档时间: <i>" + str(timestamp) + "</i> \n" + \
        "事件编号: <i><a href='https://t.me/" + \
        str(chat_username) + "/" + str(message_id) +"'>" + str(message_id) + "</a></i> \n" + \
        "涉及用户: <i><a href='tg://user?id=" + \
        str(user_id) + "'>" + str(user_id) + "</a></i> \n" + \
        "涉及群组: <i><a href='https://t.me/" + \
        str(chat_username) + "'>" + str(chat_title) + "</a></i> \n" + \
        "触发原因: <i>" + str(reason) + "</i> \n" + \
        "处理方式: <i>" + str(handle) + "</i> \n"

    if content is not None:
        msg += "消息内容: \n <i>" + str(content) + "</i>"


    status = bot.sendMessage(chat_id=log_group_id, text=msg, parse_mode="HTML", disable_web_page_preview=True)
    if status is not False:
        inlineKeyboard = [
            [
                {"text": "操作日志", "url": "https://t.me/" + str(log_chat_username) + "/" + str(status["message_id"])}
            ]
        ]
        reply_markup = {
            "inline_keyboard": inlineKeyboard
        }
        return True, reply_markup
    else:
        inlineKeyboard = [
            [
                {"text": "日志存放失败", "url": ""}
            ]
        ]
        reply_markup = {
            "inline_keyboard": inlineKeyboard
        }
        return False, reply_markup


class SqliteDB(object):
    def __init__(self, bot, plugin_dir):
        '''
        Open the connection
        '''
        self.conn = sqlite3.connect(
            bot.path_converter(plugin_dir + "Guard/captcha.db"), check_same_thread=False)  # 只读模式加上uri=True
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS captcha_list (id INTEGER PRIMARY KEY autoincrement, chat_id TEXT, user_id TEXT, message_id TEXT, authcode TEXT, timestamp INTEGER)")
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS new_user_list (id INTEGER PRIMARY KEY autoincrement, chat_id TEXT, user_id TEXT, message_times INTEGER, spam_times INTEGER)")

    def close(self):
        '''
        Close the connection
        '''
        self.cursor.close()
        self.conn.commit()
        self.conn.close()

    def insert(self, chat_id, user_id, message_id, authcode):
        '''
        Insert
        '''
        timestamp = int(time.time())
        self.cursor.execute("INSERT INTO captcha_list (chat_id, user_id, message_id, authcode, timestamp) VALUES (?,?,?,?,?)",
                            (chat_id, user_id, message_id, authcode, timestamp))

        if self.cursor.rowcount == 1:
            return True
        else:
            return False

    def select(self, chat_id, user_id):
        '''
        Select
        '''
        self.cursor.execute(
            "SELECT * FROM captcha_list WHERE chat_id=? AND user_id=?", (chat_id, user_id))
        result = self.cursor.fetchall()

        if result:
            result = result[0]
        else:
            result = False

        return result

    def delete(self, chat_id, user_id):
        '''
        Delete
        '''
        self.cursor.execute(
            "DELETE FROM captcha_list WHERE chat_id=? AND user_id=?", (chat_id, user_id))

        if self.cursor.rowcount == 1:
            return True
        else:
            return False

    def update(self, message_id, authcode, chat_id, user_id, timestamp=None):
        '''
        Update
        '''
        if timestamp == None:
            self.cursor.execute("UPDATE captcha_list SET message_id=?, authcode=? WHERE chat_id=? and user_id=?", (
                message_id, authcode, chat_id, user_id))
        else:
            self.cursor.execute("UPDATE captcha_list SET message_id=?, authcode=?, timestamp=? WHERE chat_id=? and user_id=?", (
                message_id, authcode, int(timestamp), chat_id, user_id))

        if self.cursor.rowcount == 1:
            return True
        else:
            return False

    # new_user_list
    def user_insert(self, chat_id, user_id):
        '''
        User Insert
        '''
        message_times = spam_times = 0
        self.cursor.execute("INSERT INTO new_user_list (chat_id, user_id, message_times, spam_times) VALUES (?,?,?,?)",
                            (chat_id, user_id, message_times, spam_times))

        if self.cursor.rowcount == 1:
            return True
        else:
            return False

    def user_select(self, chat_id, user_id):
        '''
        User Select
        '''
        self.cursor.execute(
            "SELECT * FROM new_user_list WHERE chat_id=? AND user_id=?", (chat_id, user_id))
        result = self.cursor.fetchall()

        if result:
            result = result[0]
        else:
            result = False

        return result

    def user_delete(self, chat_id, user_id):
        '''
        User Delete
        '''
        self.cursor.execute(
            "DELETE FROM new_user_list WHERE chat_id=? AND user_id=?", (chat_id, user_id))

        if self.cursor.rowcount == 1:
            return True
        else:
            return False

    def user_update(self, chat_id, user_id, message_times, spam_times):
        '''
        User Update
        '''
        self.cursor.execute("UPDATE new_user_list SET message_times=?, spam_times=? WHERE chat_id=? and user_id=?",
                            (message_times, spam_times, chat_id, user_id))

        if self.cursor.rowcount == 1:
            return True
        else:
            return False


def isSpamMessage(API_KEY: str, message: str, MODEL="qwen-3-32b") -> str:
    prompt = (
        "你是一个广告检测 API，用于判断用户在群聊中发送的消息是否属于广告、诈骗或色情信息。\n\n"

        "【应判定为 yes 的情况】：\n"
        "1. 明确的产品推广、代购、引流行为；\n"
        "2. 发送群号、拉人入群、发邀请码等内容；\n"
        "3. 包含外部链接（如网址、公众号、QQ群、Telegram 等）；\n"
        "4. 推广加密货币、空投、赌博、色情、诈骗等违规内容；\n"
        "5. 含有“@用户名”或“联系我”等引导联系方式，且伴随高额收益承诺；\n"
        "6. 使用“加入我们”、“私聊我”、“免费领取”、“点击链接”等具有引导意图的用语；\n"
        "7. 出现“自动发卡”、“自动下单”、“秒到账”、“售卖”、“代充”、“返利机器人”等交易导向术语；\n"
        "8. 包含“@用户名”并配合炫富、引导赚钱等语句（如“一天赚5万”、“搞一辆奔驰”等）；\n"
        "9. 出现“VX详聊”、“加我聊”、“买VX”、“联系我”等简短引导语，即使极短，也判定为广告；\n"
        "10. 出现暗示性服务（如“陪拍”、“妹妹”、“时结”等）并包含价格信息（如“300一次”、“600一小时”等），构成色情交易推广，判定为 yes；\n"
        "11. 出现服务或行为词（如“拍照”、“接单”、“来活”、“兼职”等），同时出现金额（如“每天1000u”、“一次300”），再配合引导语（如“请看简介”、“加我VX”、“详情主页看”），构成引流广告，判定为 yes。\n"
        "12. 包含“@用户名”或直接@他人，配合引导性话术（如“来干活”、“缺人”、“速教”、“主页看”等）和炫富或收益承诺（如“买宝马”、“搞几个W”、“赚钱”等），即使带粗俗语气、玩笑语气、非正式用词、错别字或变形词，也判定为广告引流，判定为 yes。\n\n"

        "【应判定为 no 的情况】：\n"
        "- 正常聊天、吐槽、玩笑内容；\n"
        "- 含有 BT、VPN、AI 等词但无推广意图；\n"
        "- 模糊词汇、昵称、视频标题、无害信息；\n"
        "- 表情符号或乱码（如“🌚”、“？？？”、“……”等）即使重复出现也不构成广告；\n"
        "- 单个字、无意义短语或极短内容，且无明确推广语句；\n"
        "- 品牌词（如小米、抖音等）单独出现，除非带有推广意图；\n"
        "- 出现“返现”、“返佣”、“返利”等词，若无推广/引导语句，则判定为 no；\n"
        "- 仅含变形字符联系方式（如 WhatsApp、微信号、电话号码），且无推广引导，判定为 no；\n"
        "- 单独提及品牌词（如“淘宝”、“京东”等）且无推广或引导语句，判定为 no；\n"
        "- 技术相关功能描述、接口调用、数据获取等明确非广告内容，判定为 no；\n"
        "- 技术文档或开发者链接（如 GitHub、docs.python.org、StackOverflow），即使含参数字段，也判定为 no；\n"
        "- 纯联系方式且无推广、引导语句，判定为 no；\n"
        "- 其他无明确推广、引流、联系方式引导的内容。\n\n"

        "请严格遵守以下规则判定：\n"
        "1. 符合“应判定为 yes”的条件，返回 yes；\n"
        "2. 符合“应判定为 no”的条件，返回 no；\n"
        "3. 其他情况统一判定为 no；\n"
        "4. 如上下文不足或难以判断，统一返回 no。\n\n"

        "请不要根据关键词联想、暗示或语义推测判断广告，仅根据明确规则判断。\n"
        "如上下文不足或难以判断，请统一返回 no。\n\n"

        "【示例判断】\n"
        "“加入我们，点击链接” → yes\n"
        "“币安有返现” → no\n"
        "“BT资源丰富” → no\n"
        "“拉群邀请码” → yes\n"
        "“卖” → no\n"
        "“买卖” → no\n"
        "“点击购买” → yes\n"
        "“🌚🌚🌚” → no\n"
        "“啊” → no\n"
        "“……” → no\n"
        "“有” → no\n"
        "“VX详聊” → yes\n"
        "“买VX” → yes\n"
        "“接入个淘宝 评价图片随机获取” → no\n"
        "“卧槽这个人 @abc 太牛了 一天赚5万买奔驰了” → yes\n"
        "“快来给妹妹拍照 一张6百 时结🥰” → yes\n"
        "“妹妹陪玩 时结 300一次” → yes\n"
        "“汽车拍照，每天1000u，请看兼介🥰” → yes\n"
        "“@abc 太牛了 一天搞几个W 缺人速教” → yes\n"
        "“兄弟们别吹牛了 来干活 一星期带你买宝马 @xxx” → yes\n"
        "“https://docs.python-telegram-bot.org/en/v20.2/...” → no\n"
        "“/submitpayload?user_id=xxx&payload=xxx” → no\n"
        "“WhatsApp +123 456 7890” → no\n"
        "“RM ᴡʜᴀᴛˢᴀᴘᴘ ⁺¹²³⁻⁴⁵⁶⁻⁷⁸⁹⁰” → no\n"
        "“？？？？？” → no\n\n"

        "最终输出只能为英文小写 yes 或 no，仅返回其一，禁止包含标点、换行、解释或其他字符。"
    )

    try:
        client = Cerebras(
            api_key= API_KEY,
        )
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": f"{message}"
                }
            ],
            extra_body={
                # "disable_reasoning": True
            },
            model=MODEL
        )

        req = chat_completion.choices[0].message.content.strip()

        if req.startswith("yes") or req.startswith("是"):
            return "yes"
        return "no"

    except Exception as e:
        print("AI 判断失败：", e)
        return "no"