# -*- coding:utf-8 -*-
'''
creation time: 2020-06-04
last_modify: 2023-05-12
'''
import time

def Admin(bot, message):
    gap = 15
    message_id = message["message_id"]
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    text = message["text"]
    bot_id = bot.bot_id
    root_id = bot.root_id
    prefix = "admin"

    command = { #命令注册
            "/adminkick": "kick",
            "/admindel": "del",
            "/adminpin": "pin",
            "/adminunpin": "unpin",
            "/adminmute": "mute",
            "/adminunmute": "unmute",
            "/adminsudo": "sudo",
            "/adminunsudo": "unsudo",
            "/admintitle": "title"
        }
    count = 0
    for c in command.keys():
        if c in str(text):
            count += 1

    if message["chat"]["type"] != "private":
        admins = administrators(bot=bot, chat_id=chat_id)
        admins.append(bot_id)
        if str(root_id) not in admins:
            admins.append(str(root_id)) #root permission

    if message["chat"]["type"] != "private":
        results = bot.getChatAdministrators(chat_id=chat_id) #判断Bot是否具管理员权限
        admin_status = False
        for admin_user in results:
            if str(admin_user["user"]["id"]) == str(bot_id):
                admin_status = True
        if admin_status != True:
            status = bot.sendChatAction(chat_id=chat_id, action="typing")
            msg = "权限不足，请授予全部权限以使用 Admin 插件。"
            status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML")
            bot.message_deletor(30, chat_id, status["message_id"])
            bot.message_deletor(gap, chat_id, message_id)
            return False


    if message["chat"]["type"] == "private" and text[1:len(prefix)+1] == prefix: #判断是否为私人对话
        status = bot.sendChatAction(chat_id=chat_id, action="typing")
        status = bot.sendMessage(chat_id=chat_id, text="抱歉，该指令不支持私人会话!", parse_mode="HTML", reply_to_message_id=message_id)
        bot.message_deletor(gap, chat_id, status["message_id"])
    elif text[1:len(prefix)+1] == prefix and count == 0: #菜单
        status = bot.sendChatAction(chat_id=chat_id, action="typing")
        msg = "<b>Admin 插件功能</b>\n\n" +\
            "<b>/adminkick</b> - 踢人。格式:以回复要踢用户的消息的形式发送指令\n" +\
            "<b>/admindel</b> - 删除消息。格式:以回复要删除的消息的形式发送指令\n" +\
            "<b>/adminpin</b> - 置顶消息。格式:以回复要置顶的消息的形式发送指令\n" +\
            "<b>/adminunpin</b> - 取消置顶。格式:以回复要取消置顶的消息的形式发送指令\n" +\
            "<b>/adminmute</b> - 禁言用户。格式:以回复要禁言用户的消息的形式发送指令，指令后跟禁言时间(支持的时间：1m,10m,1h,1d,forever)，以空格作为分隔符\n" +\
            "<b>/adminunmute</b> - 解除用户禁言。格式:以回复要解除禁言用户的消息的形式发送指令\n" +\
            "<b>/adminsudo</b> - 任命管理员。格式:以回复将被任命为管理员的用户的消息的形式发送指令\n" +\
            "<b>/adminunsudo</b> - 取消任命管理员。格式:以回复将被解除管理员权限的用户的消息的形式发送指令\n" +\
            "<b>/admintitle</b> - 设置管理员昵称。格式:以回复将被设置昵称的管理员的消息的形式发送指令，指令后跟昵称，以空格作为分隔符\n" +\
            "\n"
        status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML", reply_to_message_id=message["message_id"])

        bot.message_deletor(30, chat_id, status["message_id"])

    elif "reply_to_message" in message.keys():
        reply_to_message = message["reply_to_message"]
        target_message_id = reply_to_message["message_id"]
        target_user_id = reply_to_message["from"]["id"]
        target_chat_id = reply_to_message["chat"]["id"]

        if str(user_id) in admins and str(chat_id) == str(target_chat_id):
            if text[1:len(prefix + command["/adminkick"])+1] == prefix + command["/adminkick"]:
                if str(target_user_id) not in admins:
                    timestamp = time.time()
                    status = bot.banChatMember(chat_id=chat_id, user_id=target_user_id, until_date=timestamp+90)
                    status_ = bot.unbanChatMember(chat_id=chat_id, user_id=target_user_id)
                    if status != False:
                        status = bot.sendChatAction(chat_id=chat_id, action="typing")
                        status = bot.sendMessage(chat_id=chat_id, text="已送该用户出群。", parse_mode="HTML", reply_to_message_id=message["message_id"])
                        bot.message_deletor(gap, chat_id, status["message_id"])
                else:
                    status = bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id, text="抱歉，无权处置该用户!", parse_mode="HTML", reply_to_message_id=message["message_id"])
                    bot.message_deletor(gap, chat_id, status["message_id"])
            elif text[1:len(prefix + command["/admindel"])+1] == prefix + command["/admindel"]:
                status = bot.deleteMessage(chat_id=chat_id, message_id=target_message_id)
                if status == False:
                    status = bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id, text="删除失败!", parse_mode="HTML", reply_to_message_id=message["message_id"])
                    bot.message_deletor(gap, chat_id, status["message_id"])
            elif text[1:len(prefix + command["/adminpin"])+1] == prefix + command["/adminpin"]:
                status = bot.pinChatMessage(chat_id=chat_id, message_id=target_message_id)
                if status == False:
                    status = bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id, text="置顶失败!", parse_mode="HTML", reply_to_message_id=message["message_id"])
                    bot.message_deletor(gap, chat_id, status["message_id"])
            elif text[1:len(prefix + command["/adminunpin"])+1] == prefix + command["/adminunpin"]:
                status = bot.unpinChatMessage(chat_id=chat_id)
                if status == False:
                    status = bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id, text="取消置顶失败!", parse_mode="HTML", reply_to_message_id=message["message_id"])
                    bot.message_deletor(gap, chat_id, status["message_id"])
            elif text[1:len(prefix + command["/adminmute"])+1] == prefix + command["/adminmute"]:
                if str(target_user_id) not in admins:
                    mute_time = {
                        "1m": 1 * 60,
                        "10m": 1 * 60 * 10,
                        "1h": 1 * 60 * 60,
                        "1d": 1 * 60 * 60 * 24,
                        "forever": 0
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
                    if text[1:].split(' ')[1] in mute_time.keys():
                        timestamp = time.time()
                        status = bot.restrictChatMember(
                            chat_id=chat_id, user_id=target_user_id,
                            permissions=permissions,
                            until_date=timestamp+mute_time[text[1:].split(' ')[1]])
                        if status != False:
                            time_ = text[1:].split(' ')[1]
                            time_ = time_.replace("1m", "1分钟").replace("10m", "10分钟")
                            time_ = time_.replace("1h", "1小时").replace("1d", "1天").replace("forever", "永久")
                            status = bot.sendChatAction(chat_id=chat_id, action="typing")
                            msg = "<b><a href='tg://user?id=" + str(target_user_id) + "'>" + str(target_user_id) + "</a></b> 已被禁言，持续时间：<b>" + str(time_) + "</b>。"
                            status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML", reply_to_message_id=message["message_id"])
                            bot.message_deletor(gap, chat_id, status["message_id"])
                        else:
                            status = bot.sendChatAction(chat_id=chat_id, action="typing")
                            msg = "<b><a href='tg://user?id=" + str(target_user_id) + "'>" + str(target_user_id) + "</a></b> 禁言失败!"
                            status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML", reply_to_message_id=message["message_id"])
                            bot.message_deletor(gap, chat_id, status["message_id"])
                    else:
                        status = bot.sendChatAction(chat_id=chat_id, action="typing")
                        status = bot.sendMessage(chat_id=chat_id, text="无效指令，请检查格式!", parse_mode="HTML", reply_to_message_id=message["message_id"])
                        bot.message_deletor(gap, chat_id, status["message_id"])
                else:
                    status = bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id, text="抱歉，无权处置该用户!", parse_mode="HTML", reply_to_message_id=message["message_id"])
                    bot.message_deletor(gap, chat_id, status["message_id"])
            elif text[1:len(prefix + command["/adminunmute"])+1] == prefix + command["/adminunmute"]:
                if str(target_user_id) not in admins or str(target_user_id) == str(root_id):
                    status = bot.getChat(chat_id=chat_id)
                    permissions = status.get("permissions")
                    status = bot.restrictChatMember(chat_id=chat_id, user_id=target_user_id,permissions=permissions)
                    if status != False:
                        status = bot.sendChatAction(chat_id=chat_id, action="typing")
                        msg = "<b><a href='tg://user?id=" + str(target_user_id) + "'>" + str(target_user_id) + "</a></b> 已被解禁。"
                        status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML", reply_to_message_id=message["message_id"])
                        bot.message_deletor(gap, chat_id, status["message_id"])
                else:
                    status = bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id, text="抱歉，无权处置该用户!", parse_mode="HTML", reply_to_message_id=message["message_id"])
                    bot.message_deletor(gap, chat_id, status["message_id"])

            elif text[1:len(prefix + command["/adminsudo"])+1] == prefix + command["/adminsudo"]:
                if str(user_id) != root_id:
                    status = bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id, text="🤖 抱歉，您无权操作.",
                        parse_mode="HTML", reply_to_message_id=message["message_id"])
                    bot.message_deletor(gap, chat_id, status["message_id"])
                    bot.message_deletor(gap, chat_id, message_id)
                    return

                target_user_info = bot.getChatMember(chat_id=chat_id, user_id=target_user_id)
                if target_user_info["status"] == "creator":
                    status = bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id, text="🤖 无权处置创建者.",
                        parse_mode="HTML", reply_to_message_id=message["message_id"])
                    bot.message_deletor(gap, chat_id, status["message_id"])
                    bot.message_deletor(gap, chat_id, message_id)
                    return
                if str(target_user_id) == bot_id:
                    status = bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id, text="🤖 无权处置.",
                        parse_mode="HTML", reply_to_message_id=message["message_id"])
                    bot.message_deletor(gap, chat_id, status["message_id"])
                    bot.message_deletor(gap, chat_id, message_id)
                    return
                if target_user_info["status"] == "administrator":
                    status = bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id, text="🤖 该用户已经是管理员了.",
                        parse_mode="HTML", reply_to_message_id=message["message_id"])
                    bot.message_deletor(gap, chat_id, status["message_id"])
                    bot.message_deletor(gap, chat_id, message_id)
                    return

                bot_info = bot.getChatMember(chat_id=chat_id, user_id=bot_id)
                if bot_info["status"] == "administrator":
                    bot_info.pop("user")
                    bot_info.pop("status")
                    bot_permissions = bot_info
                    if bot_permissions.get("can_promote_members", False) and \
                        bot_permissions.get("can_restrict_members", False) and \
                        bot_permissions.get("can_delete_messages", False) and \
                        bot_permissions.get("can_pin_messages", False) and \
                        bot_permissions.get("can_invite_users", False) and \
                        bot_permissions.get("can_manage_voice_chats", False):
                        if str(target_user_id) == root_id:
                            ok = bot.promoteChatMember(
                                chat_id = chat_id,
                                user_id = root_id,
                                is_anonymous = False,
                                can_manage_chat = bot_permissions.get("can_manage_chat", False),
                                can_change_info = bot_permissions.get("can_change_info", False),
                                can_post_messages = bot_permissions.get("can_post_messages", False),
                                can_edit_messages = bot_permissions.get("can_edit_messages", False),
                                can_delete_messages = bot_permissions.get("can_delete_messages", False),
                                can_manage_voice_chats = bot_permissions.get("can_manage_voice_chats", False),
                                can_invite_users = bot_permissions.get("can_invite_users", False),
                                can_restrict_members = bot_permissions.get("can_restrict_members", False),
                                can_pin_messages = bot_permissions.get("can_pin_messages", False),
                                can_promote_members = bot_permissions.get("can_promote_members", False)
                            )
                        else:
                            ok = bot.promoteChatMember(
                                chat_id = chat_id,
                                user_id = target_user_id,
                                is_anonymous = False,
                                can_change_info = False,
                                can_post_messages = False,
                                can_edit_messages = False,
                                can_delete_messages = True,
                                can_manage_voice_chats = True,
                                can_invite_users = False,
                                can_restrict_members = True,
                                can_pin_messages = True,
                                can_promote_members = False
                            )

                        if ok:
                            status = bot.sendChatAction(chat_id=chat_id, action="typing")
                            status = bot.sendMessage(chat_id=chat_id, text="🤖 提权成功.",
                                parse_mode="HTML", reply_to_message_id=message["message_id"])
                            bot.message_deletor(gap, chat_id, status["message_id"])
                            title = bot.getMe().get("first_name", "小埋")
                            title += "的手下"
                            ok = bot.setChatAdministratorCustomTitle(chat_id=chat_id,
                                user_id=target_user_id, custom_title=title)
                            if ok:
                                status = bot.sendChatAction(chat_id=chat_id, action="typing")
                                status = bot.sendMessage(chat_id=chat_id, text="🤖 昵称设置成功.",
                                    parse_mode="HTML", reply_to_message_id=message["message_id"])
                                bot.message_deletor(gap, chat_id, status["message_id"])
                            else:
                                status = bot.sendChatAction(chat_id=chat_id, action="typing")
                                status = bot.sendMessage(chat_id=chat_id, text="🤖 昵称设置失败.",
                                    parse_mode="HTML", reply_to_message_id=message["message_id"])
                                bot.message_deletor(gap, chat_id, status["message_id"])
                        else:
                            status = bot.sendChatAction(chat_id=chat_id, action="typing")
                            status = bot.sendMessage(chat_id=chat_id, text="🤖 提权失败.",
                                parse_mode="HTML", reply_to_message_id=message["message_id"])
                            bot.message_deletor(gap, chat_id, status["message_id"])
                    else:
                        status = bot.sendChatAction(chat_id=chat_id, action="typing")
                        status = bot.sendMessage(chat_id=chat_id, text="🤖 bot不具备恰当的权限.",
                            parse_mode="HTML", reply_to_message_id=message["message_id"])
                        bot.message_deletor(gap, chat_id, status["message_id"])
                else:
                    status = bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id, text="🤖 bot不具备管理员身份.",
                        parse_mode="HTML", reply_to_message_id=message["message_id"])
                    bot.message_deletor(gap, chat_id, status["message_id"])

            elif text[1:len(prefix + command["/adminunsudo"])+1] == prefix + command["/adminunsudo"]:
                if str(user_id) != root_id:
                    status = bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id, text="🤖 抱歉，您无权操作.",
                        parse_mode="HTML", reply_to_message_id=message["message_id"])
                    bot.message_deletor(gap, chat_id, status["message_id"])
                    bot.message_deletor(gap, chat_id, message_id)
                    return

                target_user_info = bot.getChatMember(chat_id=chat_id, user_id=target_user_id)
                if target_user_info["status"] == "creator":
                    status = bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id, text="🤖 无权处置创建者.",
                        parse_mode="HTML", reply_to_message_id=message["message_id"])
                    bot.message_deletor(gap, chat_id, status["message_id"])
                    bot.message_deletor(gap, chat_id, message_id)
                    return
                if str(target_user_id) == bot_id:
                    status = bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id, text="🤖 无权处置.",
                        parse_mode="HTML", reply_to_message_id=message["message_id"])
                    bot.message_deletor(gap, chat_id, status["message_id"])
                    bot.message_deletor(gap, chat_id, message_id)
                    return

                bot_info = bot.getChatMember(chat_id=chat_id, user_id=bot_id)
                if bot_info["status"] == "administrator":
                    ok = bot.promoteChatMember(
                    chat_id = chat_id,
                    user_id = target_user_id,
                    is_anonymous = False,
                    can_manage_chat = False,
                    can_change_info = False,
                    can_post_messages = False,
                    can_edit_messages = False,
                    can_delete_messages = False,
                    can_manage_voice_chats = False,
                    can_invite_users = False,
                    can_restrict_members = False,
                    can_pin_messages = False,
                    can_promote_members = False
                    )
                    if ok:
                        status = bot.sendChatAction(chat_id=chat_id, action="typing")
                        status = bot.sendMessage(chat_id=chat_id, text="🤖 除权成功.",
                            parse_mode="HTML", reply_to_message_id=message["message_id"])
                        bot.message_deletor(gap, chat_id, status["message_id"])
                    else:
                        status = bot.sendChatAction(chat_id=chat_id, action="typing")
                        status = bot.sendMessage(chat_id=chat_id, text="🤖 除权失败.",
                            parse_mode="HTML", reply_to_message_id=message["message_id"])
                        bot.message_deletor(gap, chat_id, status["message_id"])
                else:
                    status = bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id, text="🤖 bot不具备管理员身份.",
                        parse_mode="HTML", reply_to_message_id=message["message_id"])
                    bot.message_deletor(gap, chat_id, status["message_id"])

            elif text[1:len(prefix + command["/admintitle"])+1] == prefix + command["/admintitle"]:
                if str(user_id) != root_id:
                    status = bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id, text="🤖 抱歉，您无权操作.",
                        parse_mode="HTML", reply_to_message_id=message["message_id"])
                    bot.message_deletor(gap, chat_id, status["message_id"])
                    bot.message_deletor(gap, chat_id, message_id)
                    return
                if len(text.split(" ")) < 2:
                    status = bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id, text="🤖 指令格式错误，请检查. \n(<b>e.g. /admintitle title</b>)",
                        parse_mode="HTML", reply_to_message_id=message["message_id"])
                    bot.message_deletor(gap, chat_id, status["message_id"])
                    bot.message_deletor(gap, chat_id, message_id)
                    return

                target_user_info = bot.getChatMember(chat_id=chat_id, user_id=target_user_id)
                if target_user_info["status"] == "creator":
                    status = bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id, text="🤖 无权处置创建者.",
                        parse_mode="HTML", reply_to_message_id=message["message_id"])
                    bot.message_deletor(gap, chat_id, status["message_id"])
                    bot.message_deletor(gap, chat_id, message_id)
                    return
                if str(target_user_id) == bot_id:
                    status = bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id, text="🤖 无权处置.",
                        parse_mode="HTML", reply_to_message_id=message["message_id"])
                    bot.message_deletor(gap, chat_id, status["message_id"])
                    bot.message_deletor(gap, chat_id, message_id)
                    return
                # if target_user_info["status"] != "administrator":
                #     status = bot.sendChatAction(chat_id=chat_id, action="typing")
                #     status = bot.sendMessage(chat_id=chat_id, text="🤖 不能为非管理用户设置昵称.",
                #         parse_mode="HTML", reply_to_message_id=message["message_id"])
                #     bot.message_deletor(gap, chat_id, status["message_id"])
                #     bot.message_deletor(gap, chat_id, message_id)
                #     return

                bot_info = bot.getChatMember(chat_id=chat_id, user_id=bot_id)
                if bot_info["status"] == "administrator":
                    bot_info.pop("user")
                    bot_info.pop("status")
                    bot_permissions = bot_info
                    title = text.split(" ", 1)[1]
                    if len(title) > 16:
                        status = bot.sendChatAction(chat_id=chat_id, action="typing")
                        status = bot.sendMessage(chat_id=chat_id, text="🤖 输入的昵称过长.",
                            parse_mode="HTML", reply_to_message_id=message["message_id"])
                        bot.message_deletor(gap, chat_id, status["message_id"])
                        bot.message_deletor(gap, chat_id, message_id)
                        return
                    if target_user_info["status"] != "administrator":
                        if str(target_user_id) == root_id:
                            ok = bot.promoteChatMember(
                                chat_id = chat_id,
                                user_id = root_id,
                                is_anonymous = False,
                                can_manage_chat = bot_permissions.get("can_manage_chat", False),
                                can_change_info = bot_permissions.get("can_change_info", False),
                                can_post_messages = bot_permissions.get("can_post_messages", False),
                                can_edit_messages = bot_permissions.get("can_edit_messages", False),
                                can_delete_messages = bot_permissions.get("can_delete_messages", False),
                                can_manage_voice_chats = bot_permissions.get("can_manage_voice_chats", False),
                                can_invite_users = bot_permissions.get("can_invite_users", False),
                                can_restrict_members = bot_permissions.get("can_restrict_members", False),
                                can_pin_messages = bot_permissions.get("can_pin_messages", False),
                                can_promote_members = bot_permissions.get("can_promote_members", False)
                            )
                        else:
                            ok = bot.promoteChatMember(
                                    chat_id = chat_id,
                                    user_id = target_user_id,
                                    is_anonymous = False,
                                    can_change_info = False,
                                    can_post_messages = False,
                                    can_edit_messages = False,
                                    can_delete_messages = False,
                                    can_manage_voice_chats = True,
                                    can_invite_users = True,
                                    can_restrict_members = False,
                                    can_pin_messages = False,
                                    can_promote_members = False
                                )
                        if not ok:
                            status = bot.sendChatAction(chat_id=chat_id, action="typing")
                            status = bot.sendMessage(chat_id=chat_id, text="🤖 提权失败，无法设置昵称.",
                                parse_mode="HTML", reply_to_message_id=message["message_id"])
                            bot.message_deletor(gap, chat_id, status["message_id"])
                            bot.message_deletor(gap, chat_id, message_id)
                            return
                    status = bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id, text="🤖 提权成功.",
                        parse_mode="HTML", reply_to_message_id=message["message_id"])
                    bot.message_deletor(gap, chat_id, status["message_id"])
                    ok = bot.setChatAdministratorCustomTitle(chat_id=chat_id,
                        user_id=target_user_id, custom_title=title)
                    if ok:
                        status = bot.sendChatAction(chat_id=chat_id, action="typing")
                        status = bot.sendMessage(chat_id=chat_id, text="🤖 昵称设置成功.",
                            parse_mode="HTML", reply_to_message_id=message["message_id"])
                        bot.message_deletor(gap, chat_id, status["message_id"])
                else:
                    status = bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id, text="🤖 bot不具备管理员身份.",
                        parse_mode="HTML", reply_to_message_id=message["message_id"])
                    bot.message_deletor(gap, chat_id, status["message_id"])

        else:
            status = bot.sendChatAction(chat_id=chat_id, action="typing")
            status = bot.sendMessage(chat_id=chat_id, text="抱歉，您无权操作.",
                parse_mode="HTML", reply_to_message_id=message["message_id"])
            bot.message_deletor(gap, chat_id, status["message_id"])
    else:
        status = bot.sendChatAction(chat_id=chat_id, action="typing")
        status = bot.sendMessage(chat_id=chat_id, text="未指定要操作的对象!",
            parse_mode="HTML", reply_to_message_id=message["message_id"])
        bot.message_deletor(gap, chat_id, status["message_id"])

    bot.message_deletor(gap, chat_id, message_id)


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
