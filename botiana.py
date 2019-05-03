#!/usr/bin/python
# tested on debian 8.5, you need python-pip to install the following modules:
# pyyaml, bs4, slackclient, translate

import threading,time,sys,os,signal,random,re,requests,yaml,calendar,wikipedia
import calendar
from bs4 import BeautifulSoup, FeatureNotFound
from slackclient import SlackClient
from translate import Translator
from yahoo_finance import Share
from random import randint

## Modules
class variables():
    def __init__(self):
        self.token    = token
        self.yamldata = yaml.load(os.environ['sa_dict'].decode('base64'))
        self.hotkeys  = yaml.load(os.environ['keywords'].decode('base64'))
        self.incmgt   = yaml.load(os.environ['incmgt'].decode('base64'))
        self.current_time = 0

        #Incident Management Stuff
        self.id_start      = False
        self.id_title      = ""
        self.id_rndtm      = 0
        self.id_stint      = 0
        self.id_chan       = ""
        self.id_comms      = False
        self.id_comms_user = ""
        self.id_comms_anny = 0

class incident_management(threading.Thread):
    def __init__(self, info):
        threading.Thread.__init__(self)
        self.daemon = True
        self.info = info
        self.should_run = True

    def die(self):
        self.should_run = False
        print "exception caught shutting down incident management thread"

    def run(self):
        def __send_response(text, userpic, username):
            self.info.sc.api_call('chat.postMessage',
                        username=username,
                        icon_url=userpic,
                        as_user='false',
                        channel=self.info.id_chan,
                        text=text)

        def __channel_id(channel):
            self.info.sc.api_call('channels.info',
                        token=token,
                        channel=channel,
                        include_locale="true")

        while self.should_run:
            if self.info.id_start == True:
                if self.info.id_stint       == 0:
                    self.info.id_rndtm      = (self.info.current_time + 5)
                    self.info.id_stint      = 1
                if self.info.current_time > self.info.id_rndtm:
                    user = random.choice(self.info.incmgt["names"])
                    uid, icon = zip(*user.items())
                    __send_response(random.choice(self.info.incmgt["remarks"]), icon[0], uid[0])
                    random_time = randint(15, 120)
                    self.info.id_rndtm = (int(self.info.current_time) + random_time)
                if self.info.id_comms == True:
                    if self.info.current_time > self.info.id_comms_anny:
                        __send_response(random.choice(self.info.incmgt["annoy"]).format(self.info.id_comms_user, random_time), icon_ru, "botiana")
                        random_time = randint(15, 120)
                        self.info.id_comms_anny = (int(self.info.current_time) + random_time)
            time.sleep(0.1)

