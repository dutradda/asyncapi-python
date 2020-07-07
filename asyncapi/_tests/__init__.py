from dataclasses import dataclass

from asyncapi import Spec


spec = Spec(
    title='Fake API',
    description='Faked API',
    version='0.0.1',
    development='kafka://fake.fake',
)


@dataclass
class FakeMessage:
    faked: int


@spec.subscribe(
    channel_name='fake',
    channel_description='Fake Channel',
    message_name='FakeMessage',
    message_title='Faked',
    message_summary='Faked message',
)
async def fake_operation(message: FakeMessage) -> None:
    return message
