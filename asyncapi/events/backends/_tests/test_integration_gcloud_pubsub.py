import os

import pytest

from asyncapi import EventsHandler


os.environ['PUBSUB_EMULATOR_HOST'] = 'localhost:8086'


@pytest.mark.asyncio
async def test_gcloud_pubsub():
    async with EventsHandler('gcloud-pubsub://asyncapi-local') as handler:
        async with handler.subscribe('chatroom') as subscriber:
            await handler.publish('chatroom', 'hello')
            event = await subscriber.get()
            assert event.channel == 'chatroom'
            assert event.message == 'hello'


@pytest.mark.asyncio
async def test_gcloud_pubsub_two_channels():
    async with EventsHandler('gcloud-pubsub://asyncapi-local') as handler:
        async with handler.subscribe('chatroom') as subscriber:
            async with handler.subscribe('chatroom2') as subscriber2:
                await handler.publish('chatroom', 'hello')
                await handler.publish('chatroom2', 'hello2')
                event = await subscriber.get()
                event2 = await subscriber2.get()
                assert event.channel == 'chatroom'
                assert event.message == 'hello'
                assert event2.channel == 'chatroom2'
                assert event2.message == 'hello2'


@pytest.mark.asyncio
async def test_gcloud_pubsub_consumer_wait_time_option():
    url = 'gcloud-pubsub://asyncapi-local?consumer_wait_time=0.1'
    async with EventsHandler(url) as handler:
        async with handler.subscribe('chatroom') as subscriber:
            await handler.publish('chatroom', 'hello')
            event = await subscriber.get()
            assert event.channel == 'chatroom'
            assert event.message == 'hello'


@pytest.mark.asyncio
async def test_gcloud_pubsub_consumer_consumer_ack_messages_option():
    url = 'gcloud-pubsub://asyncapi-local/?consumer_ack_messages=0'
    async with EventsHandler(url) as handler:
        async with handler.subscribe('chatroom') as subscriber:
            await handler.publish('chatroom', 'hello')
            event = await subscriber.get()
            event.context['ack_func']()
            assert event.channel == 'chatroom'
            assert event.message == 'hello'


@pytest.mark.asyncio
async def test_gcloud_pubsub_consumer_wait_time_and_consumer_ack_messages_options():
    url = 'gcloud-pubsub://asyncapi-local?consumer_wait_time=0.1&consumer_ack_messages=0'
    async with EventsHandler(url) as handler:
        async with handler.subscribe('chatroom') as subscriber:
            await handler.publish('chatroom', 'hello')
            event = await subscriber.get()
            event.context['ack_func']()
            assert event.channel == 'chatroom'
            assert event.message == 'hello'
