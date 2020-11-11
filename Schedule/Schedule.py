# -*- coding:utf-8 -*-
'''
creation time: 2020-11-11
last_modify: 2020-11-12
'''
import time

def Schedule(bot, message):
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    message_id = message["message_id"]
    text = message["text"]

    prefix = "/sched"

    gaps = {
        "1m": 60,
        "2m": 120,
        "5m": 300,
        "10m": 600,
        "15m": 900,
        "30m": 1800,
        "45m": 2700,

        "1h": 3600,
        "2h": 7200,
        "4h": 10800,
        "6h": 21600,
        "8h": 28800,
        "10h": 36000,
        "12h": 43200,

        "1d": 86400,
        "3d": 259200,
        "5d": 432000,
        "7d": 604800,
        "10d": 864000,
        "15d": 1296000,
        "20d": 1728000,
        "30d": 2592000
    }

    if prefix in text and str(chat_id) != bot.config["root"]:
        status = bot.sendMessage(chat_id, text="无权限", parse_mode="HTML",
            reply_to_message_id=message_id)
        bot.message_deletor(15, status["chat"]["id"], status["message_id"])
        return

    if text.split(" ")[0] == "/sched":
        msg = "<b> ===== Schedule 插件功能 ===== </b>" + "%0A%0A" + \
            "<b>/schedadd</b> 添加任务 格式：指令+空格+周期+消息" + "%0A" + \
            "<b>/scheddel</b> 移除任务 格式：指令+空格+标识" + "%0A" + \
            "<b>/schedclear</b> 移除所有任务" + "%0A" + \
            "<b>/schedstatus</b> 查看队列信息" + "%0A%0A" + \
            "<i>支持的周期指令：1m 2m 5m 10m 15m 30m 45m | " + \
            "1h 2h 4h 6h 8h 10h 12h | " + \
            "1d 3d 5d 7d 10d 15d 20d 30d" + "</i>"
        status = bot.sendMessage(chat_id, text=msg, parse_mode="HTML",
            reply_to_message_id=message_id)
        bot.message_deletor(60, status["chat"]["id"], status["message_id"])

    elif text.split(" ")[0] == "/schedadd":
        if  len(text.split(" ")) == 3:
            gap_key = str(text.split(" ")[1])
            gap = gaps[gap_key]
            if gap_key not in gaps.keys():
                msg = "<b>错误的周期，支持的周期指令：</b> %0A%0A" + \
                    "<b>1m 2m 5m 10m 15m 30m 45m %0A" + \
                    "1h 2h 4h 6h 8h 10h 12h %0A" + \
                    "1d 3d 5d 7d 10d 15d 20d 30d" + "</b>"
                bot.sendMessage(chat_id, text=msg, parse_mode="HTML",
                    reply_to_message_id=message_id)
                bot.message_deletor(30, status["chat"]["id"], status["message_id"])
                return

            msg = str(text.split(" ")[2]) + "%0A%0A" + "<i>此消息为定时发送，周期 " + str(gap_key) + "</i>"
            msg = msg.replace("#", " ")
            ok, uid = bot.add_schedule(gap, event, (bot, message["chat"]["id"], msg, "HTML"))
            timestamp = time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(time.time()))
            if ok:
                msg = "<b>任务已加入队列</b>%0A%0A" + \
                    "<b>周期: " + gap_key + "</b>%0A" + \
                    "<b>目标: " + str(chat_id) + "</b>%0A" + \
                    "<b>标识: " + str(uid) + "</b>%0A" + \
                    "<b>时间: " + str(timestamp) + "</b>%0A"
            else:
                if uid == "Full":
                    msg = "<b>队列已满</b>"
                elif uid == "Failure":
                    msg = "<b>遇到错误</b> %0A%0A <i>" + uid + "</i>"
            status = bot.sendMessage(chat_id, text=msg, parse_mode="HTML",
                reply_to_message_id=message_id)
            # bot.message_deletor(30, status["chat"]["id"], status["message_id"])
        else:
            status = bot.sendMessage(chat_id,
                text="<b>指令格式错误 (e.g.: /scheddel gap text)</b>",
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(30, status["chat"]["id"], status["message_id"])

    elif text.split(" ")[0] == "/scheddel":
        if len(text.split(" ")) == 2:
            uid = str(text.split(" ")[1])
            ok, uid = bot.del_schedule(uid)
            if ok:
                msg = "<b>移除了任务 " + str(uid) + "</b>"
            else:
                if uid == "Empty":
                    msg = "<b>队列为空</b>"
                elif uid == "NotFound":
                    msg = "<b>任务未找到</b>"
            status = bot.sendMessage(chat_id, text=msg,
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(30, status["chat"]["id"], status["message_id"])
        else:
            status = bot.sendMessage(chat_id,
                text="<b>指令格式错误 (e.g.: /scheddel uid)</b>",
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(30, status["chat"]["id"], status["message_id"])

    elif text.split(" ")[0] == "/schedclear":
        ok, msgg = bot.clear_schedule()
        if ok:
            msg = "<b>已清空队列</b>"
        else:
            if msgg == "Empty":
                msg = "<b>队列为空</b>"
            elif msgg != "Cleared":
                msg = "<b>遇到错误</b> %0A%0A <i>" + msgg + "</i>"

        status = bot.sendMessage(chat_id, text=msg,
            parse_mode="HTML", reply_to_message_id=message_id)
        bot.message_deletor(30, status["chat"]["id"], status["message_id"])

    elif text.split(" ")[0] == "/schedstatus":
        ok, result = bot.stat_schedule()
        if ok:
            msg = "<b>空闲: " + str(result["free"]) + "%0A" + \
                "使用: " + str(result["used"]) + "%0A" + \
                "容量: " + str(result["size"]) + "</b>%0A"
        else:
            msg = "<b>遇到错误</b> %0A%0A <i>" + result["exception"] + "</i>"
        status = bot.sendMessage(chat_id, text=msg,
            parse_mode="HTML", reply_to_message_id=message_id)
        bot.message_deletor(30, status["chat"]["id"], status["message_id"])

def event(bot, chat_id, msg, parse_mode):
    status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML")

