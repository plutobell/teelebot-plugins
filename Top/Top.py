# -*- coding:utf-8 -*-
'''
creation time: 2020-3-21
last_modify: 2020-11-13
'''
import requests

#设置重连次数
requests.adapters.DEFAULT_RETRIES = 5

def Top(bot, message):
    root_id = bot.root_id
    plugin_dir = bot.plugin_dir
    if str(message["from"]["id"]) == root_id:
        url = ""
        data = {"Key" : ""}
        with open(bot.path_converter(plugin_dir + "Top/key.ini"), "r") as f:
            sets = f.readlines()
            url = sets[0].strip()
            data["Key"] = sets[1].strip()

        status = bot.sendChatAction(message["chat"]["id"], "typing")
        status = bot.sendMessage(message["chat"]["id"], text="主人，正在获取服务器信息，请稍等...", parse_mode="HTML", reply_to_message_id=message["message_id"])
        txt_message_id = status["message_id"]
        try:
            with requests.post(url=url, data=data) as req:
                if req.json().get("status") == False:
                    req.close()
                    status = bot.editMessageText(chat_id=message["chat"]["id"], message_id=txt_message_id, text="抱歉主人，获取服务器信息失败", parse_mode="HTML")
                    bot.message_deletor(15, message["chat"]["id"], txt_message_id)
                elif req.json().get("status") == True:
                    contents = req.json().get("contents")
                    Top = contents.get("Top")
                    Cpu = contents.get("Cpu")
                    Memory = contents.get("Memory")
                    Swap = contents.get("Swap")

                    Hostname = contents.get("Hostname")
                    top_time = Top["top_time"]
                    top_time_head = top_time[0]
                    top_time_tail = top_time[1]
                    top_up = Top["top_up"]
                    top_load_average = Top["top_load_average"]
                    top_user = Top["top_user"]
                    cpu_id = Cpu["cpu_id"]
                    memory_total = Memory["memory_total"]
                    avail_memory = Swap["avail_memory"]
                    Cpu_temperature = contents.get("Cpu_temperature")
                    Hard_disk = contents.get("Hard_disk")
                    hd_used = Hard_disk[0]
                    hd_avail = Hard_disk[1]

                    msg = "<b>服务器：" + str(Hostname) + "</b>\n" + \
                        "查询时间：<i>" + str(top_time_head) + " " + str(top_time_tail) + "</i>\n\n" + \
                        "登入用户：<b>" + str(top_user) + "</b> 个\n" + \
                        "运行时间：<b>" + str(top_up) + "</b>\n" + \
                        "平均负载：<b>" + str(top_load_average[0]) + " " + str(top_load_average[1]) + " " + str(top_load_average[2]) + "</b>\n" + \
                        "CPU温度：<b>" + str(Cpu_temperature) + " ℃</b>\n" + \
                        "CPU用量：<b>" + str(round(100.0-float(cpu_id), 2)) + "</b> 已用，<b>" + str(round(float(cpu_id), 2)) + "</b> 空闲\n" + \
                        "内存用量：<b>" + str(round((float(memory_total)-float(avail_memory))/1024, 2)) + "G</b> 已用，<b>" + str(round(float(avail_memory)/1024,2)) + "G</b> 空闲\n" + \
                        "硬盘用量：<b>" + str(hd_used) + "</b> 已用，<b>" + str(hd_avail) + "</b> 空闲"

                    status = bot.editMessageText(chat_id=message["chat"]["id"], message_id=txt_message_id, text=msg, parse_mode="HTML")
                    bot.message_deletor(60, message["chat"]["id"], txt_message_id)
        except Exception:
            status = bot.editMessageText(chat_id=message["chat"]["id"], message_id=txt_message_id, text="抱歉，查询失败!", parse_mode="HTML")
            bot.message_deletor(15, message["chat"]["id"], status["message_id"])
    else:
        status = bot.sendChatAction(message["chat"]["id"], "typing")
        status = bot.sendMessage(message["chat"]["id"], text="抱歉，您无权操作!", parse_mode="HTML", reply_to_message_id=message["message_id"])
        bot.message_deletor(15, message["chat"]["id"], status["message_id"])
