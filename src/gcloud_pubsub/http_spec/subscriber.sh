PUBSUB_EMULATOR_HOST=localhost:8086 PYTHONPATH=. asyncapi-subscriber \
    --url http://localhost:5000/asyncapi.yaml \
    --api-module user_events \
    --channels-subscribes 'user-update:user-update-custom-sub=receive_user_update'
