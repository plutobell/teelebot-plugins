# -*- coding: utf-8 -*-
# Program: Reminder
# Description: Reminder Plugin
# Creation: 2023-12-11
# Last modification: 2024-05-17

import os
import time
import sqlite3
from datetime import datetime

def Init(bot):
    if not os.path.exists(bot.join_plugin_path("uid.txt")):
        with open(bot.join_plugin_path("uid.txt"), "w", encoding="utf-8") as s:
            ok, uid = bot.schedule.add(60, reminder_func, (bot,))
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
            ok, uid = bot.schedule.add(60, reminder_func, (bot,))
            if ok:
                s.write(uid)
            else:
                raise Exception("无法开启自动更新.")

def Reminder(bot, message):
    # root_id = bot.root_id

    chat_id = message.get("chat", {}).get("id")
    user_id = message.get("from", {}).get("id")
    message_id = message.get("message_id")

    message_type = message.get("message_type")
    chat_type = message.get("chat", {}).get("type")

    command = ""
    ok, metadata = bot.metadata.read()
    if ok:
        command = metadata.get("Command")


    subcommands = {
        f'{command}add': ["添加提醒事项", _add],
        f'{command}del': ["删除提醒事项", _del],
        f'{command}clear': ["清空事项列表", _clear],
        f'{command}show': ["显示提醒事项列表", _show],
        f'{command}status': ["显示统计信息", _status],
        f'{command}register': ["手动注册周期性任务池", _register],
    }

    text = message.get("text", "").strip()

    if not text.startswith(command):
        return
    
    if text == command:
        msg = "<b>Reminder 插件功能</b>\n\n"
        for k, v in subcommands.items():
            msg += f'<b>{k}</b> - {v[0]}\n'
        msg += f"\n<b>注意：只有私聊过Bot才能正常使用本插件</b>"

        bot.sendChatAction(chat_id=chat_id, action="typing")
        bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML",
                        reply_to_message_id=message_id)
        return
    
    for subcommand in subcommands.keys():
        if text.startswith(subcommand):
            db = ReminderDB(bot.join_plugin_path("Reminder.db"))
            subcommands.get(subcommand)[1](db, bot, chat_id, user_id, message_id, chat_type, text, subcommand)
            break


def _add(db, bot, chat_id, user_id, message_id, chat_type, text, subcommand):
    text_split = text.split(" ", 2)

    if len(text_split) != 3:
        bot.sendChatAction(chat_id=chat_id, action="typing")
        bot.sendMessage(chat_id=chat_id, text=f"指令格式错误，请参考如下示例指令:\n <code>{subcommand} 测试标题 2023-12-12 12:12:12</code>", parse_mode="HTML",
                        reply_to_message_id=message_id)
    else:
        title = text_split[1]
        datetime_str = text_split[2]
        datetime_str = datetime_str.replace("：", ":", -1)
        
        if not is_valid_datetime(datetime_str):
            bot.sendChatAction(chat_id=chat_id, action="typing")
            bot.sendMessage(chat_id=chat_id, text="时间格式错误，请参考如下示例时间:\n <code>2023-12-12 12:12:12</code>", parse_mode="HTML",
                            reply_to_message_id=message_id)
            return
        if len(title) >= 50:
            bot.sendChatAction(chat_id=chat_id, action="typing")
            bot.sendMessage(chat_id=chat_id, text="标题过长", parse_mode="HTML",
                            reply_to_message_id=message_id)
            return

        current_timestamp = time.time()
        input_timestamp = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S').timestamp()
        gap = input_timestamp-current_timestamp
        if gap < 3600:
            bot.sendChatAction(chat_id=chat_id, action="typing")
            bot.sendMessage(chat_id=chat_id, text="事项到期时间距离现在<b>小于一小时</b>", parse_mode="HTML",
                            reply_to_message_id=message_id)
            return

        try:
            req = db.query_reminders(conditions={"user_id": str(user_id)})
            if not req[0]:
                bot.sendChatAction(chat_id=chat_id, action="typing")
                bot.sendMessage(chat_id=chat_id, text=f"添加失败", parse_mode="HTML",
                                reply_to_message_id=message_id)
                return
            elif len(req[1]) >= 10:
                bot.sendChatAction(chat_id=chat_id, action="typing")
                bot.sendMessage(chat_id=chat_id, text=f"队列已满，请先清理旧事项", parse_mode="HTML",
                                reply_to_message_id=message_id)
                return

            req = db.add_reminder(user_id=str(user_id), title=title, due_date=datetime_str, status="created", type="countdown")
            if not req[0]:
                bot.sendChatAction(chat_id=chat_id, action="typing")
                bot.sendMessage(chat_id=chat_id, text=f"添加失败", parse_mode="HTML",
                                reply_to_message_id=message_id)
                return
            
            bot.sendChatAction(chat_id=chat_id, action="typing")
            bot.sendMessage(chat_id=chat_id, text="<b>添加成功,</b>\n将在事项<b>到期前一小时</b>通过私聊提醒您\n\n<b>注意，只有私聊过Bot才能收到提醒消息</b>", parse_mode="HTML",
                            reply_to_message_id=message_id)
        except Exception as e:
            print(e)
            bot.sendChatAction(chat_id=chat_id, action="typing")
            bot.sendMessage(chat_id=chat_id, text="添加失败", parse_mode="HTML",
                            reply_to_message_id=message_id)

