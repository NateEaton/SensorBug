
from googlevoice import Voice
#from googlevoice.util import input

voice = Voice()
voice.login()

phoneNumber = '3166418641' # input('Number to send message to: ')
text = 'Something wonderful has happened.' #input('Message text: ')

voice.send_sms(phoneNumber, text)
