# -*- coding:utf-8 -*-
'''
creation time: 2020-11-27
last_modify: 2023-05-12
'''
import time

def VoteToMute(bot, message):

    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    message_id = message["message_id"]

    message_type = message["message_type"]
    chat_type = message["chat"]["type"]

    prefix = "/vote"

    vote_time = 1 * 3 * 60
    mute_time = 1 * 60 * 60

    if message_type == "text":
        text = message["text"]

    if chat_type != "private":
        results = bot.getChatAdministrators(chat_id=chat_id) #判断Bot是否具备管理员权限
        admin_status = False
        for admin_user in results:
            if str(admin_user["user"]["id"]) == str(bot.bot_id):
                admin_status = True
        if admin_status != True:
            status = bot.sendChatAction(chat_id=chat_id, action="typing")
            msg = "权限不足，请授予适当权限以使用 VoteToMute 插件。"
            status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML")
            bot.message_deletor(15, chat_id, status["message_id"])
            return False

    if chat_type == "private" and text[:len(prefix)+1] == prefix: #判断是否为私人对话
        status = bot.sendChatAction(chat_id=chat_id, action="typing")
        status = bot.sendMessage(chat_id=chat_id, text="抱歉，该指令不支持私人会话.", parse_mode="HTML", reply_to_message_id=message_id)
        bot.message_deletor(15, chat_id, status["message_id"])
    elif "reply_markup" in message.keys():
        status = bot.editMessageText(chat_id=chat_id, message_id=message_id,
        text=message["text"] + "\n\n<b>已重新发起投票</b>", parse_mode="HTML")
        status = bot.answerCallbackQuery(callback_query_id=message["callback_query_id"])
        bot.message_deletor(15, chat_id, message_id)

        click_user_id = message["click_user"]["id"]
        callback_query_data = message["callback_query_data"]
        data = callback_query_data.split("?")[1]
        target_user_id = data.split("-")[0]
        target_message_id = data.split("-")[1]
        vote_message_id = data.split("-")[2]

        admins = administrators(bot, chat_id)
        if str(target_user_id) == str(bot.bot_id):
            status = bot.sendChatAction(chat_id=chat_id, action="typing")
            status = bot.sendMessage(chat_id=chat_id,
                text="无权处置本bot.",
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, chat_id, status["message_id"])
            return
        if str(target_user_id) in admins:
            status = bot.sendChatAction(chat_id=chat_id, action="typing")
            status = bot.sendMessage(chat_id=chat_id,
                text="无权处置管理员.",
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, chat_id, status["message_id"])
            return

        options = [
            "违规消息: 被举报者将被禁言，时间1小时",
            "驳回举报: 举报发起者将被禁言，时间1小时"
        ]
        question = "此消息已被举报，请在3分钟内投票表决"
        status = bot.sendChatAction(chat_id=chat_id, action="typing")
        status = bot.sendPoll(chat_id=chat_id,
            is_anonymous=False, question=question, options=options,
            reply_to_message_id=target_message_id)
        if status:
            poll_message_id = status["message_id"]
            poll_id = status["poll"]["id"]

            bot.timer(vote_time, handler_func, args=(bot, prefix, chat_id,
                vote_message_id,target_message_id, poll_message_id,
                poll_id, click_user_id, target_user_id, admins, mute_time))


    elif "reply_to_message" in message.keys():
        reply_to_message = message["reply_to_message"]
        target_message_id = reply_to_message["message_id"]
        target_user_id = reply_to_message["from"]["id"]
        target_chat_id = reply_to_message["chat"]["id"]

        if str(target_chat_id) != str(chat_id):
            status = bot.sendChatAction(chat_id=chat_id, action="typing")
            status = bot.sendMessage(chat_id=chat_id,
                text="只能对当前群组的用户和消息进行投票.",
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, chat_id, status["message_id"])
            return
        admins = administrators(bot, chat_id)
        if str(target_user_id) == str(bot.bot_id):
            status = bot.sendChatAction(chat_id=chat_id, action="typing")
            status = bot.sendMessage(chat_id=chat_id,
                text="无权处置本bot.",
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, chat_id, status["message_id"])
            return
        if str(target_user_id) in admins:
            status = bot.sendChatAction(chat_id=chat_id, action="typing")
            status = bot.sendMessage(chat_id=chat_id,
                text="无权处置管理员.",
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, chat_id, status["message_id"])
            return

        statu = bot.forwardMessage(chat_id=chat_id, from_chat_id=chat_id, message_id=message_id)
        vote_message_id = statu["message_id"]
        statu = bot.forwardMessage(chat_id=chat_id, from_chat_id=chat_id, message_id=target_message_id)
        forward_message_id = statu["message_id"]

        bot.deleteMessage(chat_id=chat_id, message_id=target_message_id)
        bot.deleteMessage(chat_id=chat_id, message_id=message_id)

        message_id = vote_message_id
        target_message_id = forward_message_id

        options = [
            "违规消息: 被举报者将被禁言，时间1小时",
            "驳回举报: 举报发起者将被禁言，时间1小时"
        ]
        question = "此消息已被举报，请在3分钟内投票表决"
        status = bot.sendChatAction(chat_id=chat_id, action="typing")
        status = bot.sendPoll(chat_id=chat_id,
            is_anonymous=False, question=question, options=options,
            reply_to_message_id=target_message_id)
        if status:
            poll_message_id = status["message_id"]
            poll_id = status["poll"]["id"]

            bot.timer(vote_time, handler_func, args=(bot, prefix, chat_id,
                message_id,target_message_id, poll_message_id,
                poll_id, user_id, target_user_id, admins, mute_time))
    else:
        status = bot.sendChatAction(chat_id=chat_id, action="typing")
        status = bot.sendMessage(chat_id=chat_id, text="未指定要举报的对象.",
            parse_mode="HTML", reply_to_message_id=message_id)
        bot.message_deletor(15, chat_id, status["message_id"])



