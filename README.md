# Python AsyncAPI

<p align="center" style="margin: 3em">
  <a href="https://github.com/dutradda/asyncapi-python">
    <img src="https://dutradda.github.io/asyncapi-python/asyncapi-python.svg" alt="asyncapi-python" width="300"/>
  </a>
</p>

<p align="center">
    Python library for translate <a href="https://asyncapi.io">asyncapi</a> specification to python code, without code generation.
</p>

---

**AsyncAPI Pattern**: <a href="https://asyncapi.io" target="_blank">https://asyncapi.io</a>

---

**Documentation**: <a href="https://dutradda.github.io/asyncapi-python/" target="_blank">https://dutradda.github.io/asyncapi-python/</a>

**Source Code**: <a href="https://github.com/dutradda/asyncapi-python" target="_blank">https://github.com/dutradda/asyncapi-python</a>

---


## Key Features

- **Reads an asyncapi specification and create publishers and subscribers from it**

- **Support for specification declaration with dataclasses**

- **Provides application for create subscribers**

- **Support for kafka, redis and postgres protocols (same as broadcaster library)**

- **Extra support for google cloud pubsub service**

- **Expose in http the auto-generated specification**


## Requirements

 - Python 3.8+
 - broadcaster
 - jsondaora
 - requests (Optional for http specification)
 - typer (Optional for subscriber application)
 - pyyaml (Optional for yaml specification)
 - apidaora (Optional for expose specification)

 - Package extra installs:
    + http
    + yaml
    + kafka
    + redis
    + postgres
    + subscriber
    + docs
    + google-cloud-pubsub


## Installation

```
$ pip install asyncapi[http,yaml,redis,subscriber,docs]
```


## YAML Specification Example

```yaml
asyncapi: 2.0.0

info:
  title: User API
  version: '1.0.0'
  description: API to manage users

servers:
  development:
    url: localhost
    protocol: redis
    description: Development Broker Server

channels:
  user/update:
    description: Topic for user updates
    subscribe:
      operationId: receive_user_update
      message:
        $ref: '#/components/messages/UserUpdate'
    publish:
      message:
        $ref: '#/components/messages/UserUpdate'

components:
  messages:
    UserUpdate:
      name: userUpdate
      title: User Update
      summary: Inform about users updates
      payload:
        type: object
        required:
          - id
        properties:
          id:
            type: string
          name:
            type: string
          age:
            type: integer

defaultContentType: application/json

```

### Creating subscribers module

```python
# user_events.py

from typing import Any


async def receive_user_update(message: Any) -> None:
    print(f"Received update for user id={message.id}")

```

### Start subscriber to listen events

```bash
PYTHONPATH=. asyncapi-subscriber \
    --url api-spec.yaml \
    --api-module user_events

```

```
Waiting messages...

```

### Publishing Updates

```python
# publish.py

import asyncio

from asyncapi import build_api


api = build_api('api-spec.yaml')
channel_id = 'user/update'
message = api.payload(channel_id, id='fake-user', name='Fake User', age=33)


async def publish() -> None:
    await api.connect()
    await api.publish(channel_id, message)
    await api.disconnect()


asyncio.run(publish())

print(f"Published update for user={message.id}")

```

```
python publish.py


Published update for user=fake-user

```

### Receive Updates

```
Waiting messages...
Received update for user id=fake-user

```

### Expose Specification

```bash
asyncapi-docs --path api-spec.yaml

```

```bash
curl -i localhost:5000/asyncapi.yaml
```


## Python Specification Example

```python
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

```

### Creating subscribers module

```python
# py_spec_user_events.py

import specification


spec = specification.spec


async def receive_user_update(
    message: specification.UserUpdatePayload,
) -> None:
    print(f"Received update for user id={message.id}")

```

### Start subscriber to listen events

```bash
PYTHONPATH=. asyncapi-subscriber --api-module user_events

```

```
Waiting messages...

```

### Publishing Updates

```python
# publish.py

import asyncio

from asyncapi import build_api_auto_spec


api = build_api_auto_spec('specification')
channel_id = 'user/update'
message = api.payload(channel_id, id='fake-user', name='Fake User', age=33)


async def publish() -> None:
    await api.connect()
    await api.publish(channel_id, message)
    await api.disconnect()


asyncio.run(publish())

print(f"Published update for user={message.id}")

```

```
python publish.py


Published update for user=fake-user

```

### Receive Updates

```
Waiting messages...
Received update for user id=fake-user

```

### Expose Specification

```bash
PYTHONPATH=. asyncapi-docs --api-module specification

```

```bash
curl -i localhost:5000/asyncapi.yaml
```
