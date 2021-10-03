# -*- coding:utf-8 -*-
'''
creation time: 2020-05-28
last_modify: 2021-06-26
'''
from collections import defaultdict
import re
import os
import string
import sqlite3
import time
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
    bot_id = bot.bot_id
    root_id = bot.root_id
    plugin_dir = bot.plugin_dir
    repl = "<*>"
    DFA = DFAFilter()
    DFA.parse(bot.path_converter(plugin_dir + "Guard/keywords"))
    message_id = message["message_id"]
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    message_type = message["message_type"]

    gap = 60
    db = SqliteDB(bot, plugin_dir)

    if message["chat"]["type"] != "private" and message_type == "text": # 初始化
        text = message["text"]
        if text[:len("/guardinit")] == "/guardinit":
            if str(user_id) != str(root_id):
                msg = "抱歉，您无权操作。"
                bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(
                    chat_id=chat_id, text=msg, parse_mode="HTML")
                bot.message_deletor(15, chat_id, status["message_id"])
                return

            text_list = text.strip(" ").split(" ", 1)
            if len(text_list) == 2:
                logging_channel = text_list[1].replace(" ", "")
                if logging_channel[0] != "@":
                    msg = "频道用户名格式错误，请带上'@'符号。"
                    bot.sendChatAction(chat_id, "typing")
                    status = bot.sendMessage(
                        chat_id=chat_id, text=msg, parse_mode="HTML")
                    bot.message_deletor(15, chat_id, status["message_id"])
                    return
                try:
                    status = bot.getChat(chat_id=logging_channel)
                    if status != False:
                        id = status["id"]
                        with open(bot.path_converter(plugin_dir + "Guard/config.ini"), "w", encoding="utf-8") as f:
                            f.write(str(id))

                    msg = "Guard插件日志存放频道设置成功。"
                    bot.sendChatAction(chat_id, "typing")
                    status = bot.sendMessage(
                        chat_id=chat_id, text=msg, parse_mode="HTML")
                    bot.message_deletor(15, chat_id, status["message_id"])
                    return
                except:
                    msg = "Guard插件日志存放频道设置失败，请重试。"
                    bot.sendChatAction(chat_id, "typing")
                    status = bot.sendMessage(
                        chat_id=chat_id, text=msg, parse_mode="HTML")
                    bot.message_deletor(15, chat_id, status["message_id"])
                    return
            else:
                msg = "指令格式错误。e.g.: /guardinit @ channel_username"
                bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(
                    chat_id=chat_id, text=msg, parse_mode="HTML")
                bot.message_deletor(15, chat_id, status["message_id"])
                return

    if not os.path.exists(bot.path_converter(plugin_dir + "Guard/config.ini")):
        print("Guard: configuration file not found.")
        msg = "要使用Guard插件请先设置日志存放频道\n请Bot管理员使用以下指令设置:\ne.g.: /guardinit @ channel_username"
        bot.sendChatAction(chat_id, "typing")
        status = bot.sendMessage(
            chat_id=chat_id, text=msg, parse_mode="HTML")
        bot.message_deletor(15, chat_id, status["message_id"])
        return

    with open(bot.path_converter(plugin_dir + "Guard/config.ini"), "r", encoding="utf-8") as f:
        log_group_id = f.readline().strip()

    user_status = "member"
    result = db.select(chat_id=chat_id, user_id=user_id)
    if "reply_markup" in message.keys() and\
        message["message_type"] == "callback_query_data" and\
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
            status = bot.editMessageMedia(
                chat_id=chat_id, message_id=result[3], type_="photo", media=bytes_image,
                caption=msg, parse_mode="HTML", reply_markup=reply_markup)
            if status != False:
                status = bot.answerCallbackQuery(
                    message["callback_query_id"], text="刷新成功")
            else:
                status = bot.answerCallbackQuery(
                    message["callback_query_id"], text="刷新失败")
        elif result != False and "/guardcaptchatrue" in message["callback_query_data"] and result[2] == str(user_id) and result[1] == str(chat_id):
            if message["callback_query_data"] == "/guardcaptchatrue-restricted":
                user_status = "restricted"

            status = bot.answerCallbackQuery(
                message["callback_query_id"], text="正确")
            status = bot.getChat(chat_id=chat_id)
            chat_title = status["title"]

            permissions = status.get("permissions")
            if user_status != "restricted":
                status = bot.restrictChatMember(
                    chat_id=chat_id, user_id=result[2], permissions=permissions)

            status = bot.deleteMessage(chat_id=chat_id, message_id=result[3])
            db.delete(chat_id=chat_id, user_id=user_id)
            rr = db.user_insert(chat_id=chat_id, user_id=user_id)
            msg = "<b><a href='tg://user?id=" + \
                str(user_id) + "'>" + first_name + " " + last_name + \
                "</a></b>, 欢迎加入 <b>" + str(chat_title) + "</b>。"
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(
                chat_id=chat_id, text=msg, parse_mode="HTML")

            bot.message_deletor(30, status["chat"]["id"], status["message_id"])

            log_status, reply_markup = handle_logging(bot,
                content=None, log_group_id=log_group_id,
                user_id=user_id, chat_id=chat_id,
                message_id=message_id,
                reason="人机检测", handle="准许入境")

        elif result != False and "/guardcaptchafalse" in message["callback_query_data"] and result[2] == str(user_id) and result[1] == str(chat_id):
            if "restricted" in message["callback_query_data"]:
                user_status = "restricted"

            status = bot.answerCallbackQuery(
                message["callback_query_id"], text="不正确")
            msg = "<b><a href='tg://user?id=" + str(user_id) + "'>" + first_name + " " + last_name + \
                "</a></b> 验证码不正确，已刷新，请于 <b>" + \
                str((gap + result[5])-int(time.time())) + \
                "</b> 秒内从下方选出与图片一致的验证码。"
            bytes_image, captcha_text = captcha_img()
            reply_markup = reply_markup_dict(captcha_text=captcha_text,
                user_status=user_status, user_id=user_id)
            db.update(
                message_id=result[3], authcode=captcha_text, chat_id=chat_id, user_id=user_id)
            status = bot.editMessageMedia(
                chat_id=chat_id, message_id=result[3], type_="photo", media=bytes_image,
                caption=msg, parse_mode="HTML", reply_markup=reply_markup)
            if status != False:
                status = bot.answerCallbackQuery(
                    message["callback_query_id"], text="刷新成功")
            else:
                status = bot.answerCallbackQuery(
                    message["callback_query_id"], text="刷新失败")

        elif "/guardmanual" in message["callback_query_data"] and str(user_id) in admins:
            origin_user_id = message["callback_query_data"].split("-")[1]
            result = db.select(chat_id=chat_id, user_id=origin_user_id)

            if result == False: # 消息过期
                status = bot.answerCallbackQuery(
                    message["callback_query_id"], text="点啥点，关你啥事？", show_alert=True)
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
                    message["callback_query_id"], text="放行成功")
                status = bot.getChat(chat_id=chat_id)
                chat_title = status["title"]

                permissions = status.get("permissions")
                if user_status != "restricted":
                    status = bot.restrictChatMember(
                        chat_id=chat_id, user_id=result[2], permissions=permissions)

                db.delete(chat_id=chat_id, user_id=origin_user_id)
                rr = db.user_insert(chat_id=chat_id, user_id=origin_user_id)
                admin_msg = "<b><a href='tg://user?id=" + \
                    str(user_id) + "'>" + first_name + " " + last_name + "</a></b>"
                msg = "<b><a href='tg://user?id=" + \
                    str(origin_user_id) + "'>" + origin_first_name + " " + origin_last_name + \
                    "</a></b>, 您已被管理员 " + admin_msg + " 放行。\n欢迎加入 <b>" + str(chat_title) + "</b>。"
                status = bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(
                    chat_id=chat_id, text=msg, parse_mode="HTML")

                bot.message_deletor(30, status["chat"]["id"], status["message_id"])

                log_status, reply_markup = handle_logging(bot,
                    content="由管理员 " + admin_msg + " 放行", log_group_id=log_group_id,
                    user_id=origin_user_id, chat_id=chat_id,
                    message_id=message_id,
                    reason="人机检测", handle="准许入境")
            elif "/guardmanualkick" in message["callback_query_data"]:
                status = bot.deleteMessage(chat_id=chat_id, message_id=result[3])

                status = bot.answerCallbackQuery(
                    message["callback_query_id"], text="驱逐成功")

                db.delete(chat_id=chat_id, user_id=origin_user_id)
                status = bot.banChatMember(
                    chat_id=chat_id, user_id=origin_user_id, until_date=35)
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
                    content="由管理员 " + admin_msg + " 驱逐", log_group_id=log_group_id,
                    user_id=origin_user_id, chat_id=chat_id,
                    message_id=message_id,
                    reason="人机检测", handle="拒绝入境")

        # 防止接收来自其他插件的CallbackQuery
        elif "/guardupdatingcaptcha" in message["callback_query_data"] or "/guardcaptcha" in message["callback_query_data"]:
            status = bot.answerCallbackQuery(
                message["callback_query_id"], text="点啥点，关你啥事？", show_alert=True)
        elif "/guardmanual" in message["callback_query_data"]:
            status = bot.answerCallbackQuery(
                message["callback_query_id"], text="想啥呢？只有管理员可以操作！", show_alert=True)

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
            status = bot.sendChatAction(chat_id, "typing")
            msg = "权限不足，请授予删除消息及封禁用户权限以使用 Guard 插件。"
            status = bot.sendMessage(
                chat_id=chat_id, text=msg, parse_mode="HTML")
            bot.message_deletor(30, status["chat"]["id"], status["message_id"])
            return False

        if new_chat_member["status"] != "restricted":
            status = bot.restrictChatMember(
                chat_id=chat_id, user_id=user_id, permissions=restrict_permissions, until_date=gap+5)

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
        result = DFA.filter(name_demoji, repl)
        if (repl in result and len(name) > 9) or (len(name) > 25):
            status = bot.banChatMember(
                chat_id=chat_id, user_id=user_id, until_date=35)
            status = bot.deleteMessage(
                chat_id=chat_id, message_id=message_id)
            log_status, reply_markup = handle_logging(bot,
                content=name, log_group_id=log_group_id,
                user_id=user_id, chat_id=chat_id,
                message_id=message_id,
                reason="名字违规", handle="驱逐出境")
            #status = bot.unbanChatMember(chat_id=chat_id, user_id=user_id)
            msg = "<b><a href='tg://user?id=" + \
                str(user_id) + "'>" + str(user_id) + \
                "</a></b> 的名字<b> 违规</b>，已驱逐出境。"
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(
                chat_id=chat_id, text=msg, parse_mode="HTML",
                reply_markup=reply_markup)

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
                gap + 1, timer_func, args=[bot, plugin_dir, gap, chat_id, user_id, first_name, last_name, message_id, log_group_id])
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
            status = bot.sendChatAction(chat_id, "typing")
            msg = "权限不足，请授予删除消息及封禁用户权限以使用 Guard 插件。"
            status = bot.sendMessage(
                chat_id=chat_id, text=msg, parse_mode="HTML")
            bot.message_deletor(30, status["chat"]["id"], status["message_id"])
            return False

        new_chat_member = message["new_chat_member"]
        req = db.user_select(
            chat_id=message["chat"]["id"], user_id=new_chat_member["user"]["id"])
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
        result = DFA.filter(name_demoji, repl)
        if (repl in result and len(name) > 9) or (len(name) > 25):
            status = bot.deleteMessage(chat_id=chat_id, message_id=message_id)
        else:
            # status = bot.deleteMessage(chat_id=chat_id, message_id=message_id)
            msg = "<b><a href='tg://user?id=" + \
                str(user_id) + "'>" + first_name + " " + last_name + \
                "</a></b>" + " 离开了我们。"
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(
                chat_id=chat_id, text=msg, parse_mode="HTML")

            bot.message_deletor(30, status["chat"]["id"], status["message_id"])

    elif "text" in message.keys() or "caption" in message.keys():
        text = ""
        if "text" in message.keys():
            text += message["text"]
        if "caption" in message.keys():
            text += message["caption"]
        prefix = "guard"
        gap = 15

        command = {
            "/guardadd": "add"
        }
        count = 0
        for c in command.keys():
            if c in str(text):
                count += 1

        if message["chat"]["type"] != "private":  # 监测群链接广告
            req = db.user_select(chat_id, user_id)
            if req != False:
                req = list(req)
                if req[3] < 3:
                    req[3] += 1
                    db.user_update(chat_id=chat_id, user_id=user_id,
                                message_times=req[3], spam_times=req[4])
                    text_demoji = filter_emoji(text.strip())
                    result = DFA.filter(text_demoji, repl)
                    if (repl in result and len(text) > 9) or (len(text) > 200):
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
                            chat_id=req[1], user_id=req[2], until_date=35)
                        bot.deleteMessage(
                            chat_id=req[1], message_id=message_id)
                        log_status, reply_markup = handle_logging(bot,
                            content=text, log_group_id=log_group_id,
                            user_id=user_id, chat_id=chat_id,
                            message_id=message_id,
                            reason="消息违规", handle="驱逐出境")
                        msg = "<b><a href='tg://user?id=" + \
                            str(user_id) + "'>" + str(user_id) + \
                            "</a></b> 的消息<b> 违规</b>，已驱逐出境。"
                        status = bot.sendChatAction(chat_id, "typing")
                        status = bot.sendMessage(
                            chat_id=chat_id, text=msg, parse_mode="HTML",
                            reply_markup=reply_markup)
                        #bot.message_deletor(30, status["chat"]["id"], status["message_id"])
                        db.user_delete(chat_id, user_id)
                else:
                    db.user_delete(chat_id, user_id)

        if count > 0 or text[1:len(prefix)+1] == prefix:  # 在命令列表则删除用户指令
            bot.message_deletor(gap, chat_id, message_id)

        if message["chat"]["type"] != "private":
            admins = administrators(bot=bot, chat_id=chat_id)
            if str(root_id) not in admins:
                admins.append(str(root_id))  # root permission

        # 判断是否为私人对话
        if message["chat"]["type"] == "private" and text[1:len(prefix)+1] == prefix:
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(
                chat_id, "抱歉，该指令不支持私人会话!", parse_mode="text",
                reply_to_message_id=message_id, allow_sending_without_reply=True)
            bot.message_deletor(gap, chat_id, status["message_id"])
        elif text[1:len(prefix)+1] == prefix and count == 0:  # 菜单
            status = bot.sendChatAction(chat_id, "typing")
            msg = "<b>Guard 插件功能</b>\n\n" + \
                "<b>/guardadd</b> - 新增过滤关键词，一次只能添加一个。格式：命令后接关键词，以空格作为分隔符\n" + \
                "<b>/guardinit</b> - 设置日志存放频道，格式：/guardinit @ channel_username\n" +\
                "\n"
            status = bot.sendMessage(
                chat_id=chat_id, text=msg, parse_mode="HTML",
                reply_to_message_id=message["message_id"], allow_sending_without_reply=True)

            bot.message_deletor(30, chat_id, status["message_id"])
        elif count > 0:
            if text[1:len(prefix + command["/guardadd"])+1] == prefix + command["/guardadd"]:
                if len(text.split(' ')) == 2:
                    keyword = (text.split(' ')[1]).strip()
                    keyword_demoji = filter_emoji(keyword)
                    # if str(user_id) in admins and len(keyword) <= 7:
                    if str(user_id) == str(root_id) and len(keyword) <= 7:
                        result = DFA.filter(keyword_demoji, repl)
                        if repl not in result:
                            with open(bot.path_converter(plugin_dir + "Guard/keywords"), "a", encoding="utf-8") as k:
                                k.write("\n" + keyword)
                            status = bot.sendChatAction(chat_id, "typing")
                            status = bot.sendMessage(
                                chat_id=chat_id, text="关键词添加成功!", parse_mode="text",
                                reply_to_message_id=message["message_id"], allow_sending_without_reply=True)
                            bot.message_deletor(
                                gap, chat_id, status["message_id"])
                        else:
                            status = bot.sendChatAction(chat_id, "typing")
                            status = bot.sendMessage(
                                chat_id=chat_id, text="关键词已经存在于库中!", parse_mode="text",
                                reply_to_message_id=message["message_id"], allow_sending_without_reply=True)
                            bot.message_deletor(
                                gap, chat_id, status["message_id"])
                    elif len(keyword) > 7:
                        status = bot.sendChatAction(chat_id, "typing")
                        status = bot.sendMessage(
                            chat_id=chat_id, text="输入的关键词过长!", parse_mode="text",
                            reply_to_message_id=message["message_id"], allow_sending_without_reply=True)
                        bot.message_deletor(gap, chat_id, status["message_id"])
                    else:
                        status = bot.sendChatAction(chat_id, "typing")
                        status = bot.sendMessage(
                            chat_id=chat_id, text="您无权操作!", parse_mode="text",
                            reply_to_message_id=message["message_id"], allow_sending_without_reply=True)
                        bot.message_deletor(gap, chat_id, status["message_id"])
                else:
                    status = bot.sendChatAction(chat_id, "typing")
                    status = bot.sendMessage(chat_id=chat_id, text="操作失败，请检查命令格式!",
                                            parse_mode="text", reply_to_message_id=message["message_id"],
                                            allow_sending_without_reply=True)
                    bot.message_deletor(gap, chat_id, status["message_id"])