def _del(db, bot, chat_id, user_id, message_id, chat_type, text, subcommand):
    text_split = text.split(" ", 1)

    if len(text_split) != 2:
        bot.sendChatAction(chat_id=chat_id, action="typing")
        bot.sendMessage(chat_id=chat_id, text=f"指令格式错误，请参考如下示例指令:\n <code>{subcommand} id</code>", parse_mode="HTML",
                        reply_to_message_id=message_id)
    else:
        id = text_split[1]

        if not id.isdigit():
            bot.sendChatAction(chat_id=chat_id, action="typing")
            bot.sendMessage(chat_id=chat_id, text="提醒事项的ID只能是数字", parse_mode="HTML",
                            reply_to_message_id=message_id)
            return
    
        try:
            req = db.query_reminders(conditions={"id": id})
            if not req[0]:
                bot.sendChatAction(chat_id=chat_id, action="typing")
                bot.sendMessage(chat_id=chat_id, text=f"未找到该提醒事项", parse_mode="HTML",
                                reply_to_message_id=message_id)
                return
            else:
                reminder_user_id = req[1][0][1]
                if str(user_id) != str(reminder_user_id):
                    bot.sendChatAction(chat_id=chat_id, action="typing")
                    bot.sendMessage(chat_id=chat_id, text=f"无权操作", parse_mode="HTML",
                                    reply_to_message_id=message_id)
                    return
            req = db.delete_reminder(reminder_id=id)
            if not req[0]:
                bot.sendChatAction(chat_id=chat_id, action="typing")
                bot.sendMessage(chat_id=chat_id, text=f"删除失败", parse_mode="HTML",
                                reply_to_message_id=message_id)
                return

            bot.sendChatAction(chat_id=chat_id, action="typing")
            bot.sendMessage(chat_id=chat_id, text="<b>删除成功</b>", parse_mode="HTML",
                            reply_to_message_id=message_id)
        except Exception as e:
            print(e)
            bot.sendChatAction(chat_id=chat_id, action="typing")
            bot.sendMessage(chat_id=chat_id, text="删除失败", parse_mode="HTML",
                            reply_to_message_id=message_id)

def _clear(db, bot, chat_id, user_id, message_id, chat_type, text, subcommand):
    try:
        req = db.query_reminders(conditions={"user_id": str(user_id)})
        if not req[0]:
            bot.sendChatAction(chat_id=chat_id, action="typing")
            bot.sendMessage(chat_id=chat_id, text=f"清空列表失败", parse_mode="HTML",
                            reply_to_message_id=message_id)
            return
        
        error_counts = 0
        for reminder in req[1]:
            id = reminder[0]
            req = db.delete_reminder(reminder_id=id)
            if not req[0]:
                error_counts += 1
        
        if error_counts == 0:
            bot.sendChatAction(chat_id=chat_id, action="typing")
            bot.sendMessage(chat_id=chat_id, text="<b>清空列表成功</b>", parse_mode="HTML",
                            reply_to_message_id=message_id)
        else:
            bot.sendChatAction(chat_id=chat_id, action="typing")
            bot.sendMessage(chat_id=chat_id, text="清空列表失败", parse_mode="HTML",
                            reply_to_message_id=message_id)
    except Exception as e:
        print(e)
        bot.sendChatAction(chat_id=chat_id, action="typing")
        bot.sendMessage(chat_id=chat_id, text="清空列表失败", parse_mode="HTML",
                        reply_to_message_id=message_id)

