# --------------------------------------------------------------------------------------------------
# Author: Chinmay Hegde
# Email: hosmanechinmay@gmail.com
# Created Date: 03-05-2021
# Description: Message sender script that uses twilio to send message
# License: MIT
# --------------------------------------------------------------------------------------------------

from twilio.rest import Client 

def send_message(msg_config, message):
    client = Client(msg_config['account_sid'], msg_config['auth_token'])
    twilio_message = client.messages.create( 
                from_='whatsapp:+{}'.format(msg_config['from']),
                body='Slot Availability: {}'.format(message),
                to='whatsapp:+91{}'.format(msg_config['to'])
            )
    print(twilio_message.sid)

if __name__ == '__main()__':
    pass