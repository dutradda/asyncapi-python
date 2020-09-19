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
    url='asyncapi-local',
    protocol=asyncapi.ProtocolType.GCLOUD_PUBSUB,
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
    publish=asyncapi.Operation(message=message),
)

spec = asyncapi.Specification(
    info=asyncapi.Info(
        title='User API', version='1.0.0', description='API to manage users',
    ),
    servers={'development': dev_server},
    channels={'user-update': user_update_channel},
    components=asyncapi.Components(messages={'UserUpdate': message}),
)
