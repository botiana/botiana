#!/usr/bin/python3
# Python 3, dev on debian 9, intending to run in alpine / python official image

import threading
import time
import sys
import yaml
import re
from slackclient import SlackClient
from common import logger
from message_router import message_router
from keywords import keywords


# Modules
class Variables:
    def __init__(self):
        self.token = token
        self.current_time = 0
        self.keyword_count = {'random': 0, 'current': 0}
        stream_data = open('data/data.yaml', 'r')
        self.yamldata = yaml.load(stream_data, Loader=yaml.FullLoader)
        stream_data.close()


class BotMain(threading.Thread):
    def __init__(self, variables):
        threading.Thread.__init__(self)
        self.daemon = True
        self.variables = variables
        self.should_run = True

    def die(self):
        self.should_run = False
        logger("warn", "exception caught shutting bot thread")

    def run(self):
        self.variables.sc = SlackClient(token)
        logger('crit', BOT_NAME + " Connected!")
        if self.variables.sc.rtm_connect():
            bot_mention = "<@{}".format(self.variables.sc.server.login_data["self"]["id"])
            while self.should_run:
                for evt in self.variables.sc.rtm_read():
                    # Original Command Parsing
                    if "type" in evt and evt["type"] == "message" and "text" in evt:

                        # This allows replies in the threads. Current issue is picture shows up
                        # as bot shadow in threaded conversation summary
                        if "thread_ts" not in evt:
                            evt.update({'thread_ts': ''})

                        # This seems like the right place to snoop
                        count = keywords(self.variables.sc, evt, self.variables.yamldata,
                                         self.variables.keyword_count)
                        self.variables.count = count

                        message = evt["text"].strip()

                        # This logic was used for misdirection. IT allows you to send a message
                        # starting with a channel name to have botiana deliver it there. Clever.
                        channel = ''
                        command = ''
                        if "channel" in evt and evt["type"] == "message" and evt["channel"].startswith("D"):
                            try:
                                _, channel, command, message = message.split(None, 3)
                            except ValueError:
                                try:
                                    _, channel, command = message.split(None, 2)
                                except ValueError:
                                    pass
                            if channel.startswith("<#C"):
                                logger('warn', 'misdirection module invoked')
                                misdirected_channel = str(re.findall(r'\w+', channel)[0])
                                evt["channel"] = misdirected_channel
                                message = bot_mention + "> " + command + " " + message

                        if message.startswith(bot_mention):
                            try:
                                # have a botname, command, and message?
                                _, command, message = message.split(None, 2)
                                message_router(self.variables, bot_mention, evt, command, message)
                            except ValueError:
                                try:
                                    # maybe just a botname and command?
                                    _, command = message.split(None, 1)
                                    message_router(self.variables, bot_mention, evt, command, '')
                                except ValueError:
                                    # this should never happen....
                                    logger('info', "value error in command parsing - this should \
                                                   never happen")
                        elif bot_mention in message:
                            if enable_message_processing is True:
                                try:
                                    logger('info', "routing message to message_processing")
                                    message_router(self.variables, bot_mention, evt,
                                                   message_processing_module, message)
                                except ValueError:
                                    logger('info', "failed to send message to message_processing module")

                self.variables.current_time = time.time()
                time.sleep(.1)
        else:
            if self.variables.sc.server.login_data is None:
                logger('crit', "Connection failed. Probably a bad/missing token.")
            else:
                logger('crit', "Connection failed. Server response: {}".format(
                    self.variables.sc.server.login_data["ok"]))


if __name__ == '__main__':
    "print start"
    try:
        from settings import *
    except ImportError:
        logger('crit', "Could not find settings.py or there was an error loading it.")
        sys.exit(1)
    info = Variables()
    botiana = BotMain(info)
    while botiana.run():
        try:
            time.sleep(0.5)
        except KeyboardInterrupt:
            logger('crit', "caught exception")
            botiana.die()
            sys.exit()
