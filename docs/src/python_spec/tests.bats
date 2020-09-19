#!/usr/bin/env bats


@test "should starts subscriber python spec" {
    cd docs/src
    sed -r -e "s/asyncapi-subscriber/coverage run -p -m 'asyncapi.subscriber'/" \
        ./py_spec_subscriber.sh > /tmp/asyncapi-subscriber.sh
    bash /tmp/asyncapi-subscriber.sh > /tmp/asyncapi-subscriber.log &
    sleep 1
    ps ax | grep 'asyncapi.subscriber' | \
        grep -v -E 'bats|grep' | sed -r -e 's/ ?([0-9]+) .*/\1/g' | \
        xargs kill -SIGTERM 2>/dev/null
    sleep 1
    [ "$(head -1 /tmp/asyncapi-subscriber.log)" = "$(cat subscriber.output)" ]
}


@test "should publish message python spec" {
    cd docs/src
    run coverage run -p py_spec_publish.py
    [ "$status" -eq 0 ]
    [ "$output" = "$(cat publish.output)" ]
}


@test "should receive message python spec" {
    cd docs/src
    sed -r -e "s/asyncapi-subscriber/coverage run -p -m 'asyncapi.subscriber'/" \
        ./py_spec_subscriber.sh > /tmp/asyncapi-subscriber.sh
    bash /tmp/asyncapi-subscriber.sh > /tmp/asyncapi-subscriber.log &
    sleep 1
    coverage run -p py_spec_publish.py
    sleep 1
    ps ax | grep 'asyncapi.subscriber' | \
        grep -v -E 'bats|grep' | sed -r -e 's/ ?([0-9]+) .*/\1/g' | \
        xargs kill -SIGTERM 2>/dev/null
    [ "$(head -2 /tmp/asyncapi-subscriber.log)" = "$(cat subscriber-receive-message.output)" ]
}


@test "should request yaml python spec" {
    cd docs/src
    sed -r -e "s/asyncapi-docs/coverage run -p -m 'asyncapi.docs'/" \
        ./py_spec_docs.sh > /tmp/asyncapi-docs.sh
    bash /tmp/asyncapi-docs.sh > /tmp/asyncapi-docs.log 2>&1 &
    sleep 2
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
