# py_spec_user_events.py

import specification


spec = specification.spec


async def receive_user_update(
    message: specification.UserUpdatePayload,
) -> None:
    print(f"Received update for user id={message.id}")
