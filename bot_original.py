############################################################
#Credit for this bot goes to Ved Shah/Gautham Narayan
#https://github.com/uiucsn/GW-Bot
#Written by: Ved Shah (vedgs2@illinois.edu), Gautham Narayan (gsn@illinois.edu) and the UIUCSN team at the Gravity Collective Meeting at UCSC in April 2023
############################################################
from hop import stream, Stream
from hop.io import StartPosition
from slack import WebClient
from slack_sdk.errors import SlackApiError
from slack_token import SLACK_TOKEN

#Brendan needed to add this to fix an error "ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1056)"
import ssl 
ssl._create_default_https_context = ssl._create_unverified_context

############################################################
# Uncomment this line to get old alerts. The formatting for these can be rough so be careful.
# This is a way to test the slackbot works if no alerts are currently being sent! But in general, turn it off..... (i.e., comment the line out.)
stream = Stream(start_at=StartPosition.EARLIEST)
############################################################


if __name__ == '__main__':

    print("\n\nYour SLACK_TOKEN: "+SLACK_TOKEN+"\n\n")

    with stream.open("kafka://kafka.scimma.org/igwn.gwalert", "r") as s:

        print("\n\nHop Skotch stream open. Creating Slack client...\n\n")
        client = WebClient(token=SLACK_TOKEN)

        for message in s:
            
            # Schema for data available at https://emfollow.docs.ligo.org/userguide/content.html#kafka-notice-gcn-scimma
            data = message.content

            print(f"====================\nIncoming alert of length {len(data)}")

            # Data is a list that can (potentially) have more than 1 element? This is inconsistent with the alert schema
            for instance in data:
                
                # Printing out the alert type and event id to std out
                print(f"{instance['alert_type']}: {instance['superevent_id']}")
                new_channel_name = instance['superevent_id'].lower()

                if instance["alert_type"] != "RETRACTION":

                    try:
                        
                        # Setting some preliminary thresholds so that the channel does not get flooded with bad alerts. Adapt based on needs.
                        if instance['event']['classification']['BNS'] > 0.3: 

                            #print(instance)

                            notice = parse_notice(message.content[0])
                            if notice is None: continue
                            #print(notice)

                            ########

                            #TODO: Whatever processing you want. Make plots, run analysis, classify event, call other api's etc

                            img_link1 = f"https://gracedb.ligo.org/apiweb/superevents/{instance['superevent_id']}/files/bayestar.png"

                            ########

                            
                            # Creating the message text
                            message_text = f"Superevent ID: {instance['superevent_id']}\n \
                            BNS % : {instance['event']['classification']['BNS']}\n \
                            NSBH % : {instance['event']['classification']['NSBH']}\n \
                            Join Related Channel (additional alerts for this event will be sent there): #{instance['superevent_id'].lower()} \n \
                            Skymap Image: {img_link1} \n \
                            "

                            # This creates a new slack channel for the alert
                            try:
                                print("Trying to create a new channel...", end='')
                                response = client.conversations_create(name=new_channel_name, token = SLACK_TOKEN)
                                print(response)
                                print("Done")
                            except SlackApiError as e:
                                if e.response["error"] == "name_taken":
                                    print("Done")
                                else:
                                    print("\nCould not create new channel. Error: ", e.response["error"])

                            # # This gets the bot to join the channel
                            # try:
                            #     print("Trying to join new channel...")
                            #     response = client.conversations_join(channel = new_channel_name, token = SLACK_TOKEN)
                            #     print(response)
                            # except SlackApiError as e:
                            #     print("Could not join channel. Error: ", e.response)

                            # This is a message without buttons and stuff. We are assuming #alert-bot-test already exists and the bot is added to it
                            # If it fails, create #alert-bot-test or similar channel and BE SURE to add the slack bot app to that channel or it cannot send a message to it!
                            try:
                                print("Trying to send message to general channel...", end='')
                                response = client.chat_postMessage(channel='#alert-bot-test', text=message_text)
                                print("Done")
                            except SlackApiError as e:
                                print("\nCould not post message. Error: ", e.response["error"])
                            
                            # This is a message with buttons and stuff to the new channel
                            try:
                                print("Trying to send message to event channel...",end='')
                                response = client.chat_postMessage(
                                                        channel=f"#{new_channel_name}",
                                                        token = SLACK_TOKEN,
                                                        blocks = [  {"type": "section", 
                                                                    "text": {
                                                                                "type": "mrkdwn", 
                                                                                "text": message_text
                                                                                }
                                                                    },
                                                                    {
                                                                        "type": "actions",
                                                                        "block_id": "actions1",
                                                                        "elements": 
                                                                        [
                                                                            {
                                                                                "type": "button",
                                                                                "text": {
                                                                                    "type": "plain_text",
                                                                                    "text": f"Some {instance['superevent_id']} related action"
                                                                                },
                                                                                "value": "cancel",
                                                                                "action_id": "button_1"
                                                                            }
                                                                        ]
                                                                    }
                                                                    
                                                                ]
                                                        )
                                print("Done")
                            except SlackApiError as e:
                                print("\nCould not post message. Error: ", e.response["error"])
                
                    except KeyError:
                        print('Bad data formatting...skipping message')         

                # RETRACTION
                else: 

                    """ 
                    This should archives the channel. Current method -> get list of all channels -> find id for channel name -> call archive function
                    Issue - Linear time operation in the number for channels in the workspace. We wan to avoid this. I do not have a good solution yet.
                    One possible idea is to store a hash map from super event id to channel id on our end but that does not work with dummy alerts. It
                    might work engineering run onwards. 
                    """
                    # TODO: Find O(1) method to archive channels. For now I am just sending a message that event was RETRACTED.

                    # try:
                    #     print(f"{instance['superevent_id']} was retracted. Trying to archive related channel id", end = "")
                    #     temp = "#MS230317q".lower()
                    #     channel_id = client.conversations_info(channel=temp, token=SLACK_TOKEN)['channel']['id']
                    #     print(channel_id)
                    #     try:
                    #         response  = client.conversations_archive(channel=temp)
                    #         print("Done")
                    #     except SlackApiError as e:
                    #         print("\nCould not archive channel. Error: ", e.response, response)
                    # except SlackApiError as e:
                    #         print("\nCould not find channel id. Error: ", e.response["error"])

                    try:
                        print(f"Trying to send message to {new_channel_name} channel...", end='')
                        response = client.chat_postMessage(channel=f'#{new_channel_name}', text="This alert was retracted.")
                        print("Done")
                    except SlackApiError as e:
                        print("\nCould post message. Error: ", e.response["error"])

                    

