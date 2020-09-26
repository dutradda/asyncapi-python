PUBSUB_EMULATOR_HOST=localhost:8086 PYTHONPATH=. asyncapi-subscriber \
    --url http://localhost:5000/asyncapi.yaml \
    --api-module user_events \
    --channels-subscribes 'user-update:user-update-custom-sub=receive_user_update' \
    --server-bindings 'gcloud-pubsub:consumer_wait_time=0.1;consumer_ack_messages=1'
