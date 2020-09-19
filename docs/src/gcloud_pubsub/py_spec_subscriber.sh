PUBSUB_EMULATOR_HOST=localhost:8086 PYTHONPATH=. asyncapi-subscriber \
    --api-module py_spec_user_events \
    --channels-subscribes 'user-update:user-update-custom-sub=receive_user_update'
