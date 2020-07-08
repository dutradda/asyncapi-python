# Python AsyncAPI

<p align="center" style="margin: 3em">
  <a href="https://github.com/dutradda/asyncapi-python">
    <img src="https://dutradda.github.io/asyncapi-python/asyncapi-python-white.svg" alt="asyncapi-python" width="300"/>
  </a>
</p>

<p align="center">
    Python library for translate asyncapi specification to python code, without code generation.
</p>

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
{!./src/api-spec.yaml!}
```


## Creating subscribers module

```python
{!./src/user_events.py!}
```

## Start subscriber to listen events

```bash
{!./src/subscriber.sh!}
```

```
{!./src/subscriber.output!}
```


## Publishing Updates

```python
{!./src/publish.py!}
```

```
{!./src/publish.output!}
```


## Receive Updates

```
{!./src/subscriber-receive-message.output!}
```
