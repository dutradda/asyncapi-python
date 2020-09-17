#!/usr/bin/env bats


@test "should starts subscriber" {
    cd docs/src
    bash ./subscriber.sh > /tmp/asyncapi-subscriber.log &
    sleep 1
    ps ax | grep 'asyncapi-subscriber' | \
        grep -v -E 'bats|grep' | sed -r -e 's/ ?([0-9]+) .*/\1/g' | \
        xargs kill -SIGTERM 2>/dev/null
    sleep 1
    [ "$(head -1 /tmp/asyncapi-subscriber.log)" = "$(cat subscriber.output)" ]
}


@test "should publish message" {
    cd docs/src
    run coverage run -p publish.py
    [ "$status" -eq 0 ]
    [ "$output" = "$(cat publish.output)" ]
}


@test "should receive message" {
    cd docs/src
    PYTHONPATH=. coverage run -p -m 'asyncapi.subscriber' \
        --url api-spec.yaml --api-module user_events \
        > /tmp/asyncapi-subscriber.log &
    sleep 1
    coverage run -p publish.py
    sleep 1
    ps ax | grep 'asyncapi.subscriber' | \
        grep -v -E 'bats|grep' | sed -r -e 's/ ?([0-9]+) .*/\1/g' | \
        xargs kill -SIGTERM 2>/dev/null
    [ "$(head -2 /tmp/asyncapi-subscriber.log)" = "$(cat subscriber-receive-message.output)" ]
}


@test "should publish message auto spec" {
    cd docs/src/auto_spec
    run coverage run -p publish.py
    [ "$status" -eq 0 ]
    [ "$output" = "$(cat ../publish.output)" ]
}


@test "should serve docs" {
    cd docs/src/auto_spec
    bash ./docs.sh > /tmp/asyncapi-docs.log 2>&1 &
    sleep 1
    ps ax | grep 'asyncapi-docs' | \
        grep -v -E 'bats|grep' | sed -r -e 's/ ?([0-9]+) .*/\1/g' | \
        xargs kill -SIGTERM 2>/dev/null
    sleep 1
    sed -i -r -e 's/process \[([0-9]+)\]/process [...]/g' /tmp/asyncapi-docs.log
    [ "$(cat /tmp/asyncapi-docs.log)" = "$(cat docs.output)" ]
}


@test "should request yaml spec" {
    cd docs/src/auto_spec
    PYTHONPATH=. coverage run -p -m 'asyncapi.docs' \
        --api-module user_events > /tmp/asyncapi-docs.log 2>&1 &
    sleep 1
    curl -i localhost:5000/asyncapi.yaml \
        > /tmp/asyncapi-docs-yaml.log \
        2> /dev/null
    ps ax | grep 'asyncapi.docs' | \
        grep -v -E 'bats|grep' | sed -r -e 's/ ?([0-9]+) .*/\1/g' | \
        xargs kill -SIGTERM 2>/dev/null
    sleep 1
    sed -i -r -e 's/date: .*/date: .../g' /tmp/asyncapi-docs-yaml.log
    [ "$(cat /tmp/asyncapi-docs-yaml.log)" = "$(cat docs-yaml.output)" ] || (\
        echo -e "\n\n\nServer Output (/tmp/asyncapi-docs.log):" && \
        cat /tmp/asyncapi-docs.log && \
        echo -e "\n\n\nEndpoint Output (/tmp/asyncapi-docs-yaml.log):" && \
        cat /tmp/asyncapi-docs-yaml.log \
    )
    [ "$(cat /tmp/asyncapi-docs-yaml.log)" = "$(cat docs-yaml.output)" ]
}


@test "should request json spec" {
    cd docs/src/auto_spec
    PYTHONPATH=. coverage run -p -m 'asyncapi.docs' \
        --api-module user_events > /tmp/asyncapi-docs.log 2>&1 &
    sleep 3
    curl -i localhost:5000/asyncapi.json \
        > /tmp/asyncapi-docs-json.log \
        2> /dev/null
    ps ax | grep 'asyncapi.docs' | \
        grep -v -E 'bats|grep' | sed -r -e 's/ ?([0-9]+) .*/\1/g' | \
        xargs kill -SIGTERM 2>/dev/null
    sed -i -r -e 's/date: .*/date: .../g' /tmp/asyncapi-docs-json.log
    [ "$(cat /tmp/asyncapi-docs-yaml.log)" = "$(cat docs-yaml.output)" ] || (\
        echo -e "\n\n\nServer Output (/tmp/asyncapi-docs.log):" && \
        cat /tmp/asyncapi-docs.log && \
        echo -e "\n\n\nEndpoint Output (/tmp/asyncapi-docs-json.log):" && \
        cat /tmp/asyncapi-docs-json.log \
    )
    [ "$(cat /tmp/asyncapi-docs-json.log)" = "$(cat docs-json.output)" ]
}


@test "should publish message from http spec" {
    cd docs/src/auto_spec
    bash ./docs.sh > /tmp/asyncapi-docs.log 2>&1 &
    sleep 1
    run coverage run -p publish_http.py
    sleep 1
    ps ax | grep 'asyncapi-docs' | \
        grep -v -E 'bats|grep' | sed -r -e 's/ ?([0-9]+) .*/\1/g' | \
        xargs kill -SIGTERM 2>/dev/null
    [ "$status" -eq 0 ]
    [ "$output" = "$(cat ../publish.output)" ]
}


@test "should receive message from http spec" {
    cd docs/src/auto_spec
    bash ./docs.sh > /tmp/asyncapi-docs.log 2>&1 &
    sleep 1
    bash ./subscriber-http.sh > /tmp/asyncapi-http-subscriber.log &
    sleep 1
    coverage run -p publish_http.py
    sleep 1
    ps ax | grep -E 'asyncapi-docs|asyncapi-subscriber' | \
        grep -v -E 'bats|grep' | sed -r -e 's/ ?([0-9]+) .*/\1/g' | \
        xargs kill -SIGTERM 2>/dev/null
    [ "$(head -2 /tmp/asyncapi-http-subscriber.log)" = "$(cat ../subscriber-receive-message.output)" ]
}
