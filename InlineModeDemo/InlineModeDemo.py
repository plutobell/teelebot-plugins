# -*- coding:utf-8 -*-
'''
creation time: 2021-09-09
last_modification: 2021-09-11
'''

def InlineModeDemo(bot, message):

    prefix = ""
    with open(bot.path_converter(bot.plugin_dir + "InlineModeDemo/__init__.py"), "r", encoding="utf-8") as init:
        prefix = init.readline()[1:].strip()

    results = [
        {
            "type": "article",
            "id": "item_id_1",
            "title": "teelebot",
            "input_message_content": {
                "message_text": "https://github.com/plutobell/teelebot"
            }
        },
        {
            "type": "article",
            "id": "item_id_2",
            "title": "teelebot-plugins",
            "input_message_content": {
                "message_text": "https://github.com/plutobell/teelebot-plugins"
            }
        },
        {
            "type": "article",
            "id": "item_id_3",
            "title": "your input: " + message["query"][len(prefix):],
            "input_message_content": {
                "message_text": "your input: " + message["query"][len(prefix):]
            }
        }
    ]

    bot.answerInlineQuery(inline_query_id=message["id"],
        results=results)
