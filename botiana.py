#!/usr/bin/env python
# coding=utf-8

# tested on debian 8.5, you need python-pip to install the following modules:
# pyyaml, bs4, slackclient, translate

import random
import sys
import time
import os
import re
import requests
import yaml
from bs4 import BeautifulSoup, FeatureNotFound
from slackclient import SlackClient
from translate import Translator
from yahoo_finance import Share
import wikipedia
from random import randint

# load config
try:
    from settings import *
except ImportError:
    print ("Could not find settings.py or there was an error loading it.")
    sys.exit(1)

# load yaml file(s) 
def yaml_loader(filepath):
    with open(filepath, "r") as file_descriptor:
        data = yaml.load(file_descriptor)
    return data

def __send_response(text, icon_url='ru', emoji='null'):
    if "emoji" in icon_url:
      sc.api_call('chat.postMessage',
                  username=BOT_NAME,
                  icon_emoji=emoji,
                  as_user='false',
                  channel=evt["channel"],
                  text=text)
    else:
      sc.api_call('chat.postMessage',
                  username=BOT_NAME,
                  icon_url=icon_url,
                  as_user='false',
                  channel=evt["channel"],
                  text=text)

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

# Magic 8 Ball function
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

# Sysadmin Dictionary function
def __sa_dictionary(message):
    blob = ""

    if message in yamldata["words"]:
        blob = blob + "*pronunciation:* _/" + yamldata["words"][message][
            "pronunciation"] + "/_\n"

        for lookup in ('definition', 'usage', 'symptoms', 'synonyms'):
            try:
                if isinstance([yamldata["words"][message][lookup]], list):
                    blob = blob + "\n*" + lookup + "*\n\n"
                    for item in yamldata["words"][message][lookup]:
                        i = yamldata["words"][message][lookup][item]
                        n = str(item)
                        if lookup == 'synonyms':
                            ele = yamldata["words"][message][lookup].keys()[-1]
                            if i == yamldata["words"][message][lookup][ele]:
                                blob = blob + "  " + i
                            else:
                                blob = blob + "  " + i + ","
                        else:
                            blob = blob + "  " + n + ". " + i + "\n"
            except KeyError:
                pass
    return blob

# define function
def define(message, alternate_definition_index=0, ud_results_per_page=7):
    if message in yamldata["words"]:
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

def angry():
    __send_response(msg_angry,"emoji",":angry:")

def help(message):
    resp = "commands <@botiana> will respond to:\n define <string>\n    ask botiana to look up something in the urban dictionary, or the old SA dictionary\n<tr\:from_lang|to_lang> <string> \n    ask botiana to translate something\n8ball <string>  \n    ask the magic 8 ball a question\nstock <ticker symbol>\n    get the current stock price from yahoo for <ticker symbol>\nmagic\n    send the magic gif\n wiki <string>\n    ask botiana to return a summary from wikipedia\nmemelist \n    giant wall of text listing meme commands\nmeme <meme command> <top string> | <bottom string>\n    the finest memes in all the land, powered by bradme.me\nroll <command>\n    commands are: ['coinflip', 'd100', 'd12', 'd2', 'd20', 'd3', 'd4', 'd6', 'd8']"
    __send_response(resp, icon_ru)

# Main program, slack client.
yamldata = yaml_loader("sa.yaml")
hotkeys  = yaml_loader("keywords.yaml")
sc = SlackClient(token)
try:
    if sc.rtm_connect():
        bot_mention = "<@{}".format(sc.server.login_data["self"]["id"])
        while True:
            for evt in sc.rtm_read():
                if "type" in evt and evt["type"] == "message" and "text" in evt:
                    message = evt["text"].encode('utf8', 'replace').strip()
                    if "channel" in evt and evt["type"] == "message" and evt["channel"].startswith("D"):
                      #allow dm's to botiana for activity in public rooms. 
                      if message.startswith("<#C"):
                        garble_channel,message = message.split(None, 1)
                        channel = str(re.findall('#(.*?)\|', garble_channel)[0])
                        evt["channel"]=channel
                        message = "<@{}".format(sc.server.login_data["self"]["id"]) + "> " + message
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
                        elif command == "magic":
                            __send_response("http://www.reactiongifs.com/r/mgc.gif", icon_magic)
                        elif command == "502":
                            __send_response(icon_502, icon_502)
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
                                  angry()
                            except:
                                angry()
                    if "channel" in evt and evt["type"] == "message":
                        if message in hotkeys["keywords"]:
                             if sword > rndword:
                                 if hotkeys["keywords"][message]["watch"] != "all":
                                     if hotkeys["keywords"][message]["watch"] == evt["channel"]:
                                         if hotkeys["keywords"][message]["type"] == "phrase":
                                             rndword = randint(1,7)
                                             sword = 0
                                             __send_response(random.choice(hotkeys["keywords"][message]["phrases"]), hotkeys["keywords"][message]["icon"])
                                         if hotkeys["keywords"][message]["type"] == "url":
                                             rndword = randint(1,7)
                                             sword = 0
                                             __send_response(hotkeys["keywords"][message]["url"], hotkeys["keywords"][message]["icon"])
                                 else:
                                     if hotkeys["keywords"][message]["type"] == "phrase":
                                         rndword = randint(1,7)
                                         sword = 0
                                         __send_response(random.choice(hotkeys["keywords"][message]["phrases"]), hotkeys["keywords"][message]["icon"])
                                     if hotkeys["keywords"][message]["type"] == "url":
                                         rndword = randint(1,7)
                                         sword = 0
                                         __send_response(hotkeys["keywords"][message]["url"], hotkeys["keywords"][message]["icon"])
                             sword = (sword + 1)  
            time.sleep(.1)
    else:
        if sc.server.login_data is None:
            print ("Connection failed. Probably a bad/missing token.")
        else:
            print ("Connection failed. Server response: {}".format(
                sc.server.login_data["ok"]))
except KeyboardInterrupt:
    sys.exit()
