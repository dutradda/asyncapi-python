# user_events.py

import dataclasses
from typing import Optional


@dataclasses.dataclass
class UserUpdateMessage:
    id: str
    name: Optional[str] = None
    age: Optional[int] = None


async def receive_user_update(message: UserUpdateMessage) -> None:
    print(f"Received update for user id={message.id}")
