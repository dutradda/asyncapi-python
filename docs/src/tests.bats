#!/usr/bin/env bats


@test "should starts subscriber" {
    cd docs/src
    bash ./subscriber.sh > /tmp/asyncapi-subscriber.log &
    sleep 3
    ps ax | grep 'asyncapi-subscriber' | sed -r -e 's/ ?([0-9]+) .*/\1/g' | xargs kill -SIGTERM 2>/dev/null
    [ "$(cat /tmp/asyncapi-subscriber.log)" = "$(cat subscriber.output)" ]
}


@test "should publish message" {
    run coverage run -p docs/src/publish.py
    [ "$status" -eq 0 ]
    [ "$output" = "$(cat docs/src/publish.output)" ]
}


@test "should receive message" {
    cd docs/src
    bash ./subscriber.sh > /tmp/asyncapi-subscriber.log &
    sleep 3
    python publish.py
    ps ax | grep 'asyncapi-subscriber' | sed -r -e 's/ ?([0-9]+) .*/\1/g' | xargs kill -SIGTERM 2>/dev/null
    [ "$(cat /tmp/asyncapi-subscriber.log)" = "$(cat subscriber-receive-message.output)" ]
}
