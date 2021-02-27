import os
import ssl
import sys
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(1, "./python-slackclient")
import logging
logging.basicConfig(level=logging.DEBUG)

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

from slack import WebClient, RTMClient
rtm_client = RTMClient(token=os.environ.get('BOT_TOKEN'), ssl=ssl_context)
starterbot_id = None

threads = {}

@RTMClient.run_on(event='message')
def manage_bug(**payload):
    data = payload['data']
    web_client = payload['web_client']

    if data.get('subtype'):
      return

    if threads.get(data['user']) and threads.get(data['user']).get('title'):
        threads.get(data['user'])['message'] = data['text']
        web_client.chat_postMessage(
          channel=threads.get(data['user']).get('channel_id'),
          text=f"Mensaje reportado.",
          thread_ts=data['ts']
        )
        threads.pop(data['user'])

    if threads.get(data['user']) and not threads.get(data['user']).get('title'):
        threads.get(data['user'])['title'] = data['text']
        web_client.chat_postMessage(
          channel=threads.get(data['user']).get('channel_id'),
          text=f"Titulo registrado. *Escribe un mensaje:*",
          thread_ts=data['ts']
        )

    if 'bug' == data['text'].lower():
        channel_id = data['channel']
        thread_ts = data['ts']
        user = data['user'] # This is not username but user ID (the format is either U*** or W***)

        threads[user] = {
            'channel_id': channel_id,
            'title': None,
            'message': None
        }

        web_client.chat_postMessage(
          channel=channel_id,
          text=f"Hola <@{user}>! \n*Escribe titulo del reporte:*",
          thread_ts=thread_ts
        )

if __name__ == "__main__":
    rtm_client.start()
