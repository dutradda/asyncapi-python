#!/usr/bin/env bats


@test "should request html docs from auto spec module" {
    cd docs/src/auto_spec/module
    sed -r -e "s/asyncapi-docs/coverage run -p -m 'asyncapi.docs'/" \
        ./docs.sh > /tmp/asyncapi-docs.sh
    bash /tmp/asyncapi-docs.sh > /tmp/asyncapi-docs.log 2>&1 &
    sleep 2
    curl -i localhost:5000/docs \
        > /tmp/asyncapi-docs-html.log \
        2> /dev/null
    ps ax | grep 'asyncapi.docs' | \
        grep -v -E 'bats|grep' | sed -r -e 's/ ?([0-9]+) .*/\1/g' | \
        xargs kill -SIGTERM 2>/dev/null
    sleep 1
    sed -i -r -e 's/date: .*/date: .../g' /tmp/asyncapi-docs-html.log
    [ "$(cat /tmp/asyncapi-docs-html.log)" = "$(cat docs-html.output)" ] || (\
        echo -e "\n\n\nServer Output (/tmp/asyncapi-docs.log):" && \
        cat /tmp/asyncapi-docs.log && \
        echo -e "\n\n\nEndpoint Output (/tmp/asyncapi-docs-html.log):" && \
        cat /tmp/asyncapi-docs-html.log \
    )
    [ "$(cat /tmp/asyncapi-docs-html.log)" = "$(cat docs-html.output)" ]
}


@test "should request html docs from gcloud pubsub spec" {
    cd docs/src/gcloud_pubsub
    sed -r -e "s/asyncapi-docs/coverage run -p -m 'asyncapi.docs'/" \
        ./docs.sh > /tmp/asyncapi-docs.sh
    bash /tmp/asyncapi-docs.sh > /tmp/asyncapi-docs.log 2>&1 &
    sleep 2
    curl -i localhost:5000/docs \
        > /tmp/asyncapi-docs-html.log \
        2> /dev/null
    ps ax | grep 'asyncapi.docs' | \
        grep -v -E 'bats|grep' | sed -r -e 's/ ?([0-9]+) .*/\1/g' | \
        xargs kill -SIGTERM 2>/dev/null
    sleep 1
    sed -i -r -e 's/date: .*/date: .../g' /tmp/asyncapi-docs-html.log
    [ "$(cat /tmp/asyncapi-docs-html.log)" = "$(cat docs-html.output)" ] || (\
        echo -e "\n\n\nServer Output (/tmp/asyncapi-docs.log):" && \
        cat /tmp/asyncapi-docs.log && \
        echo -e "\n\n\nEndpoint Output (/tmp/asyncapi-docs-html.log):" && \
        cat /tmp/asyncapi-docs-html.log \
    )
    [ "$(cat /tmp/asyncapi-docs-html.log)" = "$(cat docs-html.output)" ]
}


@test "should request html docs from spec containing tags" {
    cd docs/src/html_spec
    sed -r -e "s/asyncapi-docs/coverage run -p -m 'asyncapi.docs'/" \
        ./docs-tags.sh > /tmp/asyncapi-docs.sh
    bash /tmp/asyncapi-docs.sh > /tmp/asyncapi-docs.log 2>&1 &
    sleep 2
    curl -i localhost:5000/docs \
        > /tmp/asyncapi-docs-html.log \
        2> /dev/null
    ps ax | grep 'asyncapi.docs' | \
        grep -v -E 'bats|grep' | sed -r -e 's/ ?([0-9]+) .*/\1/g' | \
        xargs kill -SIGTERM 2>/dev/null
    sleep 1
    sed -i -r -e 's/date: .*/date: .../g' /tmp/asyncapi-docs-html.log
    [ "$(cat /tmp/asyncapi-docs-html.log)" = "$(cat docs-html-tags.output)" ] || (\
        echo -e "\n\n\nServer Output (/tmp/asyncapi-docs.log):" && \
        cat /tmp/asyncapi-docs.log && \
        echo -e "\n\n\nEndpoint Output (/tmp/asyncapi-docs-html.log):" && \
        cat /tmp/asyncapi-docs-html.log \
    )
    [ "$(cat /tmp/asyncapi-docs-html.log)" = "$(cat docs-html-tags.output)" ]
}
