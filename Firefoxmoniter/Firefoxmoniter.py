# -*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup

def Firefoxmoniter(bot, message):
    plugin_dir = bot.plugin_dir
    with open(bot.path_converter(plugin_dir + "Firefoxmoniter/__init__.py"), encoding="utf-8") as f:
        h = f.readline()[1:]
    if len(message["text"]) < len(h):
        status = bot.sendChatAction(chat_id=message["chat"]["id"], action="typing")
        status = bot.sendMessage(
            chat_id=message["chat"]["id"],
            text="查询失败，邮件地址为空。",
            parse_mode="HTML",
            reply_to_message_id=message["message_id"]
        )
        bot.message_deletor(15, message["chat"]["id"], status["message_id"])
        return False
    email = message["text"][len(h)-1:]
    email = email.strip()
    if all([ '@' in email, '.' in email.split('@')[1] ]):
        pass
        # ehash = hashlib.sha1(email.encode("utf-8")) #经测试由sha1加密
        # emailhash = ehash.hexdigest()
    else:
        status = bot.sendChatAction(chat_id=message["chat"]["id"], action="typing")
        status = bot.sendMessage(
            chat_id=message["chat"]["id"],
            text="查询失败，请检查邮件格式。",
            parse_mode="HTML",
            reply_to_message_id=message["message_id"]
        )
        bot.message_deletor(15, message["chat"]["id"], status["message_id"])
        return False
    root_id = bot.root_id
    if str(message["from"]["id"]) == root_id:
        status = bot.sendChatAction(chat_id=message["chat"]["id"], action="typing")
        status = bot.sendMessage(
            chat_id=message["chat"]["id"],
            text="正在查询邮件地址 <b>" + str(email) + " </b>，请稍等...",
            parse_mode="HTML",
            reply_to_message_id=message["message_id"]
        )
        txt_message_id = status["message_id"]
    else:
        status = bot.sendChatAction(chat_id=message["chat"]["id"], action="typing")
        status = bot.sendMessage(
            chat_id=message["chat"]["id"],
            text="正在查询邮件地址 <b>" + str(email) + " </b>，请稍等...",
            parse_mode="HTML",
            reply_to_message_id=message["message_id"]
        )
        txt_message_id = status["message_id"]


    r_session = requests.Session()
    # Step 1
    url = "https://monitor.firefox.com"
    connect_sid, monitor_x_csrf_token = "", ""
    with r_session.get(url, timeout=5, verify=False) as page:
        if not page.status_code == requests.codes.ok:
            status = bot.editMessageText(
                chat_id=message["chat"]["id"],
                message_id=txt_message_id,
                text="查询失败，操作过于频繁，请稍后再试。"
            )
            bot.message_deletor(15, message["chat"]["id"], status["message_id"])
            return False
        connect_sid = r_session.cookies["connect.sid"]
        monitor_x_csrf_token = page.cookies["monitor.x-csrf-token"]

    # Step 2
    url = "https://monitor.firefox.com/scan/#email=" + email
    headers = {
        'referer': 'https://monitor.firefox.com/',
        'cookie': 'connect.sid=' + connect_sid + '; monitor.x-csrf-token=' + monitor_x_csrf_token  + ';',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35',
    }
    with r_session.get(url, headers=headers, timeout=5, verify=False) as page:
        if not page.status_code == requests.codes.ok:
            status = bot.editMessageText(
                chat_id=message["chat"]["id"],
                message_id=txt_message_id,
                text="查询失败，操作过于频繁，请稍后再试。"
            )
            bot.message_deletor(15, message["chat"]["id"], status["message_id"])
            return False
        page.encoding = "utf-8"
        # connect_sid = page.cookies["connect.sid"]
        soup = BeautifulSoup(page.text, "html.parser")
        monitor_x_csrf_token = page.cookies["monitor.x-csrf-token"]
        x_csrf_token = soup.find('template', {'id':'data'})['data-csrf-token']
        soup.decompose()

    # Step 3
    url = "https://monitor.firefox.com/api/v1/scan/"
    data = {
        'email': email,
    }
    headers = {
        'Content-Type': 'application/json',
        'cookie': 'connect.sid=' + connect_sid + '; monitor.x-csrf-token=' + monitor_x_csrf_token  + ';',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35',
        'x-csrf-token': x_csrf_token,
        'accept': 'application/json',
    }
    with r_session.post(url=url, json=data, headers=headers,
                        timeout=5, verify=False) as page:
        if not page.status_code == requests.codes.ok:
            status = bot.editMessageText(
                chat_id=message["chat"]["id"],
                message_id=txt_message_id,
                text="查询失败，操作过于频繁，请稍后再试。"
            )
            bot.message_deletor(15, message["chat"]["id"], status["message_id"])
            return False
        page.encoding = "utf-8"
        data = []
        result = ""
        if page.json().get("success", False):
            total = page.json().get("total", 0)
            data = page.json().get("breaches", [])
            result += "电子邮件地址 <b>" + email +"</b> 出现在 <b>" + str(total) + "</b> 次已知数据外泄事件中。\n\n"
            for d in data:
                # name = f'名称: {d["Name"]}\n'
                title = f'标题: {d["Title"]}\n'
                domain = f'域名: {d["Domain"]}\n'
                breach_date = f'泄露时间: {d["BreachDate"].split("T")[0]}\n'
                added_date = f'记录时间: {d["AddedDate"].split("T")[0]}\n'
                is_verified_str = "No"
                is_verified_bool = d["IsVerified"]
                if is_verified_bool:
                    is_verified_str = "Yes"
                is_verified = f'是否验证: {is_verified_str}\n'
                data_classes =  f'数据类型: {", ".join(d["DataClasses"])}\n'
                pwn_count = f'数据量: {d["PwnCount"]}\n'
                # description = f'描述: {d["Description"]}\n'
                result += "<code>" + title + domain + pwn_count + \
                    breach_date + added_date + is_verified + data_classes + "</code>\n"

            inlineKeyboard = [
                [
                    {"text": "查看更多", "url": "https://monitor.firefox.com/scan/#email=" + email},
                ]
            ]
            reply_markup = {
                "inline_keyboard": inlineKeyboard
            }
            status = bot.editMessageText(
                chat_id=message["chat"]["id"],
                message_id=txt_message_id,
                text=result, parse_mode="HTML",
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
            bot.message_deletor(60, message["chat"]["id"], status["message_id"])
        else:
            status = bot.editMessageText(
                chat_id=message["chat"]["id"],
                message_id=txt_message_id,
                text="查询失败，请检查命令格式。"
            )
            bot.message_deletor(15, message["chat"]["id"], status["message_id"])


