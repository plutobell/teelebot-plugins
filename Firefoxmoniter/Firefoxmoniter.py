# -*- coding:utf-8 -*-
import requests, lxml, hashlib
from bs4 import BeautifulSoup

def Firefoxmoniter(bot, message):
    plugin_dir = bot.plugin_dir
    with open(bot.path_converter(plugin_dir + "Firefoxmoniter/__init__.py"), encoding="utf-8") as f:
        h = f.readline()[1:]
    if len(message["text"]) < len(h):
        status = bot.sendChatAction(message["chat"]["id"], "typing")
        status = bot.sendMessage(message["chat"]["id"], "查询失败！\n邮件地址为空!", parse_mode="HTML", reply_to_message_id=message["message_id"])
        bot.message_deletor(15, message["chat"]["id"], status["message_id"])
        return False
    email = message["text"][len(h)-1:]
    email = email.strip()
    if all([ '@' in email, '.' in email.split('@')[1] ]):
        ehash = hashlib.sha1(email.encode("utf-8")) #经测试由sha1加密
        emailhash = ehash.hexdigest()
    else:
        status = bot.sendChatAction(message["chat"]["id"], "typing")
        status = bot.sendMessage(message["chat"]["id"], "查询失败！\n请检查邮件格式!", parse_mode="HTML", reply_to_message_id=message["message_id"])
        bot.message_deletor(15, message["chat"]["id"], status["message_id"])
        return False
    root_id = bot.root_id
    if str(message["from"]["id"]) == root_id:
        status = bot.sendChatAction(message["chat"]["id"], "typing")
        status = bot.sendMessage(message["chat"]["id"], "主人，正在查询邮件地址[" + str(email) + "]，请稍等...", parse_mode="HTML", reply_to_message_id=message["message_id"])
        txt_message_id = status["message_id"]
    else:
        status = bot.sendChatAction(message["chat"]["id"], "typing")
        status = bot.sendMessage(message["chat"]["id"], "正在查询邮件地址" + str(email) + "，请稍等...", parse_mode="HTML", reply_to_message_id=message["message_id"])
        txt_message_id = status["message_id"]

    protocol, ip, port = get_ip()
    proxies = {
        protocol:protocol + '://' + ip + ':' + port
    }

    url = "https://monitor.firefox.com/"
    r_session = requests.Session()
    with r_session.get(url, proxies=proxies) as page:
        if not page.status_code == requests.codes.ok:
            status = bot.editMessageText(chat_id=message["chat"]["id"],message_id=txt_message_id, text="查询失败！\n操作过于频繁，请稍后再试!", parse_mode="text")
            bot.message_deletor(15, message["chat"]["id"], status["message_id"])
            return False
        page.encoding = "utf-8"
        connect_sid = page.cookies["connect.sid"]
        soup = BeautifulSoup(page.text, "lxml")
        csrf = soup.find_all("input")[0]["value"]
        soup.decompose()

    url = "https://monitor.firefox.com/scan"
    data = {
        '_csrf': csrf,
        'email': email,
        'emailHash': emailhash
    }
    headers = {
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'cookie': 'connect.sid=' + connect_sid + "; _ga=GA1.3.1750251620.1566005038; _gid=GA1.3.1329192982.1566005038; _gat=1;",
        'origin': 'https://monitor.firefox.com',
        'referer': 'https://monitor.firefox.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    with r_session.post(url=url, data=data, headers=headers, proxies=proxies, verify=False) as page:
        page.encoding = "utf-8"

        result = ""
        soup = BeautifulSoup(page.text, "lxml")

    if "扫描结果" in soup.find("title").text:
        result += "电子邮件地址 <b>" + email +"</b> 出现在 <b>" + str(soup.find("span", class_="bold").text) + "</b> 次已知数据外泄事件中。\n\n"
        sections = soup.find_all("div", class_="flx flx-col")
        if len(sections) > 10:
            sections = sections[:10]
        for section in sections:
            source = section.find_all("span")[0].text + "\n"
            date = "事件记录时间:\n" + section.find_all("span")[2].text + "\n"
            data = "泄露的数据:\n" + section.find_all("span")[4].text + "\n"
            result += source + date + data + "\n"
        result += "<i>(只显示前10条)</i>"

        soup.decompose()
        status = bot.editMessageText(chat_id=message["chat"]["id"],message_id=txt_message_id, text=result, parse_mode="HTML")
        bot.message_deletor(60, message["chat"]["id"], status["message_id"])
    else:
        soup.decompose()
        status = bot.editMessageText(chat_id=message["chat"]["id"], text="查询失败！\n请检测命令格式!", parse_mode="text")
        bot.message_deletor(15, message["chat"]["id"], status["message_id"])

def get_ip():
    url = u"http://ip.jiangxianli.com/api/proxy_ip"
    with requests.get(url=url) as req:
        status = req.json().get("msg")
        if status == "成功":
            protocol = req.json().get("data").get("protocol")
            ip = req.json().get("data").get("ip")
            port = req.json().get("data").get("port")
            return protocol, ip, port


if __name__ == "__main__":
    Firefoxmoniter("hi@ojoll.com")