import json
from typing import Any, Dict, List, Optional

import markdown


def contain_tags(obj: Any, tags_to_check: Any) -> bool:
    if not obj:
        raise Exception("object for containsTag was not provided?")

    if not tags_to_check:
        raise Exception("tags_to_check for containsTag was not provided?")

    # Ensure if only 1 tag are provided it is converted to array.
    if tags_to_check and not isinstance(tags_to_check, list):
        tags_to_check = [tags_to_check]

    # Check if pubsub contain one of the tags to check.
    def check(tag: Any) -> bool:
        found = False
        for tag_to_check in tags_to_check:
            if tag_to_check.name() == tag.name():
                found = True

        return found

    # Ensure tags are checked for the group tags
    return any(map(check, obj.tags())) if obj.tags() else False


def contain_no_tag(channels: Any, tags_to_check: Any) -> bool:
    if not channels:
        raise Exception("Channels for containNoTag was not provided?")

    for _, channel in channels:
        # Check if the channel contains publish or subscribe which does not contain tags
        if (channel.publish() and not channel.publish().tags()) or (
            channel.subscribe() and not channel.subscribe().tags()
        ):
            return True

        # Check if channel publish or subscribe does not contain one of the tags to check.
        def check(tag: Any) -> bool:
            found = False
            for tag_to_check in tags_to_check:
                if tag_to_check.name == tag.name:
                    found = True

            return found

        # Ensure pubsub tags are checked for the group tags
        publish_contains_no_tag = (
            any(map(check, channel.publish().tags()))
            if channel.publish() and channel.publish().tags()
            else False
        )
        if publish_contains_no_tag:
            return True

        subscribe_contains_no_tag = (
            any(map(check, channel.subscribe().tags()))
            if channel.subscribe() and channel.subscribe().tags()
            else False
        )
        if subscribe_contains_no_tag:
            return True

    return False


def split(value: str, split_value: str) -> List[str]:
    for split_i in split_value:
        if split_i in value:
            return value.split(split_i)

    return [value]


def markdown2html(value: str) -> str:
    if value:
        return markdown.Markdown().convert(value)

    return ''


def is_expandable(obj: Any) -> bool:
    if not obj:
        return False

    if (
        obj.type() == 'object'
        or obj.type() == 'array'
        or obj.oneOf()
        or obj.anyOf()
        or obj.allOf()
        or obj.items()
        or obj.additionalItems()
        or obj.properties()
        or obj.additionalProperties()
        or (
            obj.extensions()
            and any([e.startswith('x-parser-') for e in obj.extensions()])
        )
        or obj.patternProperties()
    ):
        return True

    return False


def dump(value: Any, indent: Optional[int] = None) -> str:
    if indent:
        return json.dumps(value, indent=indent)

    return json.dumps(value)


def non_parser_extensions(schema: Any) -> Any:
    if not schema:
        return {}

    if schema and not schema.extensions():
        return {}

    extensions = schema.extensions()

    return {
        k: v for k, v in extensions.spec if not k.startswith('x-parser-') and v
    }


def is_object(value: Any) -> bool:
    return isinstance(value, dict) or hasattr(value, 'spec')


def is_array(value: Any) -> bool:
    return isinstance(value, list)


def keys(value: Dict[str, Any]) -> List[str]:
    return list(value.keys())


def head(value: List[Any]) -> Any:
    return value[0]


def get_payload_examples(message: Any) -> List[Any]:
    return list(message.spec.get('examples', {}).values())


def generate_example(schema: Any, dumps_schema: bool = True) -> Any:
    schema_type = schema.get('type')
    schema_enum = schema.get('enum')
    example: Any = {}

    if schema_enum:
        example = schema_enum[0]

    elif schema_type == 'object' or schema_type is None:
        for prop_name, prop_schema in schema.get('properties', {}).items():
            example[prop_name] = generate_example(prop_schema, False)

        for prop_name, prop_schema in schema.get(
            'patternProperties', {}
        ).items():
            example[prop_name] = generate_example(prop_schema, False)

    elif schema_type == 'array':
        items_schema = schema.get('items', {})

        if items_schema:
            example = [generate_example(items_schema, False)]
        else:
            example = ['anyValue', {'any': 'value'}]

    elif schema_type == 'string':
        example = 'string value'

    elif schema_type == 'integer':
        example = 1

    elif schema_type == 'number':
        example = 0.1

    elif schema_type == 'boolean':
        example = True

    if dumps_schema:
        return json.dumps(example, indent=2)

    return example


def get_headers_examples(message: Any) -> List[Any]:
    headers = message.spec.get('headers', {})

    if not headers:
        return []

    return [
        example
        for header in headers
        for example in header.get('examples')
        if header.get('examples')
    ]


def boolean(value: Any) -> bool:
    if value is True:
        return True

    return False