def _show(db, bot, chat_id, user_id, message_id, chat_type, text, subcommand):
    try:
        req = db.query_reminders(conditions={"user_id": str(user_id)})
        if not req[0]:
            bot.sendChatAction(chat_id=chat_id, action="typing")
            bot.sendMessage(chat_id=chat_id, text=f"获取列表失败", parse_mode="HTML",
                            reply_to_message_id=message_id)
            return
        
        msg = f"<b>Reminder 列表 [{len(req[1])}/10]</b>\n\n"
        if len(req[1]) == 0:
            msg += "无事项"
        for i, reminder in enumerate(req[1]):
            id = reminder[0]
            title = reminder[2]
            due_time = reminder[3]
            status = reminder[4]

            msg += f'<b>[事项{i+1}]</b>\n'
            msg += f'事项ID: <code>{id}</code>\n'
            msg += f'事项标题: <code>{title}</code>\n'
            msg += f'到期时间: <code>{due_time}</code>\n'
            msg += f'当前状态: <code>{status}</code>\n\n'

        bot.sendChatAction(chat_id=chat_id, action="typing")
        status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML",
                        reply_to_message_id=message_id)
        bot.message_deletor(10 * (len(req[1])+1), status["chat"]["id"], status["message_id"])
    except Exception as e:
        print(e)
        bot.sendChatAction(chat_id=chat_id, action="typing")
        bot.sendMessage(chat_id=chat_id, text="获取列表失败", parse_mode="HTML",
                        reply_to_message_id=message_id)

def _status(db, bot, chat_id, user_id, message_id, chat_type, text, subcommand):
    try:
        req = db.query_reminders()
        if not req[0]:
            bot.sendChatAction(chat_id=chat_id, action="typing")
            bot.sendMessage(chat_id=chat_id, text=f"获取统计信息失败", parse_mode="HTML",
                            reply_to_message_id=message_id)
            return
        
        register_status = "未注册"
        uid = ""
        if os.path.exists(bot.join_plugin_path("uid.txt")):
            with open(bot.join_plugin_path("uid.txt"), "r", encoding="utf-8") as s:
                uid = s.read().strip()
            ok, uid = bot.schedule.find(uid)
            if ok:
                register_status = "已注册"
            else:
                uid = ""

        users = []
        for reminder in req[1]:
            userid = reminder[1]
            if userid not in list(users):
                users.append(userid)

        reminder_counts = len(req[1])
        user_counts = len(users)
        now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
        msg = f"<b>Reminder 统计信息</b>\n\n"
        msg += f'<code>用户数量: {user_counts} 位</code>\n'
        msg += f'<code>事项条数: {reminder_counts} 条</code>\n'
        msg += f'<code>任务池注册状态: {register_status}</code>\n'
        msg += f'<code>任务池标识: </code><code>{uid}</code>\n\n'
        msg += f'<code>查询时间: {now_time}</code>\n'

        bot.sendChatAction(chat_id=chat_id, action="typing")
        status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML",
                        reply_to_message_id=message_id)
        bot.message_deletor(60, status["chat"]["id"], status["message_id"])
    except Exception as e:
        print(e)
        bot.sendChatAction(chat_id=chat_id, action="typing")
        bot.sendMessage(chat_id=chat_id, text="获取统计信息失败", parse_mode="HTML",
                        reply_to_message_id=message_id)

def _register(db, bot, chat_id, user_id, message_id, chat_type, text, subcommand):
    if not os.path.exists(bot.join_plugin_path("uid.txt")):
        msg = ""
        with open(bot.join_plugin_path("uid.txt"), "w", encoding="utf-8") as s:
            ok, uid = bot.schedule.add(60, reminder_func, (bot,))
            if ok:
                s.write(uid)
                msg = "注册成功\n周期性任务池标识为: <code>" + str(uid) + "</code>"
            else:
                if uid == "Full":
                    msg = "周期性任务队列已满."
                else:
                    msg = "遇到错误. \n\n <i>" + uid + "</i>"
        status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML",
            reply_to_message_id=message_id)
        bot.message_deletor(60, status["chat"]["id"], status["message_id"])
    else:
        uid = ""
        msg = ""
        with open(bot.join_plugin_path("uid.txt"), "r", encoding="utf-8") as s:
            uid = s.read().strip()
        ok, uid = bot.schedule.find(uid)
        if ok:
            msg = "任务存在于周期性任务池中\n标识为: <code>" + str(uid) + "</code>"
        else:
            with open(bot.join_plugin_path("uid.txt"), "w", encoding="utf-8") as s:
                ok, uid = bot.schedule.add(60, reminder_func, (bot,))
                if ok:
                    s.write(uid)
                    msg = "注册成功\n周期性任务池标识为: <code>" + str(uid) + "</code>"
                else:
                    msg = "无法注册."
        status = bot.sendMessage(chat_id=chat_id, text=msg,
            parse_mode="HTML", reply_to_message_id=message_id)
        bot.message_deletor(30, status["chat"]["id"], status["message_id"])

