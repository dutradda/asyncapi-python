# Python AsyncAPI

<p align="center" style="margin: 3em">
  <a href="https://github.com/dutradda/asyncapi-python">
    <img src="https://dutradda.github.io/asyncapi-python/asyncapi-python-white.svg" alt="asyncapi-python" width="300"/>
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
$ pip install asyncapi[http,yaml,redis,subscriber,docs]
```


## Specification Example

```yaml
{!./src/api-spec.yaml!}
```

### Creating subscribers module

```python
{!./src/user_events.py!}
```

### Start subscriber to listen events

```bash
{!./src/subscriber.sh!}
```

```
{!./src/subscriber.output!}
```

### Publishing Updates

```python
{!./src/publish.py!}
```

```
python publish.py

{!./src/publish.output!}
```

### Receive Updates

```
{!./src/subscriber-receive-message.output!}
```

### Expose Specification


```bash
{!./src/docs.sh!}
```

```bash
curl -i localhost:5000/asyncapi.yaml
```


## Python Specification Example

```python
{!./src/specification.py!}
```

### Creating subscribers module

```python
{!./src/py_spec_user_events.py!}
```

### Start subscriber to listen events

```bash
{!./src/py_spec_subscriber.sh!}
```

```
{!./src/subscriber.output!}
```

### Publishing Updates

```python
{!./src/py_spec_publish.py!}
```

```
python py_spec_publish.py

{!./src/publish.output!}
```

### Receive Updates

```
{!./src/subscriber-receive-message.output!}
```

### Expose Specification


```bash
{!./src/py_spec_docs.sh!}
```

```bash
curl -i localhost:5000/asyncapi.yaml
```
