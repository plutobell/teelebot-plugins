# -*- coding:utf-8 -*-
# Program: ChatGPT
# Description: ChatGPT Chat Plugin
# Creation: 2023-03-11
# Last modification: 2023-04-10

import openai
import logging
import requests
from time import sleep

logging.getLogger("openai").setLevel(logging.CRITICAL)
requests.adapters.DEFAULT_RETRIES = 5

def ChatGPT(bot, message):
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
            match e["type"]:
                case "mention":
                    e_offset = int(e["offset"])
                    e_length = int(e["length"])
                    mention_username = text[e_offset:e_offset+e_length]
                    # print(mention_username, bot_username)
                    if mention_username == "@"+bot_username:
                        is_mention = True
                case "bot_command":
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
                conf_path = bot.path_converter(bot.plugin_dir + "ChatGPT/config.ini")
                ok, user_messages = bot.buffer.read()
                # print(user_messages)
                if not ok: user_messages = {}
                ai = ChatAI(conf_path=conf_path, user_messages=user_messages)
                msg = ai.chat(message=text, uid=chat_id)
                msg = msg.replace("`", "", -1)
                bot.buffer.write(buffer=ai.user_messages)
                bot.sendChatAction(chat_id, "typing")
                bot.sendMessage(chat_id=chat_id,text=msg, reply_to_message_id=message_id)
            except Exception as e:
                print(e)
                bot.sendChatAction(chat_id, "typing")
                bot.sendMessage(chat_id=chat_id, text="接口调用失败。", reply_to_message_id=message_id)
                
    except Exception as e:
        print(e)
        bot.sendChatAction(chat_id, "typing")
        bot.sendMessage(chat_id=chat_id, text="出错了。", reply_to_message_id=message_id)


class ChatAI:
    def __init__(self, conf_path, user_messages={}):
        with open(conf_path, "r", encoding="utf-8") as conf:
            lines = conf.readlines()
            if len(lines) >= 5:
                openai.api_key = lines[0].strip()
                self.__model = lines[1].strip()
                self.__session_cap = int(lines[2].strip())
                openai.proxy = lines[3].strip()
                self.__bot_setting = lines[4].strip()
            else:
                logging.info("Incomplete configuration file.")
                openai.api_key = ""
                self.__model = "gpt-3.5-turbo"
                self.__session_cap = 16
                openai.proxy = ""
                self.__bot_setting = ""

        self.user_messages = user_messages
        self.__bot_setting_message = {"role": "system", "content": self.__bot_setting}

    def chat(self, message, uid) -> str:
        if str(uid) not in self.user_messages.keys():    
            self.user_messages[str(uid)] = [{},]                     
        self.user_messages[str(uid)][0] = self.__bot_setting_message

        user_msg = str(message)

        if len(self.user_messages[str(uid)]) > self.__session_cap:
            self.user_messages[str(uid)].pop(1)
        self.user_messages[str(uid)].append({"role": "user", "content": user_msg})

        response = openai.ChatCompletion.create(
        model=self.__model,
        messages=self.user_messages[str(uid)])
        
        assistant_req = response["choices"][0]["message"]["content"]
        if len(self.user_messages[str(uid)]) > self.__session_cap:
            self.user_messages[str(uid)].pop(1)
        self.user_messages[str(uid)].append({"role": "assistant", "content": assistant_req})

        # print(assistant_req)
        return assistant_req
    
    def set_bot(self, content):
        self.__bot_setting = content
        for k, _ in self.user_messages:
            self.user_messages[k][0] = self.__bot_setting_message
    
    def read_bot_setting(self) -> str:

        return self.__bot_setting