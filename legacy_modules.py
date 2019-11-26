#!/usr/local/bin/python

import random
import requests
import wikipedia
import json
import re
from bs4 import BeautifulSoup
from translate import Translator
from pyowm import OWM
from settings import *
from common import logger, custom_icon
from slack_commands import __send_message, __send_ephemeral, __impersonator, __user_id


def eight_ball(variables, msgdict):
    if msgdict["message"]:
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
        __send_message(variables.sc, random.choice(answers), msgdict["channel"], msgdict["thread_ts"],
                        custom_icon("icon_poolball"))
    else:
        __send_message(variables.sc, "this works better when you ask the magic eight ball a question. Just say'n",
                        msgdict["channel"], msgdict["thread_ts"], custom_icon("icon_poolball"))


def wiki(variables, msgdict):
    try:
        summary = wikipedia.summary(msgdict["message"])
        __send_message(variables.sc, "```" + summary + "```", msgdict["channel"], msgdict["thread_ts"],
                        custom_icon("icon_wiki"))
    except wikipedia.exceptions.PageError:
        __send_message(variables.sc, msgdict["message"] + " is not a valid article. Try again", msgdict["channel"],
                        msgdict["thread_ts"], custom_icon("icon_wiki"))
    except wikipedia.exceptions.DisambiguationError as e:
        __send_message(variables.sc, str(e), msgdict["channel"], msgdict["thread_ts"], custom_icon("icon_wiki"))
    except wikipedia.exceptions.WikipediaException:
        __send_message(variables.sc, "Wikipedia Error. Maybe you should have donated to them when Jimmy asked the " +
                        "first time.", msgdict["channel"], msgdict["thread_ts"], custom_icon("icon_wiki"))


