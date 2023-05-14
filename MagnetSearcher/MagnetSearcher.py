# -*- coding:utf-8 -*-
# @creation: 2023-05-05
# @modification: 2023-05-12
import time
from random import choice

import requests

def MagnetSearcher(bot, message):

    proxies = bot.proxies
    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    message_type = message["message_type"]
    chat_type = message["chat"]["type"]

    prefix = ""
    ok, metadata = bot.metadata.read()
    if ok:
        prefix = metadata.get("Command", "")

    if message_type not in ["text", "callback_query_data"] or \
        chat_type == "channel": return
    
    if message_type == "callback_query_data":
        callback_query_id = message.get("callback_query_id", None)
        callback_query_data = message.get("callback_query_data", None)
        
        engine = callback_query_data.split("+")[1]
        query_words = callback_query_data.split("+")[2]
        
        if "hidealldata" in callback_query_data:
            search_and_show(
                mode="edit",
                bot=bot,
                chat_id=chat_id,
                message_id=message_id,
                callback_data= f"{prefix}showalldata",
                callback_text="展开",
                query_words=query_words,
                engine=engine,
                page_size=2,
                proxies=proxies
            )
        elif "showalldata" in callback_query_data:
            search_and_show(
                mode="edit",
                bot=bot,
                chat_id=chat_id,
                message_id=message_id,
                callback_data= f"{prefix}hidealldata",
                callback_text="折叠",
                query_words=query_words,
                engine=engine,
                page_size=20,
                proxies=proxies
            )
        bot.answerCallbackQuery(callback_query_id=callback_query_id)

    else:
        text = message.get("text", "")
        query_words = ""
        if len(text.split(" ", 1)) == 2:
            query_words = text.split(" ", 1)[1]
        if len(query_words) > 30:
            query_words = query_words[:30]

        if query_words == None or query_words == "":
            bot.sendChatAction(chat_id=chat_id, action="typing")
            status = bot.sendMessage(
                chat_id=chat_id,
                text=f"Parameter empty. (e.g. <code>{prefix} keywords</code>)",
                parse_mode="HTML",
                reply_to_message_id=message_id
            )
            bot.message_deletor(15, status["chat"]["id"], status["message_id"])
            return

        search_and_show(
            mode="send",
            bot=bot,
            chat_id=chat_id,
            message_id=message_id,
            callback_data= f"{prefix}showalldata",
            callback_text="展开",
            query_words=query_words,
            proxies=proxies
        )



def search_and_show(mode, bot, chat_id, message_id, callback_data, callback_text,
                    query_words, engine=None, page=1, page_size=2, proxies={}):

    data = jucili_search(query_words=query_words, engine=engine, 
                        page=page, proxies=proxies)
    if data.get("code", 300) == 200:
        engine = data.get("engine", "")
        if "+" not in callback_data:
            callback_data += f"+{engine}"

        ntime = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) 
        msg = f"<code>[{engine}] {ntime}</code>\n\n"

        data_list = data.get("data", []) or []
        if mode == "send" or "showalldata" in callback_data:
            data_list = data_list[len(data_list)-page_size:]
        if len(data_list) == 0:
            msg += "No Results.\n\n"
        else:
            p = 0
            count = len(data_list)
            for d in list(data_list):
                if p >= page_size:
                    break
                if len(d["title"]) > 100:
                    d["title"] = d["title"][:100] + "..."
                item = f'[{count}] Time: <code>{d["time"]}</code> Size: <code>{d["size"]}</code>\n'
                item += f'Title: <code>{d["title"]}</code>\n'
                item += f'Magnet: <code>{d["magnet"]}</code>\n'
                msg += item + "\n"

                p += 1
                count -= 1

        msg += f"☝️Search results for '{query_words}':"
        inlineKeyboard = [
            [
                {"text": callback_text, "callback_data": f"{callback_data}+{query_words}"},
            ]
        ]
        reply_markup = {
            "inline_keyboard": inlineKeyboard
        }
        if mode == "send":
            bot.sendChatAction(chat_id=chat_id, action="typing")
            status = bot.sendMessage(
                chat_id=chat_id,
                text=msg,
                parse_mode="HTML",
                reply_to_message_id=message_id,
                reply_markup=reply_markup
            )
            bot.message_deletor(180, status["chat"]["id"], status["message_id"])
        elif mode == "edit":  
            bot.editMessageText(
                chat_id=chat_id,
                text=msg,
                parse_mode="HTML",
                message_id=message_id,
                reply_markup=reply_markup
            )
    else:
        if mode == "send":
            bot.sendChatAction(chat_id=chat_id, action="typing")
            status = bot.sendMessage(
                chat_id=chat_id,
                text=f"Failed, please retry.",
                parse_mode="HTML",
                reply_to_message_id=message_id
            )
            bot.message_deletor(15, status["chat"]["id"], status["message_id"])
        elif mode == "edit":
            pass

def jucili_search(query_words, engine=None, page=1, proxies={}) -> dict:
    url = "https://api.jucili.com/api.php"
    engines = [
        "cilimao",
        "cilig",
        "52bt",
        "91bt",
        "1024bt",
        "2048bt",
        "cilisou",
        "xccl",
        "cilibao"
    ]

    if engine is None:
        engine = choice(engines)

    params = {
        "s": engine,
        "q": query_words,
        "p": page
    }
    try:
        with requests.get(
            url=url, params=params,
            timeout=10, verify=False,
            proxies=proxies
        ) as req:
            if req.status_code == requests.codes.ok:
                try:
                    data = req.json()
                except:
                    return {"code": 300}

                if "code" in list(data.keys()):
                    data["code"] = int(data["code"])
                if len(data.get("data", [])) == 0:
                    data["code"] = 200
                if int(data.get("code", 300)) == 200:
                    data["engine"] = engine
                    if "msg" in list(data.keys()):
                        del data["msg"]
                    
                    return data
                else:
                    return {"code": int(data.get("code", 300))}
            else:
                return {"code": int(req.status_code)}
                
    except Exception as e:
        print("Error:", e)
        return {"code": 300}


