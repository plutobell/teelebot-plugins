# -*- coding:utf-8 -*-
import requests

def Whois(bot, message):
    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    text = message["text"]
    txt_message_id = 0

    prefix = ""
    with open(bot.path_converter(bot.plugin_dir + "Whois/__init__.py"), "r", encoding="utf-8") as init:
        prefix = init.readline()[1:].strip()

    if text[:len(prefix)] == prefix:
        if len(text.split(' ')) == 2:
            domain = str(text.split(' ')[1])
            if len(domain.split('.')) > 1 and len(domain.split('.')) <= 2:
                bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(chat_id=chat_id, text="正在查询，请稍等...", parse_mode="TEXT", reply_to_message_id=message_id)
                txt_message_id = status["message_id"]

                result = whois_info(domain=domain)
                if result != False:
                    msg = result.split("<<<")[0]
                    if ">>>" in msg:
                        msg += "<<<"
                    msg = msg.replace("<pre>", "")
                    msg = msg.replace("</pre>", "")
                    status = bot.editMessageText(chat_id=chat_id, message_id=txt_message_id,
                        text=msg.strip(), parse_mode="TEXT", disable_web_page_preview=True)
                    bot.message_deletor(60, chat_id, txt_message_id)
                else:
                    status = bot.editMessageText(chat_id=chat_id,
                        message_id=txt_message_id, text="查询失败!", parse_mode="TEXT")
                    bot.message_deletor(15, chat_id, txt_message_id)
            else:
                bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(chat_id=chat_id, text="域名格式错误，请检查!",
                    parse_mode="TEXT", reply_to_message_id=message_id)
                bot.message_deletor(15, chat_id, status["message_id"])
        else:
            bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id=chat_id, text="指令格式错误，请检查!",
                parse_mode="TEXT", reply_to_message_id=message_id)
            bot.message_deletor(15, chat_id, status["message_id"])
    else:
        bot.sendChatAction(chat_id, "typing")
        status = bot.sendMessage(chat_id=chat_id, text="指令错误，请检查!",
            parse_mode="TEXT", reply_to_message_id=message_id)
        bot.message_deletor(15, chat_id, status["message_id"])


def whois_info(domain):
    """
    https://api.aa1.cn/doc/whois.html
    接口地址：https://v.api.aa1.cn/api/whois/index.php 
    返回格式：JSON
    请求方式：GET
    请求参数：https://v.api.aa1.cn/api/whois/index.php?domain=
    """
    url = "https://v.api.aa1.cn/api/whois/index.php?domain="+ str(domain)
    try:
        with requests.get(url=url) as req:
            return req.text
    except Exception as e:
        print(e)
        return False