def timer_func(bot, plugin_dir, gap, chat_id, user_id, first_name, last_name, message_id, log_group_id):
    db = SqliteDB(bot, plugin_dir)
    result = db.select(chat_id=chat_id, user_id=user_id)
    if result != False and result[2] == str(user_id) != "private":
        if int(time.time()) > result[5] + gap:
            status = bot.deleteMessage(chat_id=chat_id, message_id=result[3])
            db.delete(chat_id=chat_id, user_id=user_id)
            status = bot.banChatMember(
                chat_id=chat_id, user_id=user_id, until_date=35)
            #status = bot.unbanChatMember(chat_id=chat_id, user_id=user_id)
            msg = "<b><a href='tg://user?id=" + \
                str(user_id) + "'>" + first_name + " " + \
                last_name + "</a></b> 没能通过人机检测。"
            status = bot.sendMessage(
                chat_id=chat_id, text=msg, parse_mode="HTML")

            bot.message_deletor(30, status["chat"]["id"], status["message_id"])

            log_status, reply_markup = handle_logging(bot,
                content=None, log_group_id=log_group_id,
                user_id=user_id, chat_id=chat_id,
                message_id=message_id,
                reason="人机检测", handle="拒绝入境")


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
    status = bot.getChat(log_group_id)
    log_chat_username = status["username"]

    status = bot.getChat(chat_id)
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

    def __del__(self):
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


