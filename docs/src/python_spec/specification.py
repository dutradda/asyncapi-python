# specification.py

import dataclasses
from typing import Optional

import asyncapi


@dataclasses.dataclass
class UserUpdatePayload:
    id: str
    name: Optional[str] = None
    age: Optional[int] = None


dev_server = asyncapi.Server(
    url='localhost',
    protocol=asyncapi.ProtocolType.REDIS,
    description='Development Broker Server',
)
message = asyncapi.Message(
    name='userUpdate',
    title='User Update',
    summary='Inform about users updates',
    payload=UserUpdatePayload,
)
user_update_channel = asyncapi.Channel(
    description='Topic for user updates',
    subscribe=asyncapi.Operation(
        operation_id='receive_user_update', message=message,
    ),
    publish=asyncapi.Operation(message=message),
)

spec = asyncapi.Specification(
    info=asyncapi.Info(
        title='User API', version='1.0.0', description='API to manage users',
    ),
    servers={'development': dev_server},
    channels={'user/update': user_update_channel},
    components=asyncapi.Components(messages={'UserUpdate': message}),
)
