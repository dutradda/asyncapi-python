#!/usr/bin/env bats

export PUBSUB_EMULATOR_HOST=localhost:8086


@test "should starts subscriber" {
    cd docs/src
    sed -r -e "s/asyncapi-subscriber/coverage run -p -m 'asyncapi.subscriber'/" \
        ./subscriber.sh > /tmp/asyncapi-subscriber.sh
    bash /tmp/asyncapi-subscriber.sh > /tmp/asyncapi-subscriber.log &
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
    sed -r -e "s/asyncapi-subscriber/coverage run -p -m 'asyncapi.subscriber'/" \
        ./subscriber.sh > /tmp/asyncapi-subscriber.sh
    bash /tmp/asyncapi-subscriber.sh > /tmp/asyncapi-subscriber.log &
    sleep 1
    coverage run -p publish.py
    sleep 1
    ps ax | grep 'asyncapi.subscriber' | \
        grep -v -E 'bats|grep' | sed -r -e 's/ ?([0-9]+) .*/\1/g' | \
        xargs kill -SIGTERM 2>/dev/null
    [ "$(head -2 /tmp/asyncapi-subscriber.log)" = "$(cat subscriber-receive-message.output)" ]
}


@test "should request yaml spec" {
    cd docs/src
    sed -r -e "s/asyncapi-docs/coverage run -p -m 'asyncapi.docs'/" \
        ./docs.sh > /tmp/asyncapi-docs.sh
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
    echo "$output"
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


@test "should publish message auto spec" {
    cd docs/src/auto_spec
    run coverage run -p publish.py
    [ "$status" -eq 0 ]
    [ "$output" = "$(cat ../publish.output)" ]
}


@test "should receive message auto spec" {
    cd docs/src/auto_spec
    sed -r -e "s/asyncapi-subscriber/coverage run -p -m 'asyncapi.subscriber'/" \
        ./subscriber.sh > /tmp/asyncapi-subscriber.sh
    bash /tmp/asyncapi-subscriber.sh > /tmp/asyncapi-subscriber.log &
    sleep 1
    coverage run -p publish.py
    sleep 1
    ps ax | grep 'asyncapi.subscriber' | \
        grep -v -E 'bats|grep' | sed -r -e 's/ ?([0-9]+) .*/\1/g' | \
        xargs kill -SIGTERM 2>/dev/null
    [ "$(head -2 /tmp/asyncapi-subscriber.log)" = "$(cat ../subscriber-receive-message.output)" ]
}


@test "should serve docs" {
    cd docs/src/auto_spec
    sed -r -e "s/asyncapi-docs/coverage run -p -m 'asyncapi.docs'/" \
        ./docs.sh > /tmp/asyncapi-docs.sh
    bash /tmp/asyncapi-docs.sh > /tmp/asyncapi-docs.log 2>&1 &
    sleep 1
    ps ax | grep 'asyncapi.docs' | \
        grep -v -E 'bats|grep' | sed -r -e 's/ ?([0-9]+) .*/\1/g' | \
        xargs kill -SIGTERM 2>/dev/null
    sleep 1
    sed -i -r -e 's/process \[([0-9]+)\]/process [...]/g' /tmp/asyncapi-docs.log
    [ "$(cat /tmp/asyncapi-docs.log)" = "$(cat docs.output)" ]
}


@test "should request yaml auto spec" {
    cd docs/src/auto_spec
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
    [ "$(cat /tmp/asyncapi-docs-yaml.log)" = "$(cat docs-yaml.output)" ] || (\
        echo -e "\n\n\nServer Output (/tmp/asyncapi-docs.log):" && \
        cat /tmp/asyncapi-docs.log && \
        echo -e "\n\n\nEndpoint Output (/tmp/asyncapi-docs-yaml.log):" && \
        cat /tmp/asyncapi-docs-yaml.log \
    )
    [ "$(cat /tmp/asyncapi-docs-yaml.log)" = "$(cat docs-yaml.output)" ]
}


@test "should request json auto spec" {
    cd docs/src/auto_spec
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
    [ "$(cat /tmp/asyncapi-docs-json.log)" = "$(cat docs-json.output)" ] || (\
        echo -e "\n\n\nServer Output (/tmp/asyncapi-docs.log):" && \
        cat /tmp/asyncapi-docs.log && \
        echo -e "\n\n\nEndpoint Output (/tmp/asyncapi-docs-json.log):" && \
        cat /tmp/asyncapi-docs-json.log \
    )
    [ "$(cat /tmp/asyncapi-docs-json.log)" = "$(cat docs-json.output)" ]
}


@test "should publish message http auto spec" {
    cd docs/src/auto_spec
    sed -r -e "s/asyncapi-docs/coverage run -p -m 'asyncapi.docs'/" \
        ./docs.sh > /tmp/asyncapi-docs.sh
    bash /tmp/asyncapi-docs.sh > /tmp/asyncapi-docs.log 2>&1 &
    sleep 1
    run coverage run -p publish_http.py
    sleep 1
    ps ax | grep 'asyncapi.docs' | \
        grep -v -E 'bats|grep' | sed -r -e 's/ ?([0-9]+) .*/\1/g' | \
        xargs kill -SIGTERM 2>/dev/null
    [ "$status" -eq 0 ]
    [ "$output" = "$(cat ../publish.output)" ]
}


@test "should receive message http auto spec" {
    cd docs/src/auto_spec
    sed -r -e "s/asyncapi-docs/coverage run -p -m 'asyncapi.docs'/" \
        ./docs.sh > /tmp/asyncapi-docs.sh
    bash /tmp/asyncapi-docs.sh > /tmp/asyncapi-docs.log 2>&1 &
    sleep 1
    sed -r -e "s/asyncapi-subscriber/coverage run -p -m 'asyncapi.subscriber'/" \
        ./subscriber-http.sh > /tmp/asyncapi-subscriber.sh
    bash /tmp/asyncapi-subscriber.sh > /tmp/asyncapi-subscriber.log &
    sleep 1
    coverage run -p publish_http.py
    sleep 1
    ps ax | grep -E 'asyncapi.docs|asyncapi.subscriber' | \
        grep -v -E 'bats|grep' | sed -r -e 's/ ?([0-9]+) .*/\1/g' | \
        xargs kill -SIGTERM 2>/dev/null
    [ "$(head -2 /tmp/asyncapi-subscriber.log)" = "$(cat ../subscriber-receive-message.output)" ]
}


@test "should publish gcloud-pubsub message http spec" {
    cd docs/src/gcloud_pubsub
    sed -r -e "s/asyncapi-docs/coverage run -p -m 'asyncapi.docs'/" \
        ./docs.sh > /tmp/asyncapi-docs.sh
    bash /tmp/asyncapi-docs.sh > /tmp/asyncapi-docs.log 2>&1 &
    sleep 1
    run coverage run -p publish.py
    sleep 1
    ps ax | grep 'asyncapi.docs' | \
        grep -v -E 'bats|grep' | sed -r -e 's/ ?([0-9]+) .*/\1/g' | \
        xargs kill -SIGTERM 2>/dev/null
    [ "$status" -eq 0 ]
    [ "$output" = "$(cat ../publish.output)" ]
}


@test "should receive gcloud-pubsub message http spec" {
    cd docs/src/gcloud_pubsub
    sed -r -e "s/asyncapi-docs/coverage run -p -m 'asyncapi.docs'/" \
        ./docs.sh > /tmp/asyncapi-docs.sh
    bash /tmp/asyncapi-docs.sh > /tmp/asyncapi-docs.log 2>&1 &
    sleep 1
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


@test "should publish gcloud-pubsub message python spec" {
    cd docs/src/gcloud_pubsub
    run coverage run -p py_spec_publish.py
    echo "$output"
    [ "$status" -eq 0 ]
    [ "$output" = "$(cat ../publish.output)" ]
}


@test "should receive gcloud-pubsub message python spec" {
    cd docs/src/gcloud_pubsub
    sed -r -e "s/asyncapi-subscriber/coverage run -p -m 'asyncapi.subscriber'/" \
        ./py_spec_subscriber.sh > /tmp/asyncapi-subscriber.sh
    bash /tmp/asyncapi-subscriber.sh > /tmp/asyncapi-subscriber.log &
    sleep 1
    coverage run -p py_spec_publish.py
    sleep 1
    ps ax | grep 'asyncapi.subscriber' | \
        grep -v -E 'bats|grep' | sed -r -e 's/ ?([0-9]+) .*/\1/g' | \
        xargs kill -SIGTERM 2>/dev/null
    [ "$(head -2 /tmp/asyncapi-subscriber.log)" = "$(cat ../subscriber-receive-message.output)" ]
}


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
