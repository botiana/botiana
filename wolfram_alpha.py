#!/usr/local/bin/python3

from common import logger, custom_icon
from settings import *
from slack_commands import __send_message, __send_ephemeral, __impersonator, __user_id, __send_snippet

if wa_token:
   import wolframalpha
   client = wolframalpha.Client(wa_token)

def wolf(variables, msgdict):

    if wa_token:
        bot_mention = "<@{}".format(variables.sc.server.login_data["self"]["id"]) + ">"
        # if the botname is in the message, remove it. This only confuses wolfram
        message = msgdict["message"].replace(bot_mention, '')
        logger('info', "searching wolfram alpha for " + message)
        res = client.query(message)

        try:
            print (next(res.results).text)
            __send_message(variables.sc, next(res.results).text, msgdict["channel"], 
                           msgdict["thread_ts"], custom_icon("icon_default"))
            logger('info', "wolfram alpha result")
        

        except Exception:
            logger('info', "wolfram alpha exception!")
            try:
                for pod in res.pods:
                    print(pod["@title"])
                    print("")

            except Exception:
                logger('info', "wolfram alpha oh fuck that didn't work!")
