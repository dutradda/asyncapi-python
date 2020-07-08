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

- **Provides application for create subscribers**

- **Support for kafka, redis and postgres protocols (same as broadcaster library)**

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


## Installation

```
$ pip install asyncapi[http,yaml,redis,subscriber]
```


## Specification Example

```yaml
asyncapi: 2.0.0

info:
  title: User API
  version: '1.0.0'
  description: API do manage users

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


## Creating subscribers module

```python
# user_events.py

from typing import Any


async def receive_user_update(message: Any) -> None:
    print(f"Received update for user id={message.id}")

```

## Start subscriber to listen events

```bash
PYTHONPATH=. asyncapi-subscriber \
    --url api-spec.yaml \
    --api-module user_events

```

```
Waiting messages...

```


## Publishing Updates

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


asyncio.run(publish())

print(f"Published update for user={message.id}")

```

```
Published update for user=fake-user

```


## Receive Updates

```
Waiting messages...
Received update for user id=fake-user

```
