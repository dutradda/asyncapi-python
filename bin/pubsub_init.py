from google.cloud import pubsub_v1
from google.api_core.exceptions import AlreadyExists as AlreadyExistsError


def pubsub_init():
    project_id = 'asyncapi-local'
    topics = ['chatroom', 'chatroom2', 'user-update']
    subscriptions = ['chatroom', 'chatroom2', 'user-update-custom-sub']

    for topic_name, subscription_name in zip(topics, subscriptions):
        topic_path = create_topic(project_id, topic_name)
        create_subscription(project_id, subscription_name, topic_path)


def create_topic(project_id, name):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, name)

    try:
        publisher.create_topic(topic_path)
    except AlreadyExistsError:
        ...

    return topic_path


def create_subscription(project_id, name, topic_path):
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, name)

    try:
        subscriber.create_subscription(subscription_path, topic_path)
    except AlreadyExistsError:
        ...


pubsub_init()
