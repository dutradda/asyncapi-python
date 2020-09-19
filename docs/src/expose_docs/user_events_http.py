# user_events_http.py

from typing import Any


async def receive_user_update(message: Any) -> None:
    print(f"Received update for user id={message.id}")
