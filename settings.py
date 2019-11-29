# coding=utf-8
import os

# slack token
token = os.environ["token"]

BOT_NAME = os.getenv('botname', 'botiana')

# Levels: crit, warn, info
LOG_LEVEL = os.getenv('log_level', 'crit')

# max string length for translation
MAX_TRANSLATE_LENGTH = 250

# enabled commands
commands = ['eight_ball', 'define', 'wiki', 'memelist', 'meme', 'rtfm', 'wolf']

# enabled local commands
local_commands = []

wa_token = os.getenv('wa_token', '')

# bot avatar
icon_default = ('https://upload.wikimedia.org/wikipedia/' +
                'commons/thumb/7/7e/Hammer_and_sickle.svg/1024px-Hammer_and_sickle.svg.png')