# Defines
def define(variables, msgdict, alternate_definition_index=0, ud_results_per_page=7):

    if msgdict["message"] in variables.yamldata["words"]:
        sa_def = __sa_dictionary(str(msgdict["message"]), variables.yamldata)
        resp = '<@{}> The Sys Admin dictionary defines `{}` as \n>>>{}'.format(
                                                msgdict["caller"], msgdict["message"], sa_def)
        __send_message(variables.sc, resp, msgdict["channel"], msgdict["thread_ts"], custom_icon("icon_tux"))

    elif msgdict["message"]:
        parsed_message = msgdict["message"].split('alt:', 1)
        if len(parsed_message) > 1:
            try:
                alternate_definition_index = abs(int(parsed_message[1]))
            except ValueError:
                pass
        payload = {'term': parsed_message[0].strip()}

        if alternate_definition_index >= ud_results_per_page:
            payload['page'] = (alternate_definition_index
                               // ud_results_per_page) + 1
            alternate_definition_index %= ud_results_per_page
        r = requests.get(
            "http://www.urbandictionary.com/define.php", params=payload)
        try:
            soup = BeautifulSoup(r.content, "lxml")
        except ValueError:
            soup = "failure"
            logger("warn", "soup failure")
        definitions = soup.findAll("div", attrs={"class": "meaning"})
        try:
            resp = '<@{}> Urban Dictionary defines `{}` as ```{}```'.format(
                msgdict["caller"], parsed_message[0].strip(), definitions[alternate_definition_index].text)
        except IndexError:
            resp = '<@{}> Urban Dictionary doesn\'t have `{}` definitions for `{}`...'.format(
                    msgdict["caller"], alternate_definition_index + 1, parsed_message[0].strip())
        __send_message(variables.sc, resp, msgdict["channel"], msgdict["thread_ts"],
                        custom_icon("icon_urban_dictionary"))
    else:
        __send_message(variables.sc, "what exactly are you asking me to define?", msgdict["channel"],
                        msgdict["thread_ts"], custom_icon("icon_urban_dictionary"))


# SA Dictionary
def __sa_dictionary(message, yamldata):
    blob = ""

    if message in yamldata["words"]:
        try:
            if not isinstance(yamldata["words"][message]["pronunciation"], list):
                blob = blob + "*pronunciation:* _/" + yamldata["words"][message]["pronunciation"] + "/_\n"
        except KeyError:
            logger("warn", "missing pronunciation in dictionary entry for: " + message)
            pass

    for lookup in ('definition', 'usage', 'symptoms', 'synonyms'):
        try:
            if isinstance([yamldata["words"][message][lookup]], list):
                blob = blob + "\n*" + lookup + "*\n\n"
                for item in yamldata["words"][message][lookup]:
                    i = yamldata["words"][message][lookup][item]
                    n = str(item)
                    blob = blob + "  " + n + ". " + i + "\n"
        except KeyError:
            pass
    return blob


# Meme
def memelist(variables, msgdict):
    r = requests.get(
        "http://bradme.me/api/templates")
    json_data = json.loads(r.text)
    itemlist = "\n".join(sorted(["{}: {}".format(k, v.split('/')[-1]) for k, v in json_data.items() if k and v]))
    __send_ephemeral(variables.sc, itemlist, msgdict["channel"], msgdict["caller"])


def meme(variables, msgdict):
    if msgdict["message"].lower() == "list":
        memelist(variables, msgdict)
        return
    r = r"(?P<template>\w+)?(\s+(?P<text>.+))?"
    template, top_text, bottom_text = "kermit", "you should provide valid input", "but that's none of my business"
    m = re.match(r, msgdict["message"].lower())
    if m:
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
    __send_message(variables.sc, "https://bradme.me/{}/{}/{}.jpg".format(template, top_text, bottom_text),
                    msgdict["channel"], msgdict["thread_ts"], custom_icon("icon_bcat"))


# Universal Translator
def __trans(variables, msgdict, flag="flag-ru", lang="ru"):
    bot_mention = "<@{}".format(variables.sc.server.login_data["self"]["id"])
    try:
        # Fail if too much data is sent at the translator
        if len(msgdict["message"]) > MAX_TRANSLATE_LENGTH:
            resp = "Don't be a dick <@{}>".format(msgdict["caller"])
            __send_message(variables.sc, resp, msgdict["channel"], msgdict["thread_ts"],
                            custom_icon("icon_translator"))
        # Botiana can get into and endless loop, so let's discard anything that has her name at the beginning
        elif bot_mention in msgdict["message"]:
            __send_message(variables.sc, "You are a joker, I think you play trick on me, no?",
                            msgdict["channel"], msgdict["thread_ts"], "emoji", ":flag-ru:")
        else:
            # Are we translating from one language to another, syntax `tr:en|de`
            if len(lang) > 2 and lang.find('|') != -1:
                # try from_lang,to_lang = lang.split("|")
                from_lang = lang.split("|")[0]
                to_lang = lang.split("|")[1]
                # this should fail as we are expecting 2 char language codes
                if len(from_lang) > 2 or len(to_lang) > 2:
                    __send_message(variables.sc, "Such a sad story you have for me.", msgdict["channel"],
                                    msgdict["thread_ts"], "emoji", ":flag-ru:")
                else:
                    try:
                        translator = Translator(to_lang=to_lang, from_lang=from_lang)
                        if from_lang == "en":
                            flag = ":flag-us:"
                        else:
                            flag = ":flag-" + from_lang + ":"
                        resp = translator.translate(msgdict["message"])
                        __send_message(variables.sc, resp, msgdict["channel"], msgdict["thread_ts"], "emoji", flag)
                    except TypeError:
                        resp = 'hey <@{}>... {} don\'t speak that language.'.format(msgdict["caller"], BOT_NAME)
                        __send_message(variables.sc, resp, msgdict["channel"], msgdict["thread_ts"],
                                        custom_icon("icon_translator"))
            elif len(lang) > 2:
                __send_message(variables.sc, "sorry, not sorry", msgdict["channel"], msgdict["thread_ts"],
                                "emoji", ":flag-ru:")
            else:
                try:
                    translator = Translator(to_lang=lang)
                    resp = translator.translate(msgdict["message"])
                    __send_message(variables.sc, resp, msgdict["channel"], msgdict["thread_ts"], "emoji", flag)
                except TypeError:
                    __send_message(variables.sc, "Only you could get a robot to refuse a job. Such a pity.",
                                    msgdict["channel"], msgdict["thread_ts"], custom_icon("icon_translator"))
    except ValueError:
        resp = 'Vhy try to anger {} <@{}>?'.format(BOT_NAME, msgdict["caller"])
        __send_message(variables.sc, resp, msgdict["channel"], msgdict["thread_ts"], ":earth_americas:")


def rtfm(variables, msgdict):
    resp = "commands <@botiana> will respond to:\n\n" + \
           " define <string>\n" + \
           "    ask botiana to look up something in the urban dictionary, or the old SA dictionary\n\n" + \
           " tr:<from_lang>|<to_lang> <string> \n" + \
           "    ask botiana to translate something\n\n" + \
           " eight_ball <string>  \n" + \
           "    ask the magic 8 ball a question\n\n" + \
           " wiki <string>\n" + \
           "    ask botiana to return a summary from wikipedia\n\n" + \
           " memelist \n    giant wall of text listing meme commands\n\n" + \
           " meme <meme command> <top string> | <bottom string>\n" + \
           "    the finest memes in all the land, powered by bradme.me\n\n"
    __send_ephemeral(variables.sc, resp, msgdict["channel"], msgdict["caller"])
