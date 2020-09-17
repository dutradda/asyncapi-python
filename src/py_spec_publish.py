# py_spec_publish.py

import asyncio

from asyncapi import build_api_auto_spec


api = build_api_auto_spec('specification')
channel_id = 'user/update'
message = api.payload(channel_id, id='fake-user', name='Fake User', age=33)


async def publish() -> None:
    await api.connect()
    await api.publish(channel_id, message)


asyncio.run(publish())

print(f"Published update for user={message.id}")
