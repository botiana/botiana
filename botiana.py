#!/usr/bin/python


# tested on debian 8.5, you need python-pip to install the following modules:
# pyyaml, bs4, slackclient, translate

import time
import  requests
from bs4 import BeautifulSoup
from slackclient import SlackClient
from translate import Translator
import sys
import random
import yaml
import types

# Configurables:

# slack token
token = ""

# max string length for translation
maxLength=250

# http image links for avatar
ru="http://link.to/yourpic.jpg"
poolball="http://link.to/yourpic.jpg"
tux="http://link.to/yourpic.jpg"
ubd="http://link.to/yourpic.jpg"

# load yaml file w/ SA dictionary
def yaml_loader(filepath):
  with open(filepath, "r") as file_descriptor:
    data = yaml.load(file_descriptor)
  return data

# Magic 8 Ball function
def eightBall(word):
  answers = [
    "It is certain",
    "Outlook good",
    "You may rely on it",
    "Ask again later",
    "Concentrate and ask again",
    "Reply hazy, try again",
    "My reply is no",
    "My sources say no",
  ]
  if "8ball" in word:
    sc.api_call('chat.postMessage', 
                 username='botiana', 
                 icon_url=poolball,  
                 as_user='false',
                 channel=evt["channel"], 
                 text=random.choice(answers))

# Sysadmin Dictionary function
def saDictionary(word):

  print("in saDictionary def")
  blob=""

  if word in yamldata["words"]:

    try:
      blob=blob+"*pronunciation:* _/"+yamldata["words"][word]["pronunciation"]+"/_\n"
    except KeyError:
       foo='foobar'

    for lookup in ('definition','usage','symptoms','synonyms'):
      try:
        if isinstance([yamldata["words"][word][lookup]], list):
          blob=blob+"\n*"+lookup+"*\n\n"
          for item in yamldata["words"][word][lookup]:
            i=yamldata["words"][word][lookup][item]
            n=str(item)
            if lookup == 'synonyms':
              ele = yamldata["words"][word][lookup].keys()[-1]
              #els = list(yamldata["words"][word][lookup].items())
              #foo,ele,bar = word.split('\'')
              print(yamldata["words"][word][lookup][ele])
              if i==yamldata["words"][word][lookup][ele]:
                blob=blob+"  "+i
              else:
                blob=blob+"  "+i+","
            else:
              blob=blob+"  "+n+". "+i+"\n"
      except KeyError:
        foo='bar'
  return blob

# define function
def define(word):
  #print("in define function: "+word)
  if "define" in word:
    botName,defReq = word.split("define ")
    if defReq in yamldata["words"]:
      message=saDictionary(str(defReq))
      sc.api_call('chat.postMessage', 
                   username='botiana', 
                   icon_url=tux,  
                   as_user='false', 
                   channel=evt["channel"], 
                   text='<@'+evt["user"]+'> The Sys Admin dictionary defines  `'+defReq+'` as \n>>>'+message)
    else:
      r = requests.get("http://www.urbandictionary.com/define.php?term={}".format(defReq))
      soup = BeautifulSoup(r.content, "lxml")
      udDef = soup.find("div",attrs={"class":"meaning"}).text
      sc.api_call('chat.postMessage', 
                   username='botiana', 
                   icon_url=ubd,  
                   as_user='false', 
                   channel=evt["channel"], 
                   text='<@'+evt["user"]+'> Urban Dictionary defines `'+defReq+'` as ```'+udDef+'```')

# Universal Translator
def trans(flag,lang,word,delim):
  try:
    langNAme,langReq = word.split(delim,1)
    length=len(langReq)
    if ( length > maxLength):
      sc.api_call('chat.postMessage', 
                   username='botiana', 
                   icon_url=flag,  
                   as_user='false', 
                   channel=evt["channel"], 
                   text='Don\'t be a dick <@'+evt["user"]+'>')
    else:
      translator= Translator(to_lang=lang)
      l = translator.translate(langReq)
      sc.api_call('chat.postMessage', 
                   username='botiana', 
                   icon_emoji=flag,
                   as_user='false', 
                   channel=evt["channel"], 
                   text=l)
  except ValueError:
    sc.api_call('chat.postMessage', 
                 username='botiana', 
                 icon_url=flag,
                 as_user='false', 
                 channel=evt["channel"], 
                 text='Vhy try to anger botiana <@'+evt["user"]+'>?')

# unitr function
def unitr(word):
  if "magyar" in word:
    trans(":flag-hu:","hu",word,"magyar ")
  if "russian" in word:
    trans(":flag-ru:","ru",word,"russian ")
  if "tr:" in word:
    tr=word.split()[1]
    if tr.startswith("tr:"):
      ask,lang = tr.split(":")
    trans(":flag-"+lang+":",lang,word,lang+" ")

# help function
def help(word):
  defReq = word.split(" ")
  send='false'
  print(word)
  if "help" in defReq:
    resp='In Soviet Russia <@'+evt["user"]+'> helps <@'+evt["user"]+'>.'
    send='true'
  if "HELP" in defReq:
    resp='VHY YOU YELL AT ME <@'+evt["user"]+'>!'
    send='true'
  if "leave" in defReq:
    resp='I bot. leave you <@'+evt["user"]+'>!'
    send='true'
  if send == 'true':
    sc.api_call('chat.postMessage',
                 username='botiana',
                 icon_url=ru, 
                 as_user='false',
                 channel=evt["channel"],
                 text=resp)

## Main program, slack client.
yamldata = yaml_loader("sa.yaml")
sc = SlackClient(token)
if sc.rtm_connect():
  while True:
    new_evts = sc.rtm_read()
    for evt in new_evts:
      if "type" in evt:
        if evt["type"] == "message" and "text" in evt:    
          message=evt["text"].encode('utf8', 'replace')
          print(message)
          print(evt["channel"])
          if message.startswith("<@U1F0MEFBL"):
            define(message)
            unitr(message)
            eightBall(message)
            help(message)
    time.sleep(1)
else:
    print "Connection Failed, invalid token?"