class DFAFilter():

    '''Filter Messages from keywords

    Use DFA to keep algorithm perform constantly

    >>> f = DFAFilter()
    >>> f.add("sexy")
    >>> f.filter("hello sexy baby")
    hello **** baby
    '''

    def __init__(self):
        self.keyword_chains = {}
        self.delimit = '\x00'

    def add(self, keyword):
        if not isinstance(keyword, str):
            keyword = keyword.decode('utf-8')
        keyword = keyword.lower()
        chars = keyword.strip()
        if not chars:
            return
        level = self.keyword_chains
        for i in range(len(chars)):
            if chars[i] in level:
                level = level[chars[i]]
            else:
                if not isinstance(level, dict):
                    break
                for j in range(i, len(chars)):
                    level[chars[j]] = {}
                    last_level, last_char = level, chars[j]
                    level = level[chars[j]]
                last_level[last_char] = {self.delimit: 0}
                break
        if i == len(chars) - 1:
            level[self.delimit] = 0

    def parse(self, path):
        with open(path, encoding='UTF-8') as f:
            for keyword in f:
                self.add(keyword.strip())

    def filter(self, message, repl="*"):
        if not isinstance(message, str):
            message = message.decode('utf-8')
        message = message.lower()
        ret = []
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            for char in message[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        ret.append(repl * step_ins)
                        start += step_ins - 1
                        break
                else:
                    ret.append(message[start])
                    break
            else:
                ret.append(message[start])
            start += 1

        return ''.join(ret)


if __name__ == "__main__":
    gl = DFAFilter()
    gl.parse("keywords")
    import time
    t = time.time()
    print(gl.filter("免费出售", "*"))
    print(time.time() - t)