class bot_main(threading.Thread):
    def __init__(self, info):
        threading.Thread.__init__(self)
        self.daemon = True
        self.info = info
        self.should_run = True

    def die(self):
        self.should_run = False
        print "exception caught shutting down bot_main thread"

    def run(self):
        ## for now
        sword = 0
        rndword = 3

        ### Slack Commands
        def __send_response(text, icon_url='ru', emoji='null'):
            if "emoji" in icon_url:
                self.info.sc.api_call('chat.postMessage',
                            username=BOT_NAME,
                            icon_emoji=emoji,
                            as_user='false',
                            channel=evt["channel"],
                            text=text)
            else:
                self.info.sc.api_call('chat.postMessage',
                            username=BOT_NAME,
                            icon_url=icon_url,
                            as_user='false',
                            channel=evt["channel"],
                            text=text)

        def __new_topic(new_topic, channel):
            if channel.startswith("G"):
                self.info.sc.api_call('groups.setTopic',
                            token=token,
                            channel=channel,
                            topic=new_topic)
            else:
                self.info.sc.api_call('channels.setTopic',
                            token=token,
                            channel=channel,
                            topic=new_topic)

        def __channel_id(channel):
            data = self.info.sc.api_call('channels.info',
                               token=token,
                               channel=channel,
                               include_locale="true")
            return "#"+data["channel"]["name_normalized"]

        ### Botiana Modules / Commands
        def eight_ball(message):
            answers = [
                      "It is certain.",
                      "Outlook good.",
                      "You may rely on it.",
                      "Ask again later.",
                      "Concentrate and ask again.",
                      "Reply hazy, try again.",
                      "My reply is no.",
                      "My sources say no.",
                      ]
            __send_response(random.choice(answers), icon_poolball)

        def roll(message):
            operations = {
             'coinflip': randint(1, 2),
             'd2': randint(1, 2),
             'd3': randint(1, 3),
             'd4': randint(1, 4),
             'd6': randint(1, 6),
             'd8': randint(1, 8),
             'd12': randint(1, 12),
             'd20': randint(1, 20),
             'd100': randint(1, 100),
            }
            __send_response(
                operations.get(message.lower(), 'subcommand {} not found, commands are: {}'.format(message, str(sorted(operations.keys())))), icon_gw
            )


        def stock(message):
            ticker = Share(message)
            ticker.refresh()
            quote = ticker.get_price()
            if quote is None:
                resp = str(message) + " is not a valid ticker symbol"
            else:
                change = ticker.get_change()
                resp = message + ": " + quote + " " + change
            __send_response(resp, icon_money)
            quote = ""

        def wiki(message):
            try:
                summary = wikipedia.summary(message)
                __send_response("```" + summary + "```", icon_wiki)
            except wikipedia.exceptions.PageError:
                __send_response(message + " is not a valid article. Try again", icon_wiki)
            except wikipedia.exceptions.DisambiguationError as e:
                __send_response(str(e), icon_wiki)
            except wikipedia.exceptions.WikipediaException:
                __send_response("Generic Wikipedia Error. Maybe you should have dontated to them when Jimmy asked the first time.", icon_wiki)

        ## Defines
        def define(message, alternate_definition_index=0, ud_results_per_page=7):
            if message in self.info.yamldata["words"]:
                sa_def = __sa_dictionary(str(message))
                resp = '<@{}> The Sys Admin dictionary defines `{}` as \n>>>{}'.format(
                                                        evt["user"], message, sa_def)
                __send_response(resp, icon_tux)
            else:
                payload = {'term': message}
                definition_index = alternate_definition_index
                if alternate_definition_index >= ud_results_per_page:
                    payload['page'] = (alternate_definition_index
                                       // ud_results_per_page) + 1
                    definition_index %= ud_results_per_page
                r = requests.get(
                    "http://www.urbandictionary.com/define.php", params=payload)
                try:
                     soup = BeautifulSoup(r.content, "lxml")
                except FeatureNotFound:
                     soup = BeautifulSoup(r.content, "html.parser", from_encoding='utf-8')
                definitions = soup.findAll("div", attrs={"class": "meaning"})
                try:
                     ud_def = definitions[definition_index].text.encode(
                          'utf8', 'replace').strip()
                     resp = '<@{}> Urban Dictionary defines `{}` as ```{}```'.format(
                          evt["user"], message, ud_def)
                except IndexError:
                     resp = '<@{}> Urban Dictionary doesn\'t have `{}` definitions for `{}`...'.format(
                     evt["user"], alternate_definition_index + 1, message)
                __send_response(resp, icon_urban_dictionary)

        ## SA Dictionary
        def __sa_dictionary(message):
            blob = ""

            if message in self.info.yamldata["words"]:
                blob = blob + "*pronunciation:* _/" + self.info.yamldata["words"][message][
                               "pronunciation"] + "/_\n"

            for lookup in ('definition', 'usage', 'symptoms', 'synonyms'):
                try:
                    if isinstance([self.info.yamldata["words"][message][lookup]], list):
                        blob = blob + "\n*" + lookup + "*\n\n"
                        for item in self.info.yamldata["words"][message][lookup]:
                            i = self.info.yamldata["words"][message][lookup][item]
                            n = str(item)
                            if lookup == 'synonyms':
                                ele = self.info.yamldata["words"][message][lookup].keys()[-1]
                                if i == self.info.yamldata["words"][message][lookup][ele]:
                                    blob = blob + "  " + i
                                else:
                                    blob = blob + "  " + i + ","
                            else:
                                blob = blob + "  " + n + ". " + i + "\n"
                except KeyError:
                    pass
            return blob
        ##

        ## Meme
        def memelist(message):
            r = requests.get(
                "http://bradme.me/api/templates")
            __send_response("\n".join(
                    sorted(["{}: {}".format(k, v.split('/')[-1]) for k,v in r.json().iteritems() if k and v])
                )
            )

        def meme(message):
            if message == "null":
                message = ""
            if message.lower() == "list":
                memelist()
                return
            r = r"(?P<template>\w+)?(\s+(?P<text>.+))?"
            template, top_text, bottom_text = "kermit", "you should provide valid input", "but that's none of my business"
            import re
            m = re.match(r, message.lower())
            if m:
                print (m.groups())
                if m.group('template'):
                    template = m.group('template')
                if m.group('text'):
                    top_text, bottom_text = str(m.group('text') + '|||').split('|', 2)[:2]
            template, top_text, bottom_text = tuple(
                s.strip().
                 replace("-", "--").
                 replace("_", "__").
                 replace(" ", "-").
                 replace("?", "~q").
                 replace("%", "~p").
                 replace("#", "~h").
                 replace("/", "~s").
                 replace('\xe2\x80\x99', "'").
                 replace("''", '"').
                 replace("'", '%27') for s in (template, top_text, bottom_text))
            __send_response("https://bradme.me/{}/{}/{}.jpg".format(template, top_text, bottom_text), icon_bcat)

        # Universal Translator
        def __trans(flag, lang, message):
            try:
                if len(message) > MAX_TRANSLATE_LENGTH:
                    resp = "Don't be a dick <@{}>".format(evt["user"])
                    __send_response(resp, icon_ru)
                elif bot_mention in message:
                    __send_response(msg_noop, icon_ru)
                else:
                  if len(lang) > 2 and lang.find('|')!=-1:
                      from_lang = lang.split("|")[0]
                      to_lang = lang.split("|")[1]
                      if len(from_lang) > 2 or len(to_lang) > 2:
                          __send_response(msg_noop, "emoji", ":flag-ru:")
                      else:
                        try:
                          translator = Translator(to_lang=to_lang, from_lang=from_lang)
                          if from_lang == "en":
                              flag = ":flag-us:"
                          else:
                              flag = ":flag-" + from_lang + ":"
                          l = translator.translate(message)
                          __send_response(l, "emoji", flag)
                        except TypeError:
                          resp = 'hey <@{}>... {} don\'t speak that language.'.format(evt["user"],BOT_NAME)
                          __send_response(resp, icon_ru)
                  elif len(lang) > 2:
                      __send_response(msg_noop, "emoji", ":flag-ru:")
                  else:
                    try:
                      translator = Translator(to_lang=lang)
                      l = translator.translate(message)
                      __send_response(l, "emoji", ":earth_americas:")
                    except TypeError:
                        angry()
            except ValueError:
                resp = 'Vhy try to anger {} <@{}>?'.format(BOT_NAME, evt["user"])
                __send_response(resp, icon_ru)

        def magyar(message):
            __trans(":flag-hu:", "hu", message)

        def russian(message):
            __trans(":flag-ru:", "ru", message)

        def unitr(command, message):
            _, lang = command.split("tr:")
            __trans(":flag-{}:".format(lang), lang, message)

        def help(message):
            resp = "commands <@botiana> will respond to:\n define <string>\n    ask botiana to look up something in the urban dictionary, or the old SA dictionary\n<tr\:from_lang|to_lang> <string> \n    ask botiana to translate something\n8ball <string>  \n    ask the magic 8 ball a question\nstock <ticker symbol>\n    get the current stock price from yahoo for <ticker symbol>\nmagic\n    send the magic gif\n wiki <string>\n    ask botiana to return a summary from wikipedia\nmemelist \n    giant wall of text listing meme commands\nmeme <meme command> <top string> | <bottom string>\n    the finest memes in all the land, powered by bradme.me\nroll <command>\n    commands are: ['coinflip', 'd100', 'd12', 'd2', 'd20', 'd3', 'd4', 'd6', 'd8']"
            __send_response(resp, icon_ru)

        def angry():
            __send_response(msg_angry,"emoji",":angry:")

        ## End of Botiana Modules

        ## Main Loop
        self.info.sc = SlackClient(token)
        if self.info.sc.rtm_connect():
            bot_mention = "<@{}".format(self.info.sc.server.login_data["self"]["id"])
            while self.should_run:
                for evt in self.info.sc.rtm_read():
                   if "type" in evt and evt["type"] == "message" and "text" in evt:
                       message = evt["text"].encode('utf8', 'replace').strip()
                       if "channel" in evt and evt["type"] == "message" and evt["channel"].startswith("D"):
                           #allow dm's to botiana for activity in public rooms. 
                           if message.startswith("<#C"):
                               garble_channel,message = message.split(None, 1)
                               channel = str(re.findall('#(.*?)\|', garble_channel)[0])
                               evt["channel"]=channel
                               message = "<@{}".format(self.info.sc.server.login_data["self"]["id"]) + "> " + message
                       if message.startswith(bot_mention):
                           try:
                               # have a botname, command, and message?
                               _, command, message = message.split(None, 2)
                           except ValueError:
                               try:
                                   # maybe just a botname and command?
                                   _, command = message.split(None, 1)
                                   message = "null"
                               except ValueError:
                                   # this should never happen....
                                   command = ""
                           if command.startswith('__'):
                               angry()
                           elif command.startswith('tr:'):
                               unitr(command, message)
                           elif command == "8ball":
                               eight_ball(message)
                           elif command == "stock":
                               stock(message)
                           elif command == "wiki":
                               wiki(message)
                           elif command == "magic":
                               __send_response("http://www.reactiongifs.com/r/mgc.gif", icon_magic)
                           elif command == "502":
                               __send_response(icon_502, icon_502)
                           elif command == "meme":
                               meme(message)
                           elif command == "memelist":
                               memelist(command)
                           elif command == "russian":
                               russian(message)
                           elif command == "magyar":
                               magyar(message)
                           elif command == "help":
                               help(message)
                           elif command == "roll":
                               roll(message)
                           elif command == "incident":
                               if message.startswith("start"):
                                   try:
                                       action, string  = message.split(None, 1)
                                   except ValueError:
                                       action = ""
                                       __send_response("Please give a discription of the event you with to start.", icon_ru)
                               elif message.startswith("clear"):
                                   action = "clear"
                               elif message.startswith("comms"):
                                   action = ""
                                   if self.info.id_start == True:
                                       if self.info.id_comms_user  == "":
                                           if evt["channel"] == self.info.id_chan:
                                               self.info.id_comms      = True
                                               self.info.id_comms_user = evt["user"]
                                               self.info.id_comms_anny = (self.info.current_time + 60)
                                               __send_response("<@{}> has been assigned comms".format(evt["user"]) + " for incident `" + self.info.id_title + "`", icon_ru)
                                           else: 
                                               __send_response("<@{}> The incident is happening in <#{}>. Please go there to take comms.".format(evt["user"], self.info.id_chan), icon_ru)
                                       else:
                                           __send_response("<@{}> has been already been assigned comms".format(evt["user"]) + " for incident `" + self.info.id_title + "`", icon_ru)
                               if action == "start":
                                   if self.info.id_start == True:
                                       __send_response('Incident `{}` is already in progress in channel <#{}>'.format(self.info.id_title, self.info.id_chan), icon_ru)
                                   else:
                                       self.info.id_start = True
                                       self.info.id_title = string
                                       __new_topic(string, evt["channel"])
                                       __send_response("Starting incident " + self.info.id_title, icon_ru)
                                       self.info.id_chan = evt["channel"]
                               elif action == "clear":
                                   if self.info.id_stint == 0:
                                       __send_response("There is no incident to clear.", icon_ru)
                                   else:
                                       if evt["channel"] == self.info.id_chan:
                                           self.info.id_start      = False
                                           self.info.id_stint      = 0
                                           self.info.id_comms_user = ""
                                           self.info.id_comms      = False
                                           __send_response("Clearing incident " + self.info.id_title, icon_ru)
                                           __new_topic("Nothing rotten in Denmark", evt["channel"])
                                       else:
                                           channel_name = __channel_id(self.info.id_chan)
                                           __send_response("Incident `{}` must be cleared from channel `{}`".format(self.info.id_title, channel_name), icon_ru)

                           elif command == "define":
                               parsed_message = message.split('alt:', 1)
                               alternate_definition = 0
                               if len(parsed_message) > 1:
                                   try:
                                       alternate_definition = abs(
                                       int(parsed_message[1]))
                                   except ValueError:
                                       pass
                               define(parsed_message[0].strip(),
                                      alternate_definition)
                           elif command == "tot":
                               print "Bye!"
                               __send_response("byE!", icon_ru)
                               sys.exit(0)
                           else:
                               try:
                                  # http://stackoverflow.com/a/16683842/436190
                                  # stop the madness
                                  if command in cmnds:
                                      args_dict = {'message': message}
                                      globals()[command](**args_dict)
                                  else:
                                      k
                                      print "angry 1"
                                      angry()
                               except:
                                   if command == "set":
                                       # do nothing, topic has been set
                                       print ""
                                   else:
                                       print "angry 2"
                                       angry()

                       if "channel" in evt and evt["type"] == "message":
                          msgary = message.split(' ')
                          for k in msgary:
                             if k in self.info.hotkeys["keywords"]:
                                 if sword > rndword:
                                     if self.info.hotkeys["keywords"][k]["watch"] != "all":
                                         if self.info.hotkeys["keywords"][k]["watch"] == evt["channel"]:
                                             if self.infohotkeys["keywords"][k]["type"] in "phrase":
                                                 rndword = randint(1,7)
                                                 sword = 0
                                                 __send_response(random.choice(self.info.hotkeys["keywords"][k]["phrases"]), self.info.hotkeys["keywords"][k]["icon"])
                                             if self.info.hotkeys["keywords"][k]["type"] == "url":
                                                 rndword = randint(1,7)
                                                 sword = 0
                                                 __send_response(self.info.hotkeys["keywords"][k]["url"], self.info.hotkeys["keywords"][k]["icon"])
                                     else:
                                         if self.info.hotkeys["keywords"][k]["type"] in "phrase":
                                             rndword = randint(1,7)
                                             sword = 0
                                             __send_response(random.choice(self.info.hotkeys["keywords"][k]["phrases"]), self.info.hotkeys["keywords"][k]["icon"])
                                         if self.info.hotkeys["keywords"][k]["type"] == "url":
                                             rndword = randint(1,7)
                                             sword = 0
                                             __send_response(self.info.hotkeys["keywords"][k]["url"], self.info.hotkeys["keywords"][k]["icon"])
                                 sword = (sword + 1)
                self.info.current_time = time.time()
                time.sleep(.1)
        else:
            if self.info.sc.server.login_data is None:
                print ("Connection failed. Probably a bad/missing token.")
            else:
                print ("Connection failed. Server response: {}".format(
                self.info.sc.server.login_data["ok"]))

if __name__== '__main__':
    "print start"
    try:
        from settings import *
    except ImportError:
        print ("Could not find settings.py or there was an error loading it.")
        sys.exit(1)
    info=variables()
    botiana=bot_main(info)
    idbot=incident_management(info)
    idbot.start()
    while botiana.run():
        try:
             time.sleep(0.1)
        except KeyboardInterrupt:
             print "caught exception"
             botiana.die()
             sys.exit()