def is_valid_datetime(date_string, format_string="%Y-%m-%d %H:%M:%S"):
    try:
        datetime.strptime(date_string, format_string)
        return True
    except ValueError:
        return False

def reminder_func(bot):
    db = ReminderDB(bot.join_plugin_path("Reminder.db"))
    req = db.query_reminders(conditions={"status": "created"})
    if not req[0]:
        return

    for reminder in req[1]:
        id = reminder[0]
        user_id = reminder[1]
        title = reminder[2]
        due_time = reminder[3]
        status = reminder[4]
        type = reminder[5]

        current_timestamp = time.time()
        reminder_timestamp = datetime.strptime(due_time, '%Y-%m-%d %H:%M:%S').timestamp()
        gap = reminder_timestamp-current_timestamp

        if gap < 0:
            status = "expired"

        msg = f'<b>Reminder 事项到期提醒</b>\n\n'
        msg += f'事项ID: <code>{id}</code>\n'
        msg += f'事项标题: <code>{title}</code>\n'
        msg += f'到期时间: <code>{due_time}</code>\n'
        msg += f'当前状态: <code>{status}</code>\n\n'
        
        is_expiring = False
        if gap < 0:
            is_expiring = True
            msg += "该事项<b>已到期</b>，请及时处理"
            req = db.modify_reminder(reminder_id=id, new_status="expired")
        elif gap < 3600:
            is_expiring = True
            msg += "该事项<b>即将到期</b>，请及时处理"
            req = db.modify_reminder(reminder_id=id, new_status="reminded")
        
        if is_expiring:
            bot.sendChatAction(run_in_thread=True, chat_id=user_id, action="typing")
            bot.sendMessage(run_in_thread=True, chat_id=user_id, text=msg, parse_mode="HTML")


class ReminderDB:
    def __init__(self, db_name):
        if not os.path.exists(db_name):
            open(db_name, "w").close()

        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def __del__(self):
        self.conn.close()

    def create_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS reminder (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id CHAR(16),
            title CHAR(128) NOT NULL,
            due_date DATETIME NOT NULL,
            status CHAR(16),
            type CHAR(16)
        );
        '''
        try:
            self.conn.execute(query)
            self.conn.commit()
            return True, "Table created successfully."
        except sqlite3.Error as e:
            return False, f"Error creating table: {e}"

    def add_reminder(self, user_id, title, due_date, status, type):
        query = 'INSERT INTO reminder (user_id, title, due_date, status, type) VALUES (?, ?, ?, ?, ?);'
        try:
            self.conn.execute(query, (user_id, title, due_date, status, type))
            self.conn.commit()
            return True, f"Reminder added: {title} due on {due_date}"
        except sqlite3.Error as e:
            return False, f"Error adding reminder: {e}"

    def delete_reminder(self, reminder_id):
        query = 'DELETE FROM reminder WHERE id = ?;'
        try:
            self.conn.execute(query, (reminder_id,))
            self.conn.commit()
            return True, f"Reminder with ID {reminder_id} deleted."
        except sqlite3.Error as e:
            return False, f"Error deleting reminder: {e}"

    def modify_reminder(self, reminder_id, new_title=None, new_due_date=None, new_status=None):
        query = 'SELECT * FROM reminder WHERE id = ?;'
        cursor = self.conn.execute(query, (reminder_id,))
        reminder = cursor.fetchone()

        if not reminder:
            return False, f"No reminder found with ID {reminder_id}."

        current_title, current_due_date, current_status = reminder[2], reminder[3], reminder[4]

        if new_title:
            current_title = new_title
        if new_due_date:
            current_due_date = new_due_date
        if new_status:
            current_status = new_status

        update_query = '''
        UPDATE reminder 
        SET title = ?, due_date = ?, status = ?
        WHERE id = ?;
        '''

        try:
            self.conn.execute(update_query, (current_title, current_due_date, current_status, reminder_id))
            self.conn.commit()
            return True, f"Reminder with ID {reminder_id} modified."
        except sqlite3.Error as e:
            return False, f"Error modifying reminder: {e}"

    def query_reminders(self, conditions={}):
        try:
            query = 'SELECT * FROM reminder WHERE '
            params = []
            for key, value in conditions.items():
                query += f'{key} = ? AND '
                params.append(value)
            query = query[:-4]

            cursor = self.conn.execute(query, params)
            reminders = cursor.fetchall()
            
            if not reminders:
                return True, []
            else:
                reminder_list = []
                for reminder in reminders:
                    reminder_list.append(reminder)
                return True, reminder_list
        except Exception as e:
            return False, f"Error querying reminder: {str(e)}"


