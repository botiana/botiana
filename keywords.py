#!/usr/local/bin/python3
# tested on debian 8.5, you need python-pip to install the following modules:
# pyyaml, bs4, slackclient, translate

from random import randint
import random
from slack_commands import __send_message, __reaction


def keywords(sc, evt, yamldata, count):
    if "channel" in evt and evt["type"] == "message" and "bot_id" not in evt:
        message = evt["text"].strip()
        for k in yamldata["keywords"]:
            if k in message.lower():
                # Intent here is not to trigger every time.
                # Increment on times seen, trigger a random recount vault
                # when we deploy a message
                if count["current"] > count["random"]:
                    # Does our entry only apply to a specific channel?
                    print(evt["channel"])
                    if yamldata["keywords"][k]["watch"] == evt["channel"] or yamldata["keywords"][k]["watch"] == 'all':
                        if yamldata["keywords"][k]["type"] in "phrase":
                            count["random"] = randint(1, 7)
                            count["current"] = 0
                            __send_message(sc, random.choice(yamldata["keywords"][k]["phrases"]),
                                           evt["channel"], evt["thread_ts"], yamldata["keywords"][k]["icon"])
                        if yamldata["keywords"][k]["type"] == "url":
                            count["random"] = randint(1, 7)
                            count["current"] = 0
                            __send_message(sc, yamldata["keywords"][k]["url"], evt["channel"],
                                           evt["thread_ts"], yamldata["keywords"][k]["icon"])
                        if yamldata["keywords"][k]["type"] == "emoji":
                            count["random"] = randint(1, 7)
                            count["current"] = 0
                            __reaction(sc, evt["channel"], evt["ts"], yamldata["keywords"][k]["emoji"])
                count["current"] = (count["current"] + 1)
    return count
