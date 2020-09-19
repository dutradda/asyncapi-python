# GCloud PubSub Server Bindings

The AsyncAPI Specification allows custom properties for the protocols that the server runs.
Here we will use custom parameters to control the pubsub EventsHandler.

To reproduce this example you will need a local pubsub emulator running on port 8086.
The project repository has a [docker-compose file](https://github.com/dutradda/asyncapi-python/blob/master/docker-compose.yaml) setting up the emulator.


## Specification Example

The `url` attribute of the Server Object is the Google Cloud Platform `project_id`.

```yaml
{!./src/gcloud_pubsub/api-spec.yaml!}
```


## Expose the Specification

Assuming that the above specification has the name `api-spec.yaml`:

```bash
{!./src/gcloud_pubsub/docs.sh!}
```


## Creating subscribers module

```python
{!./src/gcloud_pubsub/server_bindings_user_events.py!}
```


## Start subscriber to listen events

For pubsub custom attributes we will use the `server-bindings` argument of the subscriber runner.
The pubsub EventsHandler accept two parameters: `consumer_wait_time` and `ack_consumed_messages`.
The first one is used to wait if there are no messages to consume. The default value is 1 second.

The second parameter tells the EventsHandler to acknowledge the message or not. The default value is `True`.
When `ack_consumed_messages` is `False`, the acknowledge function will be set on subscriber `kwargs` by the name `ack_func`.

This specification don't declares subscribers.
It is intentional because google pubsub can accept multiple subscribers with differents channel names on the same topic.

We will use the `channels-subscribes` argument of the subscriber runner to set the pubsub subscription.

```bash
{!./src/gcloud_pubsub/server_bindings_subscriber.sh!}
```

```
{!./src/subscriber.output!}
```


## Publishing Updates

```python
{!./src/gcloud_pubsub/publish.py!}
```

```
{!./src/publish.output!}
```


## Receive Updates

```
{!./src/subscriber-receive-message.output!}
```
