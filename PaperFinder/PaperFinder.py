# -*- coding:utf-8 -*-
'''
creation time: 2021-06-06
last_modify: 2021-06-06
'''
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import requests


def PaperFinder(bot, message):

    chat_id = message["chat"]["id"]
    message_id = message["message_id"]

    if "text" in message.keys():
        text = message["text"]
    else:
        return

    prefix = ""
    with open(bot.path_converter(bot.plugin_dir + "PaperFinder/__init__.py"), "r", encoding="utf-8") as init:
        prefix = init.readline()[1:].strip()

    page_size = 10

    if "reply_markup" in message.keys() and prefix + "page" in message["callback_query_data"]:
        click_user_id = message["click_user"]["id"]
        if "reply_to_message" in message.keys():
            from_user_id = message["reply_to_message"]["from"]["id"]
        else:
            from_user_id = bot.bot_id
        callback_query_data = message["callback_query_data"]
        if click_user_id == from_user_id:
            page = int(callback_query_data.split("-")[2])
            keyword = str(callback_query_data.split("-")[1])
        else:
            status = bot.answerCallbackQuery(message["callback_query_id"], text="What is your business?", show_alert=True)
            return

        if page == 1:
            start = 0
        else:
            start = page * page_size - 1

        ok, xml_str = arXiv_api_do(search_query=keyword,
                start=start, max_results=page_size,
                sortBy="lastUpdatedDate", sortOrder="descending")
        if ok:
            data = arXiv_xml_parser(xml_str=xml_str)
            if len(data) == 0:
                bot.answerCallbackQuery(message["callback_query_id"],
                    text="It's already the last page.")
                return
        else:
            bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id=chat_id,
                text="Failed to get data, please try again.",
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, chat_id=status["chat"]["id"],
                message_id=status["message_id"])
            return

        msg = '<b>Result for keyword "' + keyword + '" [ Page ' + str(page) + " ]:</b>"
        inlineKeyboard = []
        for i, datum in enumerate(data):
            datum["title"]
            row = [{
                "text": datum["title"],
                "callback_data": prefix + "paper-" + str(keyword) + "-" + str(page) + "-" + str(i)
            }]
            inlineKeyboard.append(row)
        turn_button = []
        if page == 1:
            turn_button = [
                {"text": "Next", "callback_data": prefix + "page-" + str(keyword) + "-" + str(page+1)}
            ]
        elif page > 1 and len(data) == 0:
            turn_button = [
                {"text": "Previous", "callback_data": prefix + "page-" + str(keyword) + "-" + str(page-1)}
            ]
        else:
            turn_button = [
                {"text": "Previous", "callback_data": prefix + "page-" + str(keyword) + "-" + str(page-1)},
                {"text": "Next", "callback_data": prefix + "page-" + str(keyword) + "-" + str(page+1)}
            ]
        inlineKeyboard.append(turn_button)
        reply_markup = {
            "inline_keyboard": inlineKeyboard
        }

        status = bot.editMessageText(
            chat_id=chat_id, message_id=message_id,
            text=msg, parse_mode="HTML",
            reply_markup=reply_markup,
            disable_web_page_preview=True)

        if status != False:
            status = bot.answerCallbackQuery(message["callback_query_id"])
        else:
            bot.answerCallbackQuery(message["callback_query_id"], text="It's already the last page.", show_alert=True)

    elif "reply_markup" in message.keys() and prefix + "paper" in message["callback_query_data"]:
        click_user_id = message["click_user"]["id"]
        if "reply_to_message" in message.keys():
            from_user_id = message["reply_to_message"]["from"]["id"]
        else:
            from_user_id = bot.bot_id
        callback_query_data = message["callback_query_data"]
        if click_user_id == from_user_id:
            page = int(callback_query_data.split("-")[2])
            keyword = str(callback_query_data.split("-")[1])
            paper_id = int(callback_query_data.split("-")[3])
        else:
            status = bot.answerCallbackQuery(message["callback_query_id"], text="What is your business?", show_alert=True)
            return

        if page == 1:
            start = 0
        else:
            start = page * page_size - 1

        ok, xml_str = arXiv_api_do(search_query=keyword,
                start=start, max_results=page_size,
                sortBy="lastUpdatedDate", sortOrder="descending")
        if ok:
            data = arXiv_xml_parser(xml_str=xml_str)
            paper = None
            for i, datum in enumerate(data):
                if i == paper_id:
                    paper = datum
            if len(data) == 0 or paper == None:
                bot.answerCallbackQuery(message["callback_query_id"],
                    text="Failed to get the paper.", show_alert=True)
                return
        else:
            bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id=chat_id,
                text="Failed to get data, please try again.",
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, chat_id=status["chat"]["id"],
                message_id=status["message_id"])
            return

        msg = "<b>Title: </b>" + paper["title"].strip().replace("\n", "").replace("\r", "").replace(keyword, "<b><i><u>"+keyword+"</u></i></b>") + "\n\n" + \
            "<b>Author: </b>" + paper["author"] + "\n\n" + \
            "<b>Summary: </b>" + paper["summary"][:500].strip().replace("\n", "").replace("\r", "").replace(keyword, "<b><i><u>"+keyword+"</u></i></b>") + "..." + "\n\n" + \
            "<b>Published: </b>" + paper["published"] + "\n" + \
            "<b>Updated: </b>" + paper["updated"] + "\n\n"

        links_row = '<b><a href="'+ paper["link"] +'">Link</a></b>'
        if "doi" in paper.keys():
            links_row += '<b> | ' + '<a href="'+ paper["doi"] +'">DOI</a></b>'
        if "pdf" in paper.keys():
            links_row += '<b> | ' + '<a href="'+ paper["pdf"] +'">PDF</a></b>'
        msg += links_row
        msg += "\n\n<code>Thank you to arXiv for use of its open access interoperability.</code>"

        inlineKeyboard = [
            [{"text": "Back to list", "callback_data": prefix + "page-" + str(keyword) + "-" + str(page)}]
        ]
        reply_markup = {
            "inline_keyboard": inlineKeyboard
        }

        status = bot.editMessageText(
            chat_id=chat_id, message_id=message_id,
            text=msg, parse_mode="HTML",
            reply_markup=reply_markup,
            disable_web_page_preview=True)

        if status != False:
            status = bot.answerCallbackQuery(message["callback_query_id"])
        else:
            bot.answerCallbackQuery(message["callback_query_id"], text="Failed to get the paper.", show_alert=True)

    elif prefix in text.split(" ", 1)[0]:
        if len(text.split(" ", 1)) == 2:
            keyword = text.split(" ", 1)[1]
            page = 1

            ok, xml_str = arXiv_api_do(search_query=keyword,
                start=page-1, max_results=page_size,
                sortBy="lastUpdatedDate", sortOrder="descending")
            if ok:
                data = arXiv_xml_parser(xml_str=xml_str)
            else:
                bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(chat_id=chat_id,
                    text="Failed to get data, please try again.",
                    parse_mode="HTML", reply_to_message_id=message_id)
                bot.message_deletor(15, chat_id=status["chat"]["id"],
                    message_id=status["message_id"])
                return

            msg = '<b>Result for keyword "' + keyword + '" [ Page ' + str(page) + " ]:</b>"
            inlineKeyboard = []
            for i, datum in enumerate(data):
                datum["title"]
                row = [{
                    "text": datum["title"],
                    "callback_data": prefix + "paper-" + str(keyword) + "-" + str(page) + "-" + str(i)
                }]
                inlineKeyboard.append(row)
            turn_button = []
            if page == 1:
                turn_button = [
                    {"text": "Next", "callback_data": prefix + "page-" + str(keyword) + "-" + str(page+1)}
                ]
            elif page > 1 and len(data) == 0:
                turn_button = [
                    {"text": "Previous", "callback_data": prefix + "page-" + str(keyword) + "-" + str(page-1)}
                ]
            else:
                turn_button = [
                    {"text": "Previous", "callback_data": prefix + "page-" + str(keyword) + "-" + str(page-1)},
                    {"text": "Next", "callback_data": prefix + "page-" + str(keyword) + "-" + str(page+1)}
                ]
            inlineKeyboard.append(turn_button)

            reply_markup = {
                "inline_keyboard": inlineKeyboard
            }

            if len(data) != 0:
                bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(chat_id=chat_id,
                    text=msg, parse_mode="HTML",
                    reply_to_message_id=message_id,
                    reply_markup=reply_markup, disable_web_page_preview=True)
                bot.message_deletor(180, chat_id=status["chat"]["id"],
                    message_id=status["message_id"])
            else:
                bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(chat_id=chat_id,
                    text=msg + "\n\n No result.", parse_mode="HTML",
                    reply_to_message_id=message_id)
                bot.message_deletor(15, chat_id=status["chat"]["id"],
                    message_id=status["message_id"])

        else:
            bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id=chat_id,
                text="Command format is wrong, please check. \n<b>e.g.: " + prefix + " keyword</b>",
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, chat_id=status["chat"]["id"],
                message_id=status["message_id"])


