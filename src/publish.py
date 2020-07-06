import asyncio
import os

from asyncapi import build_api


spec = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'api-spec.yaml',
)

api = build_api(spec)
message = {
    'id': 'fake-user',
    'name': 'Fake User',
    'age': 33,
}

asyncio.run(api.publish('user/update', message))

print(f"Published update for user={message['id']}")
