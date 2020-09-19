#!/usr/bin/env bats

export PUBSUB_EMULATOR_HOST=localhost:8086


@test "should publish gcloud-pubsub message python spec" {
    cd docs/src/gcloud_pubsub/python_spec
    run coverage run -p publish.py
    echo "$output"
    [ "$status" -eq 0 ]
    [ "$output" = "$(cat ../../publish.output)" ]
}


@test "should receive gcloud-pubsub message python spec" {
    cd docs/src/gcloud_pubsub/python_spec
    sed -r -e "s/asyncapi-subscriber/coverage run -p -m 'asyncapi.subscriber'/" \
        ./subscriber.sh > /tmp/asyncapi-subscriber.sh
    bash /tmp/asyncapi-subscriber.sh > /tmp/asyncapi-subscriber.log &
    sleep 1
    coverage run -p publish.py
    sleep 1
    ps ax | grep 'asyncapi.subscriber' | \
        grep -v -E 'bats|grep' | sed -r -e 's/ ?([0-9]+) .*/\1/g' | \
        xargs kill -SIGTERM 2>/dev/null
    [ "$(head -2 /tmp/asyncapi-subscriber.log)" = "$(cat ../../subscriber-receive-message.output)" ]
}
