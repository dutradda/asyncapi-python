#!/usr/bin/env bats

export PUBSUB_EMULATOR_HOST=localhost:8086


@test "should receive gcloud-pubsub message server bindings" {
    cd docs/src/gcloud_pubsub
    sed -r -e "s/asyncapi-docs/coverage run -p -m 'asyncapi.docs'/" \
        ./docs.sh > /tmp/asyncapi-docs.sh
    bash /tmp/asyncapi-docs.sh > /tmp/asyncapi-docs.log 2>&1 &
    sleep 1
    sed -r -e "s/asyncapi-subscriber/coverage run -p -m 'asyncapi.subscriber'/" \
        ./server_bindings_subscriber.sh > /tmp/asyncapi-subscriber.sh
    bash /tmp/asyncapi-subscriber.sh > /tmp/asyncapi-subscriber.log &
    sleep 1
    coverage run -p publish.py
    sleep 1
    ps ax | grep -E 'asyncapi.subscriber|asyncapi.docs' | \
        grep -v -E 'bats|grep' | sed -r -e 's/ ?([0-9]+) .*/\1/g' | \
        xargs kill -SIGTERM 2>/dev/null
    [ "$(head -2 /tmp/asyncapi-subscriber.log)" = "$(cat ../subscriber-receive-message.output)" ]
}
