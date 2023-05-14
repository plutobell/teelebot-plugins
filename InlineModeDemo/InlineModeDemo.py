# -*- coding:utf-8 -*-
'''
creation time: 2021-09-09
last_modification: 2023-05-12
'''

def InlineModeDemo(bot, message):

    prefix = ""
    ok, metadata = bot.metadata.read()
    if ok:
        prefix = metadata.get("Command", "")

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
