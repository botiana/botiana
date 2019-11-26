#!/usr/local/bin/python3


import sys
from common import logger
from settings import *
from slack_commands import __send_message
# We use dynamic dispatch do execute modules, next line prevents ugliness in pycharm
# noinspection PyUnresolvedReferences
from legacy_modules import eight_ball, wiki, define, memelist, meme, __trans, rtfm


def message_router(variables, botname, evt, command, message):
    if "type" in evt and evt["type"] == "message" and "text" in evt:
        # Channel/Group Invites
        # Slack does something along the lines of "@bot has been added to channel"
        # Botiana thinks is a command, but it's not really. We will process as such
        # just to keep things nice and clean.
        if "subtype" in evt.keys():
            if evt["subtype"] == "channel_join":
                message = botname + " channel_join"
                logger('warn', 'channel_join event')
            elif evt["subtype"] == "group_join":
                message = botname + " group_join"
                logger('warn', 'group_join event')

        # Build variable Dict
        messagedetails = {
            'command': command,
            'message': message,
            'channel': evt["channel"],
            'ts': evt["ts"],
            'thread_ts': evt["thread_ts"],
            'caller':  evt["user"]
        }

        # Command Parsing logic. This is mostly for the older modules, translate and incident_management
        # Get their own methods, because I'm lazy.
        if command.startswith('__'):
            logger('warn', "ERROR: command starts with __")
        elif command == "set":
            logger('warn', "set command sent")
        elif command == "tot":
            logger('crit', "Killed by human")
            sys.exit(0)
        else:
            if command in cmnds:
                # http://stackoverflow.com/a/16683842/436190
                # stop the madness
                globals()[command](variables, messagedetails)
            elif command.startswith("tr:"):
                command, request = command.split(':')
                __trans(variables, messagedetails, flag="flag-" + request, lang=request)
            elif command.startswith("channel_join"):
                __send_message(variables.sc, "Just like the Crimea! You can not keep me out, you capitalist pigs!",
                               evt["channel"], "", icon_default)
            elif command.startswith("group_join"):
                __send_message(variables.sc, "You are all parasites and loafers that stop others from working!",
                               evt["channel"], "", icon_default)
            else:
                logger('info', "I have been tasked with an invalid command.")