def handler_func(bot, prefix, chat_id, message_id,
    target_message_id, poll_message_id, poll_id, user_id, target_user_id, admins, mute_time):
    status = bot.stopPoll(chat_id=chat_id, message_id=poll_message_id)
    if status:
        total_voter_count = status["total_voter_count"]
        question1 = status.get("options")[0]
        question1_voter_count = question1["voter_count"]
        question2 = status.get("options")[1]
        question2_voter_count = question2["voter_count"]

        if total_voter_count >= 3:
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
            if question1_voter_count > question2_voter_count:
                timestamp = time.time()
                status = bot.restrictChatMember(chat_id=chat_id,
                    user_id=target_user_id,permissions=permissions,
                    until_date=timestamp+mute_time)
                bot.deleteMessage(chat_id=chat_id, message_id=target_message_id)
                bot.deleteMessage(chat_id=chat_id, message_id=poll_message_id)
                msg = "投票结束，涉及消息已被删除\n<b>被举报者</b> <b><a href='tg://user?id=" + str(target_user_id) + "'>" + str(target_user_id) + "</a></b> 已被禁言\n持续时间：<b>1小时</b>"
                status = bot.sendChatAction(chat_id=chat_id, action="typing")
                bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML", reply_to_message_id=message_id)

            elif question1_voter_count < question2_voter_count:
                if str(user_id) not in admins:
                    timestamp = time.time()
                    status = bot.restrictChatMember(chat_id=chat_id,
                        user_id=user_id,permissions=permissions,
                        until_date=timestamp+mute_time)
                    msg = "投票结束\n<b>举报发起者</b> <b><a href='tg://user?id=" + str(user_id) + "'>" + str(user_id) + "</a></b> 已被禁言\n持续时间：<b>1小时</b>"
                else:
                    msg = "投票结束\n<b>举报被驳回</b>\n但无权处置管理员"
                bot.deleteMessage(chat_id=chat_id, message_id=poll_message_id)
                status = bot.sendChatAction(chat_id=chat_id, action="typing")
                bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML", reply_to_message_id=message_id)

            elif question1_voter_count == question2_voter_count:
                inlineKeyboard = [
                    [
                        {"text": "重新发起投票", "callback_data": prefix + "?" + str(target_user_id) + "-" + str(target_message_id) + "-" + str(message_id)},
                    ]
                ]
                reply_markup = {
                    "inline_keyboard": inlineKeyboard
                }
                bot.deleteMessage(chat_id=chat_id, message_id=poll_message_id)
                msg = "投票结束\n由于结果五五开，<b>此次投票无效</b>\n请重新投票"
                status = bot.sendChatAction(chat_id=chat_id, action="typing")
                bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML",
                    reply_to_message_id=target_message_id, reply_markup=reply_markup)

        else:
            inlineKeyboard = [
                [
                    {"text": "重新发起投票", "callback_data": prefix + "?" + str(target_user_id) + "-" + str(target_message_id) + "-" + str(message_id)},
                ]
            ]
            reply_markup = {
                "inline_keyboard": inlineKeyboard
            }
            bot.deleteMessage(chat_id=chat_id, message_id=poll_message_id)
            msg = "投票结束\n由于投票人数不足 <b>3</b> 人，<b>此次投票无效</b>\n请重新投票"
            status = bot.sendChatAction(chat_id=chat_id, action="typing")
            bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML",
                reply_to_message_id=target_message_id, reply_markup=reply_markup)


def administrators(bot, chat_id):
    admins = []
    results = bot.getChatAdministrators(chat_id=chat_id)
    if results != False:
        for result in results:
            if str(result["user"]["is_bot"]) == "False":
                admins.append(str(result["user"]["id"]))
    else:
        admins = False

    if str(bot.bot_id) not in admins:
        admins.append(str(bot.bot_id))
    if str(bot.root_id) not in admins:
        admins.append(str(bot.root_id))

    return admins