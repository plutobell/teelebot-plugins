# -*- coding:utf-8 -*-
'''
@creation time: 2020-3-21
@last_modify: 2020-12-15
@The backend is powered by Pi Dashboard Go
    https://github.com/plutobell/pi-dashboard-go
'''
import requests

#设置重连次数
requests.adapters.DEFAULT_RETRIES = 5

def Top(bot, message):
    root_id = bot.root_id
    plugin_dir = bot.plugin_dir
    if str(message["from"]["id"]) == root_id:
        url = ""
        username = ""
        password = ""
        with open(bot.path_converter(plugin_dir + "Top/config.ini"), "r") as f:
            sets = f.readlines()
            if len(sets) != 3 and "/\n" in sets:
                for i, set in enumerate(sets):
                    if set == "/\n":
                        sets.pop(i)

            url = sets[0].strip("\n")
            username = sets[1].strip("\n")
            password = sets[2].strip("\n")

        status = bot.sendChatAction(message["chat"]["id"], "typing")
        status = bot.sendMessage(message["chat"]["id"], text="正在获取服务器信息，请稍等...", parse_mode="HTML", reply_to_message_id=message["message_id"])
        txt_message_id = status["message_id"]
        try:
            with requests.get(url=url + "?ajax=true", auth=(username, password)) as req:
                if req.json().get("version", False) is False:
                    req.close()
                    status = bot.editMessageText(chat_id=message["chat"]["id"], message_id=txt_message_id, text="抱歉，获取服务器信息失败", parse_mode="HTML")
                    bot.message_deletor(15, message["chat"]["id"], txt_message_id)
                else:
                    contents = req.json()
                    version = contents.get("version")

                    Hostname = contents.get("hostname")
                    # IP = contents.get("ip")
                    # Device_model = contents.get("model")
                    System = contents.get("system")
                    top_time_head = contents.get("now_time_ymd")
                    top_time_tail = contents.get("now_time_hms")
                    top_up = contents.get("uptime")
                    top_load_average = [
                        contents.get("load_average_1m"),
                        contents.get("load_average_5m"),
                        contents.get("load_average_15m"),
                    ]
                    top_user = contents.get("login_user_count")
                    cpu_id = contents.get("cpu_status_idle")
                    memory_total = contents.get("memory_total")
                    # memory_percent = contents.get("memory_real_percent")
                    avail_memory = contents.get("memory_available")
                    Cpu_temperature = contents.get("cpu_temperature")
                    # Cpu_cores = contents.get("cpu_cores")
                    # hd_name = contents.get("disk_name")
                    hd_used = contents.get("disk_used")
                    hd_avail = contents.get("disk_total")
                    # hd_percent = contents.get("disk_used_percent")
                    net_in_data = contents.get("net_status_in_data_format")
                    net_out_data = contents.get("net_status_out_data_format")
                    # net_dev_name = contents.get("net_dev_name")
                    process_running = contents.get("load_average_process_running")
                    process_total = contents.get("load_average_process_total")

                    msg = "<b>服务器：" + str(Hostname) + "</b>\n\n" + \
                        "<code>查询时间：<i>" + str(top_time_head) + " " + str(top_time_tail) + "</i>\n" + \
                        "后端版本：<b>v" + str(version).strip() + "</b>\n\n" + \
                        "系统版本：<b>" + str(System).strip() + "</b>\n" + \
                        "登入用户：<b>" + str(top_user) + "</b> user(s)\n" + \
                        "运行时间：<b>" + str(top_up) + "</b>\n" + \
                        "平均负载：<b>" + str(top_load_average[0]) + " " + str(top_load_average[1]) + " " + str(top_load_average[2]) + "</b>\n" + \
                        "核心温度：<b>" + str(Cpu_temperature) + "℃</b>\n" + \
                        "核心用量：<b>" + str(round(100.0-float(cpu_id), 2)) + "%</b>\n" + \
                        "进程统计：<b>" + str(process_running) + "/" + str(process_total) + "</b>\n" + \
                        "网络监控：<b>↓" + str(net_in_data) + "</b>/<b>↑" + str(net_out_data) + "</b>\n" + \
                        "内存用量：<b>" + str(round((float(memory_total)-float(avail_memory))/1024, 2)) + "GB</b>/<b>" + str(round(float(memory_total)/1024,2)) + "GB</b>\n" + \
                        "硬盘用量：<b>" + str(hd_used) + "GB</b>/<b>" + str(hd_avail) + "GB</b></code>" + \
                        "\n\n<code>Powered by Pi Dashboard Go</code>"

                    status = bot.editMessageText(chat_id=message["chat"]["id"], message_id=txt_message_id, text=msg, parse_mode="HTML")
                    bot.message_deletor(60, message["chat"]["id"], txt_message_id)
        except Exception as e:
            print("Top plugin error:", e)
            status = bot.editMessageText(chat_id=message["chat"]["id"], message_id=txt_message_id, text="抱歉，获取失败!", parse_mode="HTML")
            bot.message_deletor(15, message["chat"]["id"], status["message_id"])
    else:
        status = bot.sendChatAction(message["chat"]["id"], "typing")
        status = bot.sendMessage(message["chat"]["id"], text="抱歉，您无权操作!", parse_mode="HTML", reply_to_message_id=message["message_id"])
        bot.message_deletor(15, message["chat"]["id"], status["message_id"])
