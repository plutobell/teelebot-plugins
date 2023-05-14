# -*- coding:utf-8 -*-
'''
creation time: 2020-11-20
last_modify: 2023-05-12
'''
import requests

def MusicDownload(bot, message):

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

    prefix = "/musicd"

    text = message["text"]

    if text.split(" ")[0][:len(prefix)] == prefix:
        if len(text.split(" ")) == 3:
            app = text.split(" ")[1]
            m_id = text.split(" ")[2]
            if app in ("wy", "qq", "bd"):
                result = get_music(app, m_id)
                if result and result["song_id"] != None:
                    if result["mp3url"] != "":
                        caption = "<b>歌名: " + str(result["name"]) + "</b>\n" +\
                            "<b>歌手: #" + str(result["author"]) + "</b>\n" +\
                            "<b>资源: <a href='" + str(result["mp3url"]) + "'>点击下载</a></b>"
                    else:
                        caption = "<b>歌名: " + str(result["name"]) + "</b>\n" +\
                            "<b>歌手: #" + str(result["author"]) + "</b>\n" +\
                            "<b>资源: 无法下载</b>"
                    status = bot.sendPhoto(chat_id=chat_id, photo=result["cover"],
                        caption=caption, parse_mode="HTML", reply_to_message_id=message_id)
                else:
                    status = bot.sendMessage(chat_id=chat_id,
                        text="获取歌曲信息失败.",
                        parse_mode="HTML", reply_to_message_id=message_id)
                    bot.message_deletor(15, status["chat"]["id"], status["message_id"])
            else:
                status = bot.sendMessage(chat_id=chat_id,
                    text="不支持的App.<b> (wy qq bd)</b>",
                    parse_mode="HTML", reply_to_message_id=message_id)
                bot.message_deletor(15, status["chat"]["id"], status["message_id"])
        else:
            status = bot.sendMessage(chat_id=chat_id,
                text="指令格式错误. <b>(e.g.: " + prefix + " app id)</b>",
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, status["chat"]["id"], status["message_id"])
    else:
        status = bot.sendMessage(chat_id=chat_id,
            text="指令格式错误. <b>(e.g.: " + prefix + " app id)</b>",
            parse_mode="HTML", reply_to_message_id=message_id)
        bot.message_deletor(15, status["chat"]["id"], status["message_id"])


def get_music(app, m_id):
    urls = {
        "wy": "https://api.vvhan.com/api/music?id={}&type=song&media=netease",
        "qq": "https://api.vvhan.com/api/music?id={}&type=song&media=tencent",
        "bd": "https://api.vvhan.com/api/music?id={}&type=song&media=baidu"
    }
    url = urls[app]
    url = url.format(m_id)
    try:
        with requests.get(url=url, verify=False) as req:
            result = req.json()
            if not req.status_code == requests.codes.ok:
                return False
            elif bool(result["success"]) == True:
                return result
            else:
                return False
    except:
        return False