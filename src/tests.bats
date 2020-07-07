#!/usr/bin/env bats


@test "should starts subscriber" {
    cd docs/src
    bash ./subscriber.sh > /tmp/asyncapi-subscriber.log &
    sleep 3
    ps ax | grep 'asyncapi-subscriber' | grep -v bats | sed -r -e 's/ ?([0-9]+) .*/\1/g' | xargs kill -SIGTERM 2>/dev/null
    [ "$(cat /tmp/asyncapi-subscriber.log)" = "$(cat subscriber.output)" ]
}


@test "should publish message" {
    cd docs/src
    run coverage run -p publish.py
    [ "$status" -eq 0 ]
    [ "$output" = "$(cat publish.output)" ]
}


@test "should receive message" {
    cd docs/src
    bash ./subscriber.sh > /tmp/asyncapi-subscriber.log &
    sleep 3
    python publish.py
    ps ax | grep 'asyncapi-subscriber' | grep -v bats | sed -r -e 's/ ?([0-9]+) .*/\1/g' | xargs kill -SIGTERM 2>/dev/null
    [ "$(cat /tmp/asyncapi-subscriber.log)" = "$(cat subscriber-receive-message.output)" ]
}


@test "should publish message auto spec" {
    cd docs/src/auto_spec
    run coverage run -p publish.py
    [ "$status" -eq 0 ]
    [ "$output" = "$(cat ../publish.output)" ]
}

@test "should receive message auto spec" {
    cd docs/src/auto_spec
    bash ./subscriber.sh > /tmp/asyncapi-subscriber.log &
    sleep 3
    python publish.py
    ps ax | grep 'asyncapi-subscriber' | grep -v bats | sed -r -e 's/ ?([0-9]+) .*/\1/g' | xargs kill -SIGTERM 2>/dev/null
    [ "$(cat /tmp/asyncapi-subscriber.log)" = "$(cat ../subscriber-receive-message.output)" ]
}
