# -*- coding:utf-8 -*-
'''
creation time: 2020-6-26
last_modify: 2025-05-22
'''
import os
from datetime import timedelta, datetime
import psutil

GAP = 5

def Init(bot):
    feedback_links = None
    detail_links = None
    if os.path.exists(bot.join_plugin_path("config.ini")):
        with open(bot.join_plugin_path("config.ini"), 'r') as f:
            lines = f.readlines()
            if len(lines) >= 1:
                feedback_links = lines[0].strip()
            if len(lines) >= 2:
                detail_links = lines[1].strip()
                if len(detail_links) == 0 or detail_links == "":
                    detail_links = None

            if len(str(feedback_links)) == 0 or feedback_links == "":
                feedback_links = None

    if detail_links == None:
        return

    if not os.path.exists(bot.join_plugin_path("uid.txt")):
        with open(bot.join_plugin_path("uid.txt"), "w", encoding="utf-8") as s:
            ok, uid = bot.schedule.add(
                    GAP, supervisor_func, (bot, feedback_links, detail_links, GAP))
            if ok:
                s.write(uid)
            else:
                if uid == "Full":
                    raise Exception("周期性任务队列已满.")
                else:
                    raise Exception("遇到错误. \n\n " + uid)
    else:
        uid = ""
        with open(bot.join_plugin_path("uid.txt"), "r", encoding="utf-8") as s:
            uid = s.read().strip()
        ok, uid = bot.schedule.find(uid)
        if ok:
            bot.schedule.delete(uid)

        with open(bot.join_plugin_path("uid.txt"), "w", encoding="utf-8") as s:
            ok, uid = bot.schedule.add(
                    GAP, supervisor_func, (bot, feedback_links, detail_links, GAP))
            if ok:
                s.write(uid)
            else:
                raise Exception("无法开启自动更新.")


def Uptime(bot, message):

    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    text = message["text"]
    VERSION = bot.version
    prefix = "uptime"

    detail_links = None
    feedback_links = None
    if not os.path.exists(bot.join_plugin_path("config.ini")):
        detail_links = None
        feedback_links = None
    else:
        with open(bot.join_plugin_path("config.ini"), 'r') as f:
            lines = f.readlines()
            if len(lines) >= 1:
                feedback_links = lines[0].strip()
            if len(lines) >= 2:
                detail_links = lines[1].strip()
                if len(detail_links) == 0 or detail_links == "":
                    detail_links = None

            if len(str(feedback_links)) == 0 or feedback_links == "":
                feedback_links = None

    if detail_links != None:
        uid = ""
        with open(bot.join_plugin_path("uid.txt"), "r", encoding="utf-8") as s:
            uid = s.read().strip()
        ok, uid = bot.schedule.find(uid)
        if not ok:
            with open(bot.join_plugin_path("uid.txt"), "w", encoding="utf-8") as s:
                ok, uid = bot.schedule.add(
                        GAP, supervisor_func, (bot, feedback_links, detail_links, GAP))
                if ok:
                    s.write(uid)
                else:
                    raise Exception("无法开启自动更新.")


    if text[1:len(prefix)+1] == prefix:
        time_second = bot.uptime
        time_format = timedelta(seconds=time_second)
        response_times = bot.response_times
        response_chats = len(bot.response_chats)
        response_users = len(bot.response_users)
        installed_plugin = len(bot.plugin_bridge)
        process = psutil.Process(os.getpid())
        memory = process.memory_info().rss / 1024 / 1024
        cpu = process.cpu_percent(interval=0.5)
        load_avg_tuple = os.getloadavg() if hasattr(os, "getloadavg") else (0.0, 0.0, 0.0)
        load_avg_str = " ".join(f"{x:.2f}" for x in load_avg_tuple)

        bot.sendChatAction(chat_id=chat_id, action="typing")
        inlineKeyboard = [
                    [
                        {"text": "👀", "url": detail_links}
                    ]
                ]
        if detail_links != None:
            reply_markup = {
                "inline_keyboard": inlineKeyboard
            }
        else:
            reply_markup = None

        msg = "<code>" + (
            f"我已运行 {time_second} 秒\n"
            f"即：{time_format}\n\n"
            f"我的状态如下:\n"
            f"响应指令: {response_times} 次\n"
            f"服务用户: {response_users} 位\n"
            f"服务群组: {response_chats} 个\n"
            f"安装插件: {installed_plugin} 个\n\n"
            f"平均负载: {load_avg_str}\n"
            f"核心占用: {cpu:.2f}%\n"
            f"内存占用: {memory:.2f}M\n\n"
            f"框架版本: teelebot v{VERSION}"
        ) + "</code>"

        bot.sendMessage(
            chat_id=chat_id, text=msg, parse_mode="HTML", del_msg_after=30,
            reply_to_message_id=message_id, reply_markup=reply_markup)


def supervisor_func(bot, feedback_links, detail_links, gap=5):
    detail_links_split = detail_links.split("/")
    detail_chat_id = None
    detail_msg_id = None
    if len(detail_links_split) >= 5:
        detail_msg_id = detail_links_split[len(detail_links_split)-1]
        detail_chat_id = detail_links_split[len(detail_links_split)-2]

    time_second = bot.uptime
    time_format = timedelta(seconds=time_second)
    response_times = bot.response_times
    response_chats = len(bot.response_chats)
    response_users = len(bot.response_users)
    installed_plugin = len(bot.plugin_bridge)
    process = psutil.Process(os.getpid())
    memory = process.memory_info().rss / 1024 / 1024
    cpu = process.cpu_percent(interval=0.5)
    load_avg_tuple = os.getloadavg() if hasattr(os, "getloadavg") else (0.0, 0.0, 0.0)
    load_avg_str = " ".join(f"{x:.2f}" for x in load_avg_tuple)
    now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    msg = (
        f"<a href='tg://user?id={str(bot.bot_id)}'><b>我:\n\n</b></a><code>"
        f"已运行 {time_second} 秒\n"
        f"即：{time_format}\n\n"
        f"我的状态如下:\n"
        f"响应指令: {response_times} 次\n"
        f"服务用户: {response_users} 位\n"
        f"服务群组: {response_chats} 个\n"
        f"安装插件: {installed_plugin} 个\n\n"
        f"平均负载: {load_avg_str}\n"
        f"核心占用: {cpu:.2f}%\n"
        f"内存占用: {memory:.2f}M\n\n"
        f"刷新间隔: {gap} sec\n"
        f"最后刷新: {str(now_time)}\n\n"
        f"框架版本: teelebot v{bot.version}"
    ) + "</code>"

    inlineKeyboard = [
            [
                {"text": "离线反馈", "url": str(feedback_links)}
            ]
        ]

    if feedback_links != None:
        reply_markup = {
            "inline_keyboard": inlineKeyboard
        }
    else:
        reply_markup = None

    bot.editMessageText(run_in_thread=True, chat_id=f"@{detail_chat_id}",
        message_id=detail_msg_id, text=msg, parse_mode="HTML", reply_markup=reply_markup)
