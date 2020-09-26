# user_events.py

from typing import Awaitable, Callable

import specification


spec = specification.spec


async def receive_user_update(
    message: specification.UserUpdatePayload,
    ack_func: Callable[[], Awaitable[None]],
) -> None:
    print(f"Received update for user id={message.id}")
    await ack_func()
