# -*- coding:utf-8 -*-
# Program: WorkersAIChat
# Description: Cloudflare Workers AI Chat Plugin
# Creation: 2024-05-17
# Last modification: 2024-05-17

import logging
import traceback
import requests

def WorkersAIChat(bot, message):

    message_type = message.get("message_type")
    message_id = message.get("message_id")
    chat_id = message.get("chat").get("id")
    user_id = message.get("from").get("id")
    chat_type = message.get("chat").get("type")

    me = bot.getMe()
    bot_username = me.get("username")
    bot_id = me.get("id")

    if message_type != "text":
        return
    
    text = str(message.get("text"))
    is_mention = False
    is_bot_command = False
    mention_username = ""
    if "entities" in message.keys():
        entities = message.get("entities")
        for e in entities:
            if e["type"] == "mention":
                e_offset = int(e["offset"])
                e_length = int(e["length"])
                mention_username = text[e_offset:e_offset+e_length]
                # print(mention_username, bot_username)
                if mention_username == "@"+bot_username:
                    is_mention = True
            elif e["type"] == "bot_command":
                is_bot_command = True
    
    if is_bot_command:
        return
    if is_mention:
        text = text.replace("@"+bot_username, "", -1)
        if text.strip() == "":
            text += " hi"

    try:
        if chat_type == "private" or \
            (chat_type == "supergroup" and "reply_to_message" in message.keys()) or \
            (chat_type == "supergroup" and is_mention):

            if "entities" in message.keys():
                entities = message.get("entities")
            if "reply_to_message" in message.keys():
                reply_from_id = message.get("reply_to_message").get("from").get("id")
                if str(reply_from_id) != str(bot_id):
                    return

            try:
                user_messages = {}
                ok, buf = bot.buffer.select(idx=0)
                if ok and len(buf) == 1:
                    user_messages = buf[0]["user_messages"]
                else:
                    bot.buffer.insert(data={"user_messages": user_messages})

                ai = WorkersAI(conf_path=bot.join_plugin_path("config.ini"),
                            user_messages=user_messages)
                msg = ai.chat(message=text, uid=chat_id)
                msg = msg.replace("`", "", -1)
                bot.buffer.update(idx=0, data={"user_messages": ai.user_messages})
                bot.sendChatAction(chat_id=chat_id, action="typing")
                bot.sendMessage(chat_id=chat_id,text=msg, reply_to_message_id=message_id)
            except Exception as e:
                print(e)
                traceback.print_exc()
                bot.sendChatAction(chat_id=chat_id, action="typing")
                bot.sendMessage(chat_id=chat_id, text="接口调用失败。", reply_to_message_id=message_id)
                
    except Exception as e:
        print(e)
        traceback.print_exc()
        bot.sendChatAction(chat_id=chat_id, action="typing")
        bot.sendMessage(chat_id=chat_id, text="出错了。", reply_to_message_id=message_id)


class WorkersAI:
    def __init__(self, conf_path, user_messages={}):
        with open(conf_path, "r", encoding="utf-8") as conf:
            lines = conf.readlines()
            if len(lines) >= 4:
                self.__cf_account_id = lines[0].strip()
                self.__cf_workers_ai_api_token = lines[1].strip()
                self.__model = lines[2].strip()
                self.__session_cap = int(lines[3].strip())
            else:
                logging.info("Incomplete configuration file.")
                self.__cf_account_id = ""
                self.__cf_workers_ai_api_token = ""
                self.__model = "@hf/thebloke/openchat_3.5-awq"
                self.__session_cap = 16
        
        self.__API_BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{self.__cf_account_id}/ai/run/"
        self.__api_url = f"{self.__API_BASE_URL}{self.__model}"
        self.__headers = {"Authorization": f"Bearer {self.__cf_workers_ai_api_token}"}
        self.user_messages = user_messages
    
    def chat(self, message, uid) -> str:
        if str(uid) not in self.user_messages.keys():    
            self.user_messages[str(uid)] = []                     

        user_msg = str(message)

        if len(self.user_messages[str(uid)]) > self.__session_cap:
            self.user_messages[str(uid)].pop(0)
        self.user_messages[str(uid)].append({"role": "user", "content": user_msg})

        input = { "messages": self.user_messages[str(uid)] }
        response = requests.post(self.__api_url, headers=self.__headers, json=input)

        assistant_req = "请求出错"
        ok = response.json().get("success", False)
        if ok:
            if len(self.user_messages[str(uid)]) > self.__session_cap:
                self.user_messages[str(uid)].pop(0)
            assistant_req = response.json().get("result", {}).get("response", None)
            if assistant_req != None:
                self.user_messages[str(uid)].append({"role": "assistant", "content": assistant_req})

        # print(assistant_req)
        return assistant_req
