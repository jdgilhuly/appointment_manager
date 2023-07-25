from twilio.rest import Client

client = Client(account_sid, auth_token)

message = client.messages.create(
  from_='+12295973977',
  to='+13106500226'
)

print(message.sid)