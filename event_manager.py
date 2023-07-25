import os
from vocode.streaming.models.events import Event, EventType
from vocode.streaming.utils import events_manager

from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

class CustomEventsManager(events_manager.EventsManager):
    def __init__(self):
        super().__init__(subscriptions=[EventType.TRANSCRIPT_COMPLETE,EventType.PHONE_CALL_CONNECTED,EventType.TRANSCRIPT])

    def handle_event(self, event: Event):
        if event.type == EventType.PHONE_CALL_CONNECTED:
            print('------------------------------------------------------')
            print('to_phone', event.to_phone_number)
            global to_phone
            to_phone = event.to_phone_number
            print('from_phone', event.from_phone_number)
            global from_phone
            from_phone = event.from_phone_number
        if event.type == EventType.TRANSCRIPT_COMPLETE:
            print('------------------------------------------------------')
            print('conversation_id', event.conversation_id)
            for message in event.transcript.event_logs:
                text = message.text
                print('individual message',text)
                if 'confirmed for an appointment with' in text:
                    body = text
                    message = client.messages.create(
                              body = body,
                              from_ = to_phone,
                              to = from_phone
                          )

                    print('twilio message',message.sid)