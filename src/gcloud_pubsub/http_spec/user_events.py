# user_events.py

from typing import Any, Awaitable, Callable


async def receive_user_update(
    message: Any, ack_func: Callable[[], Awaitable[None]]
) -> None:
    print(f"Received update for user id={message.id}")
    await ack_func()
