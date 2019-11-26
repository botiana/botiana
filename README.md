# botiana
botiana is a bot for slack. She does things. 

## Slack Configuration
Follow [these directions](https://slack.com/help/articles/115005265703-create-a-bot-for-your-workspace) from slack. Be sure to configure a default icon.

## Getting started
Botiana is intended to run in a container. But, make your own choice, this isn't Soviet Russia.
Commits should be emojified using https://gitmoji.carloscuesta.me/ 

### Install requirements
Botiana is currently developed and testing using python 3.7
`pip install -r requirements.txt`

### Settings
The settings file has a few defaults you may need to customize. 
 - You may set your token here, or via the environment
 - If you insist, you can change the bot's name, or set it via the environment
 - Set your desired level of logs
 - Set the maximum input length for translations
 - Configure the commands you wish to enable from legacy_modules
 
Several other items can be configured by setting environment variables:
 - 'icon_poolball' uri for eight_ball command
 - 'icon_wiki'     uri for wiki command

more are available, consult legacy_modules.py.

#### Data
Botiana loads local data from a yaml file: data/data.yaml

#### Keywords & Reactions
Keywords, responses and reactions can occur in specific channels, or all channels. Configure this in the data.yaml file.

#### Systems Administrator Dictionary
Local dictionary entries can be created for lookup. Configure this in the data.yaml file.

### Build
`docker build . -t botiana`

### Local testing
Get your token from the slack api and export it as shown and run with docker.
```
export token="xoxb-11111111111-111111111111-aaa1aAAAAAaaaAAaAAAAaa1a"
docker build . -t botiana;docker run  -e token=$token botiana
```
