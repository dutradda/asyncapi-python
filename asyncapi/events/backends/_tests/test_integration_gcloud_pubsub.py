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
            await event.context['ack_func']()
            assert event.channel == 'chatroom'
            assert event.message == 'hello'


@pytest.mark.asyncio
async def test_gcloud_pubsub_publish_without_subscriber():
    async with EventsHandler('gcloud-pubsub://asyncapi-local') as handler:
        await handler.publish('chatroom', 'hello')

    async with EventsHandler('gcloud-pubsub://asyncapi-local') as handler:
        async with handler.subscribe('chatroom') as subscriber:
            event = await subscriber.get()
            await event.context['ack_func']()
            assert event.channel == 'chatroom'
            assert event.message == 'hello'


@pytest.mark.asyncio
async def test_gcloud_pubsub_two_channels():
    url = 'gcloud-pubsub://asyncapi-local'
    bindings = {
        'consumer_wait_time': '0.01',
        'consumer_pull_message_timeout': '0.01',
    }
    async with EventsHandler(url, bindings) as handler:
        async with handler.subscribe('chatroom') as subscriber:
            async with handler.subscribe('chatroom2') as subscriber2:
                await handler.publish('chatroom', 'hello')
                await handler.publish('chatroom2', 'hello2')
                event = await subscriber.get()
                await event.context['ack_func']()
                assert event.channel == 'chatroom'
                assert event.message == 'hello'
                event2 = await subscriber2.get()
                await event2.context['ack_func']()
                assert event2.channel == 'chatroom2'
                assert event2.message == 'hello2'


@pytest.mark.asyncio
async def test_gcloud_pubsub_consumer_consumer_ack_messages_option():
    url = 'gcloud-pubsub://asyncapi-local'
    bindings = {'consumer_ack_messages': '1'}
    async with EventsHandler(url, bindings) as handler:
        async with handler.subscribe('chatroom') as subscriber:
            await handler.publish('chatroom', 'hello')
            event = await subscriber.get()
            assert 'ack_func' not in event.context
            assert event.channel == 'chatroom'
            assert event.message == 'hello'
