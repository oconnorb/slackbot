# GW-Bot

Slack alert bot for `LIGO 04` gravitational wave alerts via Scimma's Hopskotch. 

If you are are looking to set up the alert bot within your own workspace, follow the instructions below.

## 1. Getting started in your own workspace:

### 1.1 Set up SCiMMA / HOPSKOTCH listener

* Follow instructions to create credentials and install hop-client https://rtd.igwn.org/projects/userguide/en/v17.1/tutorial/receiving/scimma.html 
And https://github.com/scimma/hop-client/wiki/Tutorial:-using-hop-client-with-the-SCiMMA-Hopskotch-server and https://hop-client.readthedocs.io/en/stable/
* You can download the hopskotch credentials as a .csv to then pass to hop auth as the username and password are the credentials and not those used to register on the hopskotch website
* It seems this information from hopskotch for your credentials is only provided once so download it or save it otherwise you will just need to repeat the process. 
* To check your authorizations: hop auth locate
* Then need to run hop subscribe kafka://kafka.scimma.org/igwn.gwalert
* LVK Alerts content https://emfollow.docs.ligo.org/userguide/content.html

### 1.2 Configure Slack

* Start creating a new app here [https://api.slack.com/apps].
* Click on `Create New App`.
* Choose `From an App Manifest`.
* Choose your workspace. This is where the bot will be installed.
* Use the app manifest below (both JSON and YAML formats). Please note that these are the permissions that we are currently using. You may want to limit what the bot is capable of doing inside your workspace but that might come at the cost of functionality.
* Create the app.
* Navigate to `Features` > `OAuth & Permissions` and scroll down to `OAuth Tokens for Your Workspace`. From here, you can install the app to your workspace. Once you have read through the data permissions, click allow.
* You will now see a `Bot User OAuth Token`. This is what you can use within python to access the api. 
* Note: I found that you need pip3 install slack-sdk in order for the `import slack' command to work - pip3 install slackclient is apparently deprecated…


#### App manifests:
```YAML
display_information:
  name: LIGO-Alert-Bot
features:
  bot_user:
    display_name: LIGO-Alert-Bot
    always_online: false
oauth_config:
  scopes:
    bot:
      - calls:read
      - channels:join
      - channels:manage
      - chat:write
      - chat:write.customize
      - commands
      - files:write
      - groups:write
      - im:write
      - mpim:write
      - channels:read
      - groups:read
settings:
  org_deploy_enabled: false
  socket_mode_enabled: false
  token_rotation_enabled: false

```

```JSON
{
    "display_information": {
        "name": "LIGO-Alert-Bot"
    },
    "features": {
        "bot_user": {
            "display_name": "LIGO-Alert-Bot",
            "always_online": false
        }
    },
    "oauth_config": {
        "scopes": {
            "bot": [
                "calls:read",
                "channels:join",
                "channels:manage",
                "chat:write",
                "chat:write.customize",
                "commands",
                "files:write",
                "groups:write",
                "im:write",
                "mpim:write",
                "channels:read",
                "groups:read"
            ]
        }
    },
    "settings": {
        "org_deploy_enabled": false,
        "socket_mode_enabled": false,
        "token_rotation_enabled": false
    }
}
```

### 1.3 Configure Python 

* Create a file named `slack_token.py`. Within this file, store the `Bot User OAuth Token` in a variable called `SLACK_TOKEN`. This token will allow you to interface between python and slack.
* Use the `env.txt` file to recreate the python environment using conda. This can be done using `conda env create --file env.txt`.
* Activate the newly created conda environment and run `python bot_updated.py` and you should seeing the alerts as they come in. 
* Note: The original `bot.py` is available through the SCIMMA repo and this fork was edited to add additional capabilities. 

## Known Issues:

* The current alerts are not real. Thus, there is a fair bit of repetition which causes some of the channel-creation and archiving features to fail. We expect this issue to resolve itself when the engineering run begins. The current alerts are also all BNS mergers and this will change once the science run begins.

* Archiving channels after a retraction is very slow right now and will get slower as the number of channels in a workspace increases (due to linear search). Slack does not currently have api's (that I could find) that can do this efficiently (O(1)) so we might have to build something on our own. Once again, this depends on having relatively consistent data formatting (like `PRELIMINARY` alerts for any `superevent id` coming in before `RETRACTION` alerts). We hope to iron this out during the engineering run.

## Brendan's To Do:

* Fix channel archiving
* Run gwemopt automatically to generate pointings for good events
* Define better event selection criteria
* Slack button to create new channel for events instead of doing so everytime, because, as mentioned above, this causes things to slow down over time. 
* Document the selection criteria used and the workflow for channel creation etc...

## Acknowledgements:

This bot was created as part of the collaborative efforts of the Gravity collective. 

If you do use this project in your work, please acknowledge the original code developers Ved Shah (vedgs2@illinois.edu), Gautham Narayan (gsn@illinois.edu) and the UIUCSN team. This repo also makes use of some code developed by Charlie Kilpatrick (https://github.com/charliekilpatrick/bot) for parsing LVK alerts. 
