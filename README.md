# botiana

## Getting started
Botiana is intended to run in a container. But, make your own choice, this isn't Soviet Russia.

### Install requirements
Botiana is currently developed and testing using python 3.7
`pip install -r requirements.txt`

### Settings
The settings file has a few defaults you may need to customize. 
 - You may set your token here, or via the environment.
 - You can change the bot's name, if you must.
 - Set your desired level of logs
 - Set the max translation length
 - Configure the commands you wish to enable from legacy_modules
 
Several other items can be configured by setting environment variables:
 - 'icon_poolball' uri for eight_ball command
 - 'icon_wiki'     uri for wiki command

more are available, consult legacy_modules.py.

Data
Botiana loads local data from a yaml file: data/data.yaml

Keywords & Reactions
Keywords, responses and reactions can occur in specific channels, or all channels. Configure this in the data.yaml file.

Systems Administrator Dictionary
Local dictionary entries can be created for lookup. Configure this in the data.yaml file.

### Build
docker build . -t botiana
