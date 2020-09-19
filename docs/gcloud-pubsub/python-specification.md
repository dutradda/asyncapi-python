# From a Python Specification

To reproduce this example you will need a local pubsub emulator running on port 8086.
The project repository has a [docker-compose file](https://github.com/dutradda/asyncapi-python/blob/master/docker-compose.yaml) setting up the emulator.


## Specification Example

The `url` attribute of the Server Object is the Google Cloud Platform `project_id`.

```python
{!./src/gcloud_pubsub/specification.py!}
```

## Creating subscribers module

```python
{!./src/gcloud_pubsub/py_spec_user_events.py!}
```

## Start subscriber to listen events

This specification don't declares subscribers.
It is intentional because google pubsub can accept multiple subscribers with differents channel names on the same topic.

We will use the `channels-subscribes` argument of the subscriber runner to set the pubsub subscription.

```bash
{!./src/gcloud_pubsub/py_spec_subscriber.sh!}
```

```
{!./src/subscriber.output!}
```


## Publishing Updates

```python
{!./src/gcloud_pubsub/py_spec_publish.py!}
```

```
{!./src/publish.output!}
```


## Receive Updates

```
{!./src/subscriber-receive-message.output!}
```
