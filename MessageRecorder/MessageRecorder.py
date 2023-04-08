# -*- coding:utf-8 -*-
"""
@description: Message Recorder
@creation date: 2023-04-07
@last modification: 2023-04-08
@author: Pluto (github.com/plutobell)
"""
import io
import time
import sqlite3
import logging
import jieba
import wordcloud
import numpy as np
from PIL import Image

pil_logger = logging.getLogger('PIL')  
pil_logger.setLevel(logging.INFO)
jieba.setLogLevel(jieba.logging.INFO)

def MessageRecorder(bot, message):

    bot_id =bot.bot_id
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    message_id = message["message_id"]

    message_type = message["message_type"]
    chat_type = message["chat"]["type"]

    prefix = ""
    with open(bot.path_converter(bot.plugin_dir + "MessageRecorder/__init__.py"), "r", encoding="utf-8") as init:
        prefix = init.readline()[1:].strip()


    db_path = bot.path_converter(bot.plugin_dir + "MessageRecorder/MessageRecorder.db")
    db = Database(db_path)


    fileds = [
        "id integer PRIMARY KEY",
        "chatid text NOT NULL ",
        "userid text NOT NULL",
        "status integer NOT NULL",
        "lastchange timestamp NOT NULL"
    ]
    db.create_table(table_name="activation", fields=fileds)
    req = db.query_data(table_name="activation", condition={"chatid": str(chat_id)})
    if len(req) == 0:
        data = {
            "chatid": str(chat_id),
            "userid": "",
            "status": 0,
            "lastchange": message.get("date", "")
        }
        db.insert_data(table_name="activation", data=data)
    
    table_name = str(chat_id).replace("-", "")
    if chat_type == "private":
        table_name = "p" + table_name
    elif chat_type == "supergroup":
        table_name = "g" + table_name

    fileds = [
        "id integer PRIMARY KEY",
        "userid text NOT NULL ",
        "type text NOT NULL",
        "content text NOT NULL",
        "date timestamp NOT NULL"
    ]
    db.create_table(table_name=table_name, fields=fileds)
    # print(message)

    prefix = "/mr"
    admin_commands = [prefix+"on", prefix+"off"]
    commands = [
        prefix+"wc",
        prefix+"gwc"
    ]
    admin_list = chat_admin_list(bot=bot, chat_id=chat_id)
    if message_type == "text" and message.get("text", "") in admin_commands:
        
        if str(user_id) not in admin_list:
            bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id=chat_id, text="Permission denied.", parse_mode="text", reply_to_message_id=message_id)
            bot.message_deletor(15, status["chat"]["id"], status["message_id"])

            if chat_type != "private" and str(bot_id) in admin_list:
                bot.message_deletor(20, chat_id, message_id)
        else:
            status = 0
            msg = "Message Recorder."
            if message.get("text", "") == prefix+"on":
                status = 1
                msg = "Message Recorder On."
            elif message.get("text", "") == prefix+"off":
                status = 0
                msg = "Message Recorder Off."
            update = {
                "chatid": str(chat_id),
                "userid": str(user_id),
                "status": status,
                "lastchange": message.get("date", "")
            }
            db.update_data(table_name="activation", update=update, condition={"chatid": str(chat_id)})
            bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="text", reply_to_message_id=message_id)
            bot.message_deletor(15, status["chat"]["id"], status["message_id"])

            if chat_type != "private" and str(bot_id) in admin_list:
                bot.message_deletor(20, chat_id, message_id)

    elif message_type == "text" and message.get("text", "") in commands:
        reply_to_message = message.get("reply_to_message", None)
        target_user_id = ""
        if reply_to_message != None:
            target_user_id = reply_to_message["from"]["id"]

        user_final_id = user_id
        for_other_user = False
        break_if = False
        if message_type != "private" and reply_to_message != None:
            if str(user_id) in admin_list:
                user_final_id = target_user_id
                for_other_user = True
            else:
                bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(chat_id=chat_id, text="Permission denied.", parse_mode="text", reply_to_message_id=message_id)
                bot.message_deletor(15, status["chat"]["id"], status["message_id"])
                if chat_type != "private" and str(bot_id) in admin_list:
                    bot.message_deletor(15, chat_id, message_id)
                break_if = True
        
        table_name = str(chat_id).replace("-", "")
        if chat_type == "private":
            table_name = "p" + table_name
        elif chat_type == "supergroup":
            table_name = "g" + table_name

        if message.get("text", "") == prefix+"wc" and not break_if:
            condition={
                "userid": str(user_final_id),
                "type": "text"
            }
            req = db.query_data(table_name=table_name, condition=condition)
            if len(req) > 0:
                text_list = []
                now_timestamp = time.time()
                for r in req:
                    if len(r[3]) > 1 and r[3][0] == "/":
                        continue
                    if abs(int(now_timestamp) - int(r[4])) < 604800: # 30d
                        text_list.append(r[3])
                
                bot.sendChatAction(chat_id, "typing")
                shape_path = bot.path_converter(bot.plugin_dir + "MessageRecorder/shape.png")
                stopwords_path = bot.path_converter(bot.plugin_dir + "MessageRecorder/stopwords.txt")
                with open(stopwords_path, "a", encoding="utf-8") as f: pass
                font_path = bot.path_converter(bot.plugin_dir + "MessageRecorder/font.ttf")
                img_bytes = generate_wordcloud(
                    text_list=text_list,
                    shape_path=shape_path,
                    stopwords_path=stopwords_path,
                    font_path=font_path)
                user_name = "Untitled"
                first_name = message.get("from", {}).get("first_name", "")
                last_name = message.get("from", {}).get("last_name", "")
                if for_other_user:
                    first_name = reply_to_message.get("from", {}).get("first_name", "")
                    last_name = reply_to_message.get("from", {}).get("last_name", "") 
                if first_name != "" or last_name != "":
                    user_name = first_name + " " + last_name
                caption = "This is <b><a href='tg://user?id=" + str(user_id) + "'>"+ str(user_name) + "</a></b>" + \
                    "'s word cloud for the past <b>30</b> days."
                status = bot.sendPhoto(chat_id=chat_id, photo=img_bytes,
                    caption=caption, parse_mode="HTML", reply_to_message_id=message_id)
                bot.message_deletor(60, status["chat"]["id"], status["message_id"])

                if chat_type != "private" and str(bot_id) in admin_list:
                    bot.message_deletor(65, chat_id, message_id)
            else:
                bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(chat_id=chat_id, text="No Data.", parse_mode="text", reply_to_message_id=message_id)
                bot.message_deletor(15, status["chat"]["id"], status["message_id"])

                if chat_type != "private" and str(bot_id) in admin_list:
                    bot.message_deletor(20, chat_id, message_id)
        elif message.get("text", "") == prefix+"gwc":
            if chat_type != "private":
                condition={"type": "text"}
                req = db.query_data(table_name=table_name, condition=condition)
                if len(req) > 0:
                    text_list = []
                    now_timestamp = time.time()
                    for r in req:
                        if len(r[3]) > 1 and r[3][0] == "/":
                            continue
                        if abs(int(now_timestamp) - int(r[4])) < 604800: # 30d
                            text_list.append(r[3])
                    
                    bot.sendChatAction(chat_id, "typing")
                    shape_path = bot.path_converter(bot.plugin_dir + "MessageRecorder/shape.png")
                    stopwords_path = bot.path_converter(bot.plugin_dir + "MessageRecorder/stopwords.txt")
                    with open(stopwords_path, "a", encoding="utf-8") as f: pass
                    font_path = bot.path_converter(bot.plugin_dir + "MessageRecorder/font.ttf")
                    img_bytes = generate_wordcloud(
                        text_list=text_list,
                        shape_path=shape_path,
                        stopwords_path=stopwords_path,
                        font_path=font_path)
                    caption = "This is <b>the group</b>'s word cloud for the past <b>30</b> days."
                    status = bot.sendPhoto(chat_id=chat_id, photo=img_bytes,
                        caption=caption, parse_mode="HTML", reply_to_message_id=message_id)
                    bot.message_deletor(60, status["chat"]["id"], status["message_id"])

                    if chat_type != "private" and str(bot_id) in admin_list:
                        bot.message_deletor(65, chat_id, message_id)
                else:
                    bot.sendChatAction(chat_id, "typing")
                    status = bot.sendMessage(chat_id=chat_id, text="No Data.", parse_mode="text", reply_to_message_id=message_id)
                    bot.message_deletor(15, status["chat"]["id"], status["message_id"])

                    if chat_type != "private" and str(bot_id) in admin_list:
                        bot.message_deletor(20, chat_id, message_id)
            else:
                bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(chat_id=chat_id, text="Private chat is not supported.", parse_mode="text", reply_to_message_id=message_id)
                bot.message_deletor(15, status["chat"]["id"], status["message_id"])
            
            

    req = db.query_data(table_name="activation", condition={"chatid": str(chat_id)})
    activation_status = req[0][3]
    if int(activation_status) == 0:
        return

    match str(message_type):
        case "text":
            content = message.get("text", "")
        case "sticker":
            content = message.get(str(message_type), {}).get("file_unique_id", "")
        case _:
            content = ""
    data = {
        "userid": str(user_id),
        "type": str(message_type),
        "content": content,
        "date": message.get("date", "")
    }
    db.insert_data(table_name=table_name, data=data)

    db.close()



