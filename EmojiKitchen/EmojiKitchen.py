# -*- coding: utf-8 -*-
'''
creation time: 2025-05-11
last_modify: 2025-05-11
'''
import requests
import re


def EmojiKitchen(bot, message):

    chat_id = message.get("chat", {}).get("id")
    message_id = message.get("message_id")

    command = ""
    ok, metadata = bot.metadata.read()
    if ok:
        command = metadata.get("Command")

    text = message.get("text", "")[len(command)+1:].strip()
    text_slice = text.split("+", 1)
    if len(text_slice) == 2:
        emoji_mix_image_bytes = get_emoji_mix_image(
            input1=text_slice[0], input2=text_slice[1])
        if type(emoji_mix_image_bytes) == str:
            status = bot.sendChatAction(chat_id=chat_id, action="typing")
            status = bot.sendMessage(chat_id=chat_id, text=emoji_mix_image_bytes, parse_mode="HTML",
                                    reply_to_message_id=message_id)
            bot.message_deletor(15, chat_id, status["message_id"])
        elif type(emoji_mix_image_bytes) == bytes:
            bot.sendPhoto(
                chat_id=chat_id, photo=emoji_mix_image_bytes,
                parse_mode="HTML", reply_to_message_id=message_id)
        else:
            status = bot.sendChatAction(chat_id=chat_id, action="typing")
            status = bot.sendMessage(chat_id=chat_id, text="出错了", parse_mode="HTML",
                                    reply_to_message_id=message_id)
            bot.message_deletor(15, chat_id, status["message_id"])
    else:
        msg = "指令格式错误，请检查!\ne.g. <code>/emk 😎+🔒</code>"
        status = bot.sendChatAction(chat_id=chat_id, action="typing")
        status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML",
                                reply_to_message_id=message_id)
        bot.message_deletor(15, chat_id, status["message_id"])


def parse_emoji_or_code(s: str) -> str:
    """
    将 emoji 或 Unicode 编码转换为 API 要求的格式：
    - 输入 emoji：直接返回字符
    - 输入 code：'1F617' 或 'U+1F617' => '1f617'
    """
    s = s.strip()
    if re.fullmatch(r'[Uu\+]?([0-9A-Fa-f]+)(\s+[0-9A-Fa-f]+)*', s):
        parts = re.findall(r'[0-9A-Fa-f]+', s)
        return ''.join(f"{int(p, 16):x}" for p in parts)
    return s

def get_emoji_mix_image(input1: str, input2: str, size: int = 256) -> bytes | str:
    """
    API Source: https://emoji-kitchen.vercel.app/
    """
    if not (16 <= size <= 512):
        return "size 必须在 16 到 512 之间"

    e1 = parse_emoji_or_code(input1.strip())
    e2 = parse_emoji_or_code(input2.strip())

    if len(e1) > 12 or len(e2) > 12:
        return "输入过长，最多允许单个 emoji 或单组组合"

    url = f"https://emojik.vercel.app/s/{e1}_{e2}?size={size}"

    try:
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.content
    except requests.RequestException as e:
        return "请求失败"