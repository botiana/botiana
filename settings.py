# coding=utf-8
import os

# slack token
token = os.environ["token"]

BOT_NAME = os.getenv('botname', 'botiana')

# Levels: crit, warn, info
LOG_LEVEL = 'crit'

# max string length for translation
MAX_TRANSLATE_LENGTH = 250

# enabled commands
cmnds = ['eight_ball', 'define', 'wiki', 'memelist', 'meme', 'rtfm']

# bot avatar
icon_default = ('https://upload.wikimedia.org/wikipedia/' +
                'commons/thumb/7/7e/Hammer_and_sickle.svg/1024px-Hammer_and_sickle.svg.png')
