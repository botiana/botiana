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
 - Configure the commands you wish to enable from legacy_modules
 
Several other items can be configured by setting environment variables:
 - 'icon_poolball' uri for eight_ball command
 - 'icon_wiki'     uri for wiki command

more are available, consult legacy_modules.py.

#### Data
Botiana loads local data from a yaml file: `data/data.yaml`

If you're running the bot in kubernetes or in docker you can mount your file from a ConfigMap or a volume mount.

`docker run -v "/path/to/my/data.yaml":"/usr/local/botiana/data/data.yaml"  -e token=$token botiana`

#### Keywords & Reactions
Keywords, responses and reactions can occur in specific channels, or all channels. Configure this in the data.yaml file.

#### Systems Administrator Dictionary
Local dictionary entries can be created for lookup. Configure this in the data.yaml file.

#### Fancy Message Processing
If you would like to route spurios statements including the bot name to a service like Wolfram Alpha or Cleverbot, add the following config to your settings.py (following assumes wolfram alpha). Note, the message_processing_module must match the name of the local module you create for this feature. 

`enable_message_processing = True`
`message_processing_module = 'wolfram'`

You will likely also want to add settings for your custom local module that will handle the command parsing / api call to the service

`# Wolfram Alpha API token`
`wa_token = os.getenv('wa_token', '')`

##### File Requirements
1. All custom commands must start with a letter, not underscores, as the bot rejects underscore commands.
1. You must define an array  `local_commands = ['tru', 'lunch']` that defines what commands in local`local_modules.py` are actionable by botiana. 

If you're running the bot in kubernetes or in docker you can mount your file from a ConfigMap or a volume mount.

`docker run -v "/path/to/my/cool_modules.py":"/usr/local/botiana/local_modules.py"  -e token=$token botiana`

### Build
`docker build . -t botiana`

### Local testing
Get your token from the slack api and export it as shown and run with docker.
```
export token="xoxb-11111111111-111111111111-aaa1aAAAAAaaaAAaAAAAaa1a"
docker build . -t botiana;docker run  -e token=$token botiana
```


