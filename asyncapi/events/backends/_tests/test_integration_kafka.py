import asyncio

import pytest

from asyncapi import EventsHandler


@pytest.mark.asyncio
async def test_kafka_two_urls():
    async with EventsHandler(
        'kafka://localhost:9093,localhost:9093'
    ) as events_handler:
        async with events_handler.subscribe('chatroom') as subscriber:
            await asyncio.sleep(1)
            await events_handler.publish('chatroom', 'hello')
            event = await subscriber.get()
            assert event.channel == 'chatroom'
            assert event.message == 'hello'
