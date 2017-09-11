# botiana

## Getting started
I highly suggest running this in docker. But, make your own choice, this isn't Soviet Russia.

### Install requirements
`pip install -r requirements.txt`

### Configuration
settings are in `settings.py`
sysadmin dictonary definitions in `sa.yaml`
keyword triggers are in `keywords.yaml`

Consider using the environment for your setting.py. It makes it easier when running in kubernetes

## Execution
`cd /path/to/botiana/repo && ./botiana.py`
