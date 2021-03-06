#!/usr/bin/env bats


@test "should request yaml http auto spec" {
    cd docs/src/yaml_spec
    sed -r -e "s/asyncapi-docs/coverage run -p -m 'asyncapi.docs'/" \
        ./docs.sh > /tmp/asyncapi-docs.sh
    bash /tmp/asyncapi-docs.sh > /tmp/asyncapi-docs.log 2>&1 &
    sleep 2
    curl -i localhost:5000/asyncapi.yml \
        > /tmp/asyncapi-docs-yaml.log \
        2> /dev/null
    ps ax | grep 'asyncapi.docs' | \
        grep -v -E 'bats|grep' | sed -r -e 's/ ?([0-9]+) .*/\1/g' | \
        xargs kill -SIGTERM 2>/dev/null
    sleep 1
    sed -i -r -e 's/date: .*/date: .../g' /tmp/asyncapi-docs-yaml.log
    [ "$(cat /tmp/asyncapi-docs-yaml.log)" = "$(cat ../docs-yaml.output)" ] || (\
        echo -e "\n\n\nServer Output (/tmp/asyncapi-docs.log):" && \
        cat /tmp/asyncapi-docs.log && \
        echo -e "\n\n\nEndpoint Output (/tmp/asyncapi-docs-yaml.log):" && \
        cat /tmp/asyncapi-docs-yaml.log \
    )
    [ "$(cat /tmp/asyncapi-docs-yaml.log)" = "$(cat ../docs-yaml.output)" ]
}


@test "should request json http auto spec" {
    cd docs/src/yaml_spec
    sed -r -e "s/asyncapi-docs/coverage run -p -m 'asyncapi.docs'/" \
        ./docs.sh > /tmp/asyncapi-docs.sh
    bash /tmp/asyncapi-docs.sh > /tmp/asyncapi-docs.log 2>&1 &
    sleep 2
    curl -i localhost:5000/asyncapi.json \
        > /tmp/asyncapi-docs-json.log \
        2> /dev/null
    ps ax | grep 'asyncapi.docs' | \
        grep -v -E 'bats|grep' | sed -r -e 's/ ?([0-9]+) .*/\1/g' | \
        xargs kill -SIGTERM 2>/dev/null
    sed -i -r -e 's/date: .*/date: .../g' /tmp/asyncapi-docs-json.log
    [ "$(cat /tmp/asyncapi-docs-json.log)" = "$(cat ../docs-json.output)" ] || (\
        echo -e "\n\n\nServer Output (/tmp/asyncapi-docs.log):" && \
        cat /tmp/asyncapi-docs.log && \
        echo -e "\n\n\nEndpoint Output (/tmp/asyncapi-docs-json.log):" && \
        cat /tmp/asyncapi-docs-json.log \
    )
    [ "$(cat /tmp/asyncapi-docs-json.log)" = "$(cat ../docs-json.output)" ]
}


@test "should publish message http auto spec" {
    cd docs/src/yaml_spec
    sed -r -e "s/asyncapi-docs/coverage run -p -m 'asyncapi.docs'/" \
        ./docs.sh > /tmp/asyncapi-docs.sh
    bash /tmp/asyncapi-docs.sh > /tmp/asyncapi-docs.log 2>&1 &
    sleep 1
    cd ../expose_docs
    run coverage run -p publish.py
    sleep 1
    ps ax | grep 'asyncapi.docs' | \
        grep -v -E 'bats|grep' | sed -r -e 's/ ?([0-9]+) .*/\1/g' | \
        xargs kill -SIGTERM 2>/dev/null
    [ "$status" -eq 0 ]
    [ "$output" = "$(cat ../publish.output)" ]
}


@test "should receive message http auto spec" {
    cd docs/src/yaml_spec
    sed -r -e "s/asyncapi-docs/coverage run -p -m 'asyncapi.docs'/" \
        ./docs.sh > /tmp/asyncapi-docs.sh
    bash /tmp/asyncapi-docs.sh > /tmp/asyncapi-docs.log 2>&1 &
    sleep 1
    cd ../expose_docs
    sed -r -e "s/asyncapi-subscriber/coverage run -p -m 'asyncapi.subscriber'/" \
        ./subscriber.sh > /tmp/asyncapi-subscriber.sh
    bash /tmp/asyncapi-subscriber.sh > /tmp/asyncapi-subscriber.log &
    sleep 1
    coverage run -p publish.py
    sleep 1
    ps ax | grep -E 'asyncapi.docs|asyncapi.subscriber' | \
        grep -v -E 'bats|grep' | sed -r -e 's/ ?([0-9]+) .*/\1/g' | \
        xargs kill -SIGTERM 2>/dev/null
    [ "$(head -2 /tmp/asyncapi-subscriber.log)" = "$(cat ../subscriber-receive-message.output)" ]
}
