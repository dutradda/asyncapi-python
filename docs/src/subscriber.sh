PYTHONPATH=. asyncapi-subscriber \
    --url api-spec.yaml \
    --channel user/update \
    --operations-module user_events
