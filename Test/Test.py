# -*- coding: utf-8 -*-

def Test(bot, message):

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
    # proxies = bot.proxies

    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    message_id = message["message_id"]

    message_type = message["message_type"]
    chat_type = message["chat"]["type"]

    plugin_info = bot.get_plugin_info()
    command = ""
    if plugin_info.get("status", False):
        command = plugin_info.get("command", "")


    # Write your plugin code below
    plugin_info = bot.get_plugin_info(plugin_name="Hello")
    # print(plugin_info)
    bot.sendMessage(chat_id=chat_id, text=str(plugin_info))

    # print(bot.join_plugin_path("__init__.py"))
    # bot.sendMessage(chat_id=chat_id, text=str(bot.join_plugin_path("__init__.py")))
    req = bot.getChatAdminsUseridList(chat_id=chat_id, skip_bot=False)
    # print(req)
    bot.sendMessage(chat_id=chat_id, text=str(req))