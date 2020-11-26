# -*- coding:utf-8 -*-
'''
creation time: 2020-11-27
last_modify: 2020-11-27
'''

def VoteToMute(bot, message):

    # root_id = bot.root_id
    # bot_id = bot.bot_id
    # author = bot.author
    # version = bot.version
    # plugin_dir = bot.plugin_dir
    # plugin_bridge = bot.plugin_bridge
    # uptime = bot.uptime
    # response_times = bot.response_times
    # response_chats = bot.response_chats
    # response_users = bot.response_users

    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    message_id = message["message_id"]

    message_type = message["message_type"]
    chat_type = message["chat"]["type"]

    prefix = "/vote"

    if message_type == "text":
        text = message["text"]

    if message["chat"]["type"] == "private" and text[:len(prefix)+1] == prefix: #判断是否为私人对话
        status = bot.sendChatAction(chat_id, "typing")
        status = bot.sendMessage(chat_id, "抱歉，该指令不支持私人会话!", parse_mode="HTML", reply_to_message_id=message_id)
        bot.message_deletor(15, chat_id, status["message_id"])
    elif "reply_to_message" in message.keys():
        reply_to_message = message["reply_to_message"]
        target_message_id = reply_to_message["message_id"]
        target_user_id = reply_to_message["from"]["id"]
        target_chat_id = reply_to_message["chat"]["id"]

        if str(target_chat_id) != str(chat_id):
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id=chat_id,
                text="只能对当前群组的用户和消息进行投票.",
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, chat_id, status["message_id"])
            return
        admins = administrators(bot, chat_id)
        if str(target_user_id) == str(bot.bot_id):
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id=chat_id,
                text="无权处置本bot.",
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, chat_id, status["message_id"])
            return
        if str(target_user_id) in admins:
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id=chat_id,
                text="无权处置管理员.",
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, chat_id, status["message_id"])
            return

        options = [
            "违规消息: 将根据投票结果禁言被举报者，时间1小时。",
            "驳回举报: 若举报被驳回，举报者将被禁言1小时。"
        ]
        question = "此消息已被举报，请在3分钟内投票表决."
        status = bot.sendChatAction(chat_id, "typing")
        status = bot.sendPoll(chat_id=chat_id,
            is_anonymous=False, question=question, options=options,
            reply_to_message_id=target_message_id)
        if status:
            poll_message_id = status["message_id"]
            poll_id = status["poll"]["id"]

            bot.timer(1 * 3 * 60, handler_func, args=(bot, chat_id,
                message_id,target_message_id, poll_message_id,
                poll_id, user_id, target_user_id))
    else:
        status = bot.sendChatAction(chat_id, "typing")
        status = bot.sendMessage(chat_id=chat_id, text="未指定要举报的对象!",
            parse_mode="HTML", reply_to_message_id=message_id)
        bot.message_deletor(15, chat_id, status["message_id"])



def handler_func(bot, chat_id, message_id,
    target_message_id, poll_message_id, poll_id, user_id, target_user_id):
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
                status = bot.restrictChatMember(chat_id=chat_id,
                    user_id=target_user_id,permissions=permissions,
                    until_date=1 * 60 * 60)
                bot.deleteMessage(chat_id=chat_id, message_id=target_message_id)
                bot.deleteMessage(chat_id=chat_id, message_id=poll_message_id)
                msg = "投票结束，涉及消息已被删除\n<b>被举报者</b> <b><a href='tg://user?id=" + str(target_user_id) + "'>" + str(target_user_id) + "</a></b> 已被禁言\n持续时间：<b>1小时</b>"
                status = bot.sendChatAction(chat_id, "typing")
                bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML", reply_to_message_id=message_id)

            elif question1_voter_count < question2_voter_count:
                status = bot.restrictChatMember(chat_id=chat_id,
                    user_id=user_id,permissions=permissions,
                    until_date=1 * 60 * 60)
                bot.deleteMessage(chat_id=chat_id, message_id=poll_message_id)
                msg = "投票结束\n<b>举报者</b> <b><a href='tg://user?id=" + str(user_id) + "'>" + str(user_id) + "</a></b> 已被禁言\n持续时间：<b>1小时</b>"
                status = bot.sendChatAction(chat_id, "typing")
                bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML", reply_to_message_id=message_id)

            elif question1_voter_count == question2_voter_count:
                bot.deleteMessage(chat_id=chat_id, message_id=poll_message_id)
                msg = "投票结束\n由于结果五五开，<b>此次投票无效</b>\n请重新投票"
                status = bot.sendChatAction(chat_id, "typing")
                bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML", reply_to_message_id=message_id)

        else:
            bot.deleteMessage(chat_id=chat_id, message_id=poll_message_id)
            msg = "投票结束\n由于投票人数不足 <b>3</b> 人,<b>此次投票无效</b>\n请重新投票"
            status = bot.sendChatAction(chat_id, "typing")
            bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML", reply_to_message_id=message_id)


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