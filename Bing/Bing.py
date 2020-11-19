# -*- coding:utf-8 -*-
import os
import time
import sqlite3
import requests
import datetime

def Bing(bot, message):
    prefix = "bing"
    text = message["text"]
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    message_id = message["message_id"]

    if text[1:len(prefix)+1] == prefix:
        plugin_dir = bot.plugin_dir
        db = SqliteDB(bot, plugin_dir)
        if len(text.split(" ")) == 1:
            timestamp = time.strftime('%Y%m%d',time.localtime(time.time()))
            result = db.select(enddate=timestamp)
            if result:
                enddate = result[1]
                date = enddate[:4] + '-' + enddate[4:6] + '-' + enddate[6:]
                img_url = "https://cn.bing.com" + result[2] + "&ensearch=0&mkt=zh-cn"
                copyright_ = result[3]
            else:
                img = bing_img()
                if img != False:
                    enddate = str(img["enddate"])
                    data_time = datetime.datetime.strptime(enddate, '%Y%m%d')
                    dbdate = "".join(str(data_time).split(" ")[0].split("-"))
                    date = str(data_time).split(" ")[0]
                    img_url = "https://cn.bing.com" + img["url"] + "&ensearch=0&mkt=zh-cn" # 中文显示
                    copyright_ = img["copyright"]
                    db.insert(enddate=dbdate, url=img["url"], copyright_=copyright_)
                else:
                    status = bot.sendChatAction(chat_id, "typing")
                    status = bot.sendMessage(chat_id=chat_id, text="获取失败，请重试!", parse_mode="HTML", reply_to_message_id=message["message_id"])
                    bot.message_deletor(15, chat_id, status["message_id"])
                    return

            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendPhoto(chat_id=chat_id, photo=img_url, caption=copyright_+"\n\n"+date, parse_mode="HTML", reply_to_message_id=message["message_id"])

        elif len(text.split(" ")) == 2:
            command = text.split(" ")[1]
            if command == "rand":
                result = db.random_select()
                if result:
                    enddate = result[1]
                    date = enddate[:4] + '-' + enddate[4:6] + '-' + enddate[6:]
                    img_url = "https://cn.bing.com" + result[2] + "&ensearch=0&mkt=zh-cn"
                    copyright_ = result[3]
                else:
                    img = bing_img()
                    if img != False:
                        enddate = str(img["enddate"])
                        data_time = datetime.datetime.strptime(enddate, '%Y%m%d')
                        dbdate = "".join(str(data_time).split(" ")[0].split("-"))
                        date = str(data_time).split(" ")[0]
                        img_url = "https://cn.bing.com" + img["url"] + "&ensearch=0&mkt=zh-cn" # 中文显示
                        copyright_ = img["copyright"]
                        result = db.select(dbdate)
                        if not result:
                            db.insert(enddate=dbdate, url=img["url"], copyright_=copyright_)
                    else:
                        status = bot.sendChatAction(chat_id, "typing")
                        status = bot.sendMessage(chat_id=chat_id, text="获取失败，请重试!", parse_mode="HTML", reply_to_message_id=message["message_id"])
                        bot.message_deletor(15, chat_id, status["message_id"])

                status = bot.sendChatAction(chat_id, "typing")
                status = bot.sendPhoto(chat_id=chat_id, photo=img_url, caption=copyright_+"\n\n"+date, parse_mode="HTML", reply_to_message_id=message["message_id"])

            elif command == "update":
                if not os.path.exists(bot.path_converter(plugin_dir + "Bing/last_updated.txt")):
                    with open(bot.path_converter(plugin_dir + "Bing/last_updated.txt"), "w", encoding="utf-8") as s:
                        s.write("20201024")
                last_updated = ""
                with open(bot.path_converter(plugin_dir + "Bing/last_updated.txt"), "r", encoding="utf-8") as s:
                    last_updated = s.read().strip()
                    last_updated = datetime.datetime.strptime(last_updated, '%Y%m%d')
                    last_updated = str(last_updated).split(" ")[0]

                if not os.path.exists(bot.path_converter(plugin_dir + "Bing/uid.txt")):
                    msg = ""
                    with open(bot.path_converter(plugin_dir + "Bing/uid.txt"), "w", encoding="utf-8") as s:
                        ok, uid = bot.schedule.add(86520, update_func, (bot, plugin_dir))
                        if ok:
                            s.write(uid)
                            msg = "成功开启自动更新\n周期性任务池标识为: <code>" + str(uid) + "</code>" +\
                                "\n\n最后更新: <code>" + str(last_updated) + "</code>"
                        else:
                            if uid == "Full":
                                msg = "周期性任务队列已满."
                            else:
                                msg = "遇到错误. \n\n <i>" + uid + "</i>"
                    status = bot.sendMessage(chat_id, text=msg, parse_mode="HTML",
                        reply_to_message_id=message_id)
                    bot.message_deletor(60, status["chat"]["id"], status["message_id"])
                else:
                    uid = ""
                    msg = ""
                    with open(bot.path_converter(plugin_dir + "Bing/uid.txt"), "r", encoding="utf-8") as s:
                        uid = s.read().strip()
                    ok, uid = bot.schedule.find(uid)
                    if ok:
                        msg = "任务存在于周期性任务池中\n标识为: <code>" + str(uid) + "</code>" +\
                            "\n\n最后更新: <code>" + str(last_updated) + "</code>"
                    else:
                        with open(bot.path_converter(plugin_dir + "Bing/uid.txt"), "w", encoding="utf-8") as s:
                            ok, uid = bot.schedule.add(86520, update_func, (bot, plugin_dir))
                            if ok:
                                s.write(uid)
                                msg = "成功开启自动更新\n周期性任务池标识为: <code>" + str(uid) + "</code>" +\
                                    "\n\n最后更新: <code>" + str(last_updated) + "</code>"
                            else:
                                msg = "无法开启自动更新."
                    status = bot.sendMessage(chat_id, text=msg,
                        parse_mode="HTML", reply_to_message_id=message_id)
                    bot.message_deletor(30, status["chat"]["id"], status["message_id"])
            else:
                if validate(command):
                    data_time = datetime.datetime.strptime(command, '%Y%m%d')
                    dbdate = "".join(str(data_time).split(" ")[0].split("-"))
                    result = db.select(dbdate)
                    if result:
                        enddate = result[1]
                        date = enddate[:4] + '-' + enddate[4:6] + '-' + enddate[6:]
                        img_url = "https://cn.bing.com" + result[2] + "&ensearch=0&mkt=zh-cn"
                        copyright_ = result[3]

                        status = bot.sendChatAction(chat_id, "typing")
                        status = bot.sendPhoto(chat_id=chat_id,
                            photo=img_url, caption=copyright_+"\n\n"+date,
                            parse_mode="HTML", reply_to_message_id=message["message_id"])
                    else:
                        date = dbdate[:4] + '-' + dbdate[4:6] + '-' + dbdate[6:]
                        status = bot.sendChatAction(chat_id, "typing")
                        status = bot.sendMessage(chat_id=chat_id,
                            text="在库中未找到 <b>" + date + "</b> 的图片", parse_mode="HTML", reply_to_message_id=message["message_id"])
                        bot.message_deletor(15, chat_id, status["message_id"])
                else:
                    status = bot.sendChatAction(chat_id, "typing")
                    status = bot.sendMessage(chat_id=chat_id,
                        text="日期格式错误，请检查! <b>(e.g. 20201024)</b>", parse_mode="HTML", reply_to_message_id=message["message_id"])
                    bot.message_deletor(15, chat_id, status["message_id"])
        else:
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id=chat_id, text="指令错误，请检查!", parse_mode="HTML", reply_to_message_id=message["message_id"])
            bot.message_deletor(15, chat_id, status["message_id"])
    else:
        status = bot.sendChatAction(chat_id, "typing")
        status = bot.sendMessage(chat_id=chat_id, text="指令错误，请检查!", parse_mode="HTML", reply_to_message_id=message["message_id"])
        bot.message_deletor(15, chat_id, status["message_id"])