# 定义一个数据库操作类
# Generated by Bing AI
class Database:

    # 初始化方法，创建数据库连接和游标对象
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    # 创建表的方法，接受一个表名和一个字段列表
    def create_table(self, table_name, fields):
        # 拼接sql语句
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ("
        for field in fields:
            sql += f"{field},"
        sql = sql[:-1] + ")"
        # 执行sql语句
        self.cursor.execute(sql)
        # 提交事务
        self.conn.commit()

    # 插入数据的方法，接受一个表名和一个数据字典
    def insert_data(self, table_name, data):
        # 拼接sql语句
        sql = f"INSERT INTO {table_name} ("
        for key in data.keys():
            sql += f"{key},"
        sql = sql[:-1] + ") VALUES ("
        for value in data.values():
            sql += f"'{value}',"
        sql = sql[:-1] + ")"
        # 执行sql语句
        self.cursor.execute(sql)
        # 提交事务
        self.conn.commit()

    # 查询数据的方法，接受一个表名和一个条件字典，返回一个结果列表
    def query_data(self, table_name, condition):
        # 拼接sql语句
        sql = f"SELECT * FROM {table_name} WHERE "
        for key, value in condition.items():
            sql += f"{key}='{value}' AND "
        sql = sql[:-5]
        # 执行sql语句
        self.cursor.execute(sql)
        # 获取查询结果
        result = self.cursor.fetchall()
        return result

    # 更新数据的方法，接受一个表名，一个更新字典和一个条件字典
    def update_data(self, table_name, update, condition):
        # 拼接sql语句
        sql = f"UPDATE {table_name} SET "
        for key, value in update.items():
            sql += f"{key}='{value}',"
        sql = sql[:-1] + " WHERE "
        for key, value in condition.items():
            sql += f"{key}='{value}' AND "
        sql = sql[:-5]
        # 执行sql语句
        self.cursor.execute(sql)
        # 提交事务
        self.conn.commit()

    # 删除数据的方法，接受一个表名和一个条件字典
    def delete_data(self, table_name, condition):
        # 拼接sql语句
        sql = f"DELETE FROM {table_name} WHERE "
        for key, value in condition.items():
            sql += f"{key}='{value}' AND "
        sql = sql[:-5]
        # 执行sql语句
        self.cursor.execute(sql)
        # 提交事务
        self.conn.commit()

    # 关闭数据库连接的方法
    def close(self):
        self.cursor.close()
        self.conn.close()



def chat_admin_list(bot, chat_id) -> list:
    admin_list = []

    req = bot.getChatAdministrators(chat_id=chat_id)
    for r in req:
        admin_list.append(str(r["user"]["id"]))
    admin_list.append(str(bot.root_id))

    return admin_list


# Generated by Bing AI
def generate_wordcloud(text_list, shape_path, stopwords_path, font_path):
    # 将字符串列表转换为一个长字符串
    text = " ".join(text_list)
    # 使用jieba进行分词
    words = jieba.cut(text)
    words_clear = []
    for word in words:
        if len(word) > 1:
            words_clear.append(word)
    # 将分词结果转换为一个字符串，用空格分隔
    word_string = " ".join(words_clear)
    # 加载停用词
    stopwords = set()
    content = [line.strip() for line in open(stopwords_path,'r' ,encoding="utf-8").readlines()]
    stopwords.update(content)
    # 读取形状图片文件
    shape = Image.open(shape_path)
    # 将图片转换为灰度模式，并获取其像素矩阵
    mask = shape.convert("L")
    mask_array = np.array(mask)
    # 创建词云对象，设置参数
    
    wc = wordcloud.WordCloud(
        scale=2,
        font_path=font_path, # 设置字体路径，如果没有，会报错
        mask=mask_array, # 设置形状遮罩
        background_color="white", # 设置背景颜色
        max_words=100, # 设置最大显示的词数
        max_font_size=100, # 设置字体最大值
        min_font_size=10, # 设置字体最小值
        random_state=42, # 设置随机状态，保证每次生成的结果一样
        collocations=False, # 避免重复单词的出现
        stopwords=stopwords
    )
    # 根据分词结果生成词云
    wc.generate(word_string)
    # 将词云转换为图片对象
    image = wc.to_image()
    # 创建一个字节流对象，用于存储图片数据
    byte_io = io.BytesIO()
    # 将图片保存到字节流对象中，格式为png
    image.save(byte_io, "png")
    # 获取字节流对象的值，即二进制数据
    byte_data = byte_io.getvalue()
    # 返回二进制数据
    return byte_data