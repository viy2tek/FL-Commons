"""Read-only initial SDK example; set the same token as the local server."""
import os

from fl_commons.sdk import APIError, Client

client = Client(os.environ['FL_COMMONS_TOKEN'])
try:
    print(client.capabilities())
    print(client.command('transport.state'))
except APIError as error:
    print('Bridge error:', error.code, str(error))
    raise SystemExit(1)