def bing_img():
    url = "https://cn.bing.com/HPImageArchive.aspx?ensearch=0&mkt=zh-cn&format=js&idx=0&n=1"
    try:
        with requests.post(url=url, verify=False) as req:
            if not req.status_code == requests.codes.ok:
                return False
            elif req.json().get("images"):
                return req.json().get("images")[0]
            else:
                return False
    except:
        return False

def validate(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y%m%d')

        return True
    except ValueError:
        return False


def update_func(bot, plugin_dir):
    db = SqliteDB(bot, plugin_dir)
    img = bing_img()
    if img != False:
        enddate = str(img["enddate"])
        data_time = datetime.datetime.strptime(enddate, '%Y%m%d')
        dbdate = "".join(str(data_time).split(" ")[0].split("-"))
        copyright_ = img["copyright"]
        result = db.select(dbdate)
        if not result:
            db.insert(enddate=dbdate, url=img["url"], copyright_=copyright_)
            with open(bot.path_converter(plugin_dir + "Bing/last_updated.txt"), "w", encoding="utf-8") as s:
                s.write(str(dbdate))


class SqliteDB(object):
    def __init__(self, bot, plugin_dir):
        '''
        Open the connection
        '''
        self.conn = sqlite3.connect(
            bot.path_converter(plugin_dir + "Bing/bing.db"), check_same_thread=False)  # 只读模式加上uri=True
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS picture_list (id INTEGER PRIMARY KEY autoincrement, enddate TEXT, url TEXT, copyright TEXT, timestamp INTEGER)")

    def __del__(self):
        '''
        Close the connection
        '''
        self.cursor.close()
        self.conn.commit()
        self.conn.close()

    def insert(self, enddate, url, copyright_):
        '''
        Insert
        '''
        timestamp = int(time.time())
        self.cursor.execute("INSERT INTO picture_list (enddate, url, copyright, timestamp) VALUES (?,?,?,?)",
                            (enddate, url, copyright_, timestamp))

        if self.cursor.rowcount == 1:
            return True
        else:
            return False

    def select(self, enddate):
        '''
        Select
        '''
        self.cursor.execute(
            "SELECT * FROM picture_list WHERE enddate=?", (enddate,))
        result = self.cursor.fetchall()

        if result :
            return result[0]
        else:
            return False

    def random_select(self):
        self.cursor.execute(
            "SELECT * FROM picture_list ORDER BY RANDOM() limit 1")
        result = self.cursor.fetchall()

        if result:
            return result[0]
        else:
            return False

    def delete(self, enddate):
        '''
        Delete
        '''
        self.cursor.execute(
            "DELETE FROM picture_list WHERE enddate=?", (enddate,))

        if self.cursor.rowcount == 1:
            return True
        else:
            return False