def arXiv_api_do(search_query,
    id_list=None, start=None, max_results=None,
    sortBy=None, sortOrder=None):
    """Requests arXiv API

    :param search_query: keyword for search
    :param id_list: id_list
    :param start: start id
    :param max_results: max_results
    :param sortBy: can be "relevance", "lastUpdatedDate", "submittedDate"
    :param sortOrder: can be either "ascending" or "descending"
    :return: xml text string
    :rtype: str
    """

    basic_url = "http://export.arxiv.org/api/query"

    data = {"search_query": "all:" + search_query}

    if id_list is not None:
        data["id_list"] = id_list
    if start is not None:
        data["start"] = start
    if max_results is not None:
        data["max_results"] = max_results
    if sortBy is not None and sortBy in ["relevance", "lastUpdatedDate", "submittedDate"]:
        data["sortBy"] = sortBy
    if sortOrder is not None and sortOrder in ["ascending", "descending"]:
        data["sortOrder"] = sortOrder

    try:
        req = requests.post(url=basic_url, data=data)
        # print(req.text)
        return True, req.text
    except:
        return False, ""

def arXiv_xml_parser(xml_str):
    """Parse the xml result of arXiv API

    :param xml_str: the xml string
    :return: xml data dict
    :rtype: dict
    """

    root = ET.fromstring(text=xml_str)
    tree = ET.ElementTree(root)

    data = []
    for elem in tree.iter():
        elem.tag = elem.tag.replace("{http://www.w3.org/2005/Atom}", "")
        if elem.tag == "entry":
            item_dict = {}
            authors = []
            for ent in elem.iter():
                ent.tag = ent.tag.replace("{http://www.w3.org/2005/Atom}", "")
                if ent.tag == "title" and "ArXiv Query:" not in ent.text:
                    item_dict["title"] = ent.text
                if ent.tag == "name":
                    authors.append(ent.text)
                if ent.tag == "published":
                    item_dict["published"] = ent.text
                if ent.tag == "updated":
                    item_dict["updated"] = ent.text
                if ent.tag == "summary":
                    item_dict["summary"] = ent.text
                if ent.tag == "link" and "http://arxiv.org/abs/" in ent.attrib.get("href", None):
                    item_dict["link"] = ent.attrib.get("href", None)
                if ent.tag == "link" and ent.attrib.get("title", None) in ["doi", "pdf"]:
                    item_dict[ent.attrib["title"]] = ent.attrib.get("href", None)

            # print("\n##########################\n")
            item_dict["author"] = ", ".join(authors)
            data.append(item_dict)
    # print(data)

    return data