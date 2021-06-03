# -*- coding:utf-8 -*-
"""
@Creation: 2021-05-30
@Last modify: 2021-06-03
"""
import requests
import lxml
from bs4 import BeautifulSoup

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def SteamFreePromotion(bot, message):

    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    message_id = message["message_id"]

    message_type = message["message_type"]
    chat_type = message["chat"]["type"]

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

    games = get_steam_free_promotion_info()
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


def get_steam_free_promotion_info():
    url = "https://steamcommunity.com/groups/freegamesinfoo/announcements"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko",
        "Host": "steamcommunity.com",
        "Referer": "https://steamcommunity.com/groups/freegamesinfoo"
    }

    try:
        req = requests.get(url=url, headers=headers, verify=False)
        soup = BeautifulSoup(req.text, "lxml")
        announcements = soup.find_all("div", class_="announcement")

        games = {}
        for announcement in announcements:
            a_links = announcement.find("a", class_="large_title")
            bodytext = announcement.find("div", class_="bodytext")
            announcement_byline = announcement.find("div", class_="announcement_byline")

            text_info = bodytext.text.strip("\n").strip("\r").strip()
            game_links = text_info.split("Game:")[1].split(" ")[0]
            text_info = text_info.split("Game:")[0]
            announcement_date = announcement_byline.text.split("-")[0].strip("\n").strip("\r").strip()
            game_name = a_links.text
            announcement_detail = a_links["href"]
            # print(announcement_date, game_name, announcement_detail, text_info, game_links)

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