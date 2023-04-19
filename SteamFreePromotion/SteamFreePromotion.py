# -*- coding:utf-8 -*-
"""
@Creation: 2021-05-30
@Last modify: 2023-04-19
"""
import re
import requests
from bs4 import BeautifulSoup

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def SteamFreePromotion(bot, message):
    proxies = bot.proxies

    chat_id = message["chat"]["id"]
    message_id = message["message_id"]

    prefix = ""
    with open(bot.path_converter(bot.plugin_dir + "SteamFreePromotion/__init__.py"), "r", encoding="utf-8") as init:
        prefix = init.readline()[1:].strip()

    with open(bot.path_converter(bot.plugin_dir + "SteamFreePromotion/steam_logo.png"), "rb") as p:
        photo = p.read()
    bot.sendChatAction(chat_id, "typing")
    status = bot.sendPhoto(chat_id=chat_id, photo=photo,  parse_mode="HTML",
        caption="<b>Steam Free Promotion</b>\n\nGetting the latest Steam free promotion information, please wait...",
        reply_to_message_id=message_id)
    tip_message_id = status["message_id"]

    games = get_steam_free_promotion_info(proxies=proxies)
    if games != False:
        msg = "<b>Steam Free Promotion</b>\n\n"
        for game, info in games.items():
            msg += '<b><a href="' + info["game_links"] + '">' + game + '</a></b>' + '\n' + \
                '<i><b>Posted on ' + info["announcement_date"] + '</b></i>' + '\n' + \
                info["text_info"] + '\n\n'

        status = bot.editMessageCaption(chat_id=chat_id,
            message_id=tip_message_id, caption=msg, parse_mode="HTML")
        bot.message_deletor(60, chat_id, tip_message_id)
    else:
        msg = "<b>Steam Free Promotion</b>\n\nFailed to get, please retry."
        status = bot.editMessageCaption(chat_id=chat_id,
            message_id=tip_message_id, caption=msg, parse_mode="HTML")
        bot.message_deletor(60, chat_id, tip_message_id)


def get_steam_free_promotion_info(proxies):
    url = "https://steamcommunity.com/groups/freegamesinfoo/announcements"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko",
        "Host": "steamcommunity.com",
        "Referer": "https://steamcommunity.com/groups/freegamesinfoo"
    }

    try:
        req = requests.get(url=url, headers=headers, verify=False, proxies=proxies)
        soup = BeautifulSoup(req.text, "html.parser")
        announcements = soup.find_all("div", class_="announcement")

        games = {}
        for announcement in announcements:
            a_links = announcement.find("a", class_="large_title")
            bodytext = announcement.find("div", class_="bodytext")
            announcement_byline = announcement.find("div", class_="announcement_byline")

            text_info = bodytext.text.strip("\n").strip("\r").strip()
            pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
            urls = re.findall(pattern, text_info)

            game_links = None
            for url in urls:
                if "store.steampowered.com/app" in url:
                    game_links = "/".join(url.strip().split("/")[:6])
            if game_links is None:
                continue

            text_info = text_info.replace(url.strip(), "")
            announcement_date = announcement_byline.text.split("-")[0].strip("\n").strip("\r").strip()
            game_name = a_links.text
            announcement_detail = a_links["href"]
            # print(announcement_date, game_name, announcement_detail, text_info, game_links)

            if len(announcement_detail) > 200:
                announcement_detail = announcement_detail[:200]
            if len(text_info) > 200:
                text_info = text_info[:200]

            games[game_name] = {}
            games[game_name]["game_links"] = game_links
            games[game_name]["announcement_detail"] = announcement_detail
            games[game_name]["announcement_date"] = announcement_date
            games[game_name]["text_info"] = text_info

        soup.decompose()
        return games
    except:
        soup.decompose()
        return False