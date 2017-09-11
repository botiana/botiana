# coding=utf-8
import os

# slack token
token = os.environ["token"]

BOT_NAME = 'botiana'

# max string length for translation
MAX_TRANSLATE_LENGTH = 250

cmnds = ['define', 'tr', '8ball', 'stock', 'magic', 'wiki', 'meme', 'memelist', 'roll', 'magyar', 'help', 'tot']

# Set inital values for secret dictionary
sword = 0
rndword = 3

# http image links for avatar
icon_ru = os.environ['icon_ru'] 
icon_poolball = os.environ['icon_poolball']
icon_tux = os.environ['icon_tux']
icon_urban_dictionary = os.environ['icon_urban_dictionary']
icon_gw = os.environ['icon_gw']
icon_money = os.environ['icon_money']
icon_magic = os.environ['icon_magic']
icon_wiki = os.environ['icon_wiki']
icon_bcat = os.environ['icon_bcat']
icon_heart = os.environ['icon_heart']
icon_502 = os.environ['icon_502']

# Botiana Responses for conditions
msg_angry = u"Соединительная связь, какая у вас функция"
msg_noop = u"Я не готов выполнить эту задачу"
