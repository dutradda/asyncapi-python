# user_events.py

import dataclasses
from typing import Optional

from asyncapi import AutoSpec


spec = AutoSpec('User Events', development='redis://localhost')


@dataclasses.dataclass
class UserUpdateMessage:
    id: str
    name: Optional[str] = None
    age: Optional[int] = None


@spec.subscribe(channel_name='user/update')
async def receive_user_update(message: UserUpdateMessage) -> None:
    print(f"Received update for user id={message.id}")
