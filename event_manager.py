import os
from vocode.streaming.models.events import Event, EventType
from vocode.streaming.utils import events_manager

from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

from collections import defaultdict

class CustomEventsManager(events_manager.EventsManager):
    def __init__(self):
        super().__init__(subscriptions=[EventType.TRANSCRIPT_COMPLETE, EventType.PHONE_CALL_CONNECTED, EventType.TRANSCRIPT])
        self.confirmation_sent = defaultdict(bool)

    def handle_event(self, event: Event):

        # Get Phone call information
        if event.type == EventType.PHONE_CALL_CONNECTED:
            print('------------------------------------------------------')
            print('phone call # recieving call:', event.to_phone_number)
            global to_phone
            to_phone = event.to_phone_number
            print('recieving call from phone #:', event.from_phone_number)
            global from_phone
            from_phone = event.from_phone_number

        # Handles post conversation i.e. sends message after convo is done and appointment is confirmed
        if event.type == EventType.TRANSCRIPT_COMPLETE:
            print('------------------------------------------------------')
            print('conversation_id', event.conversation_id)

            if not self.confirmation_sent[event.conversation_id]:
                for message in event.transcript.event_logs:
                    text = message.text
                    print('individual message', text)
                    if 'confirmed for an appointment with' in text:
                        body = text
                        message = client.messages.create(
                            body=body,
                            from_=to_phone,
                            to=from_phone
                        )

                        print('twilio message send id: ', message.sid)
                        self.confirmation_sent[event.conversation_id] = True
                        break  # Only send one message per conversation