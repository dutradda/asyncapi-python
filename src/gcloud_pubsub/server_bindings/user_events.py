# user_events.py

from typing import Any, Callable


async def receive_user_update(
    message: Any, ack_func: Callable[[], None]
) -> None:
    print(f"Received update for user id={message.id}")
    ack_func()
