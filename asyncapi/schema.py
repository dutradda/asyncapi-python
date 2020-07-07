from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Type,
    Union,
    get_type_hints,
)


def type_as_jsonschema(python_type: Type[Any]) -> Dict[str, Any]:
    if python_type is Any:
        return {}

    schema_type = SCALARS.get(python_type)

    if schema_type is None:
        origin = getattr(python_type, '__origin__', None)

        if origin is List or origin is Sequence or origin is Iterable:
            return {
                'type': 'array',
                'items': type_as_jsonschema(python_type.__args__[0]),
            }

        return build_object_schema(python_type)

    return {'type': schema_type}


def build_object_schema(python_type: Type[Any]) -> Dict[str, Any]:
    type_hints = get_type_hints(python_type)

    schema = {
        'type': 'object',
        'properties': {
            attr_name: {
                'anyOf': [
                    type_as_jsonschema(arg)
                    for arg in getattr(attr_type, '__args__', ())
                ]
            }
            if getattr(attr_type, '__origin__', None) is Union
            else type_as_jsonschema(attr_type)
            for attr_name, attr_type in type_hints.items()
        },
    }
    required = [
        attr_name
        for attr_name, attr_type in type_hints.items()
        if not getattr(attr_type, '__origin__', None) is Optional
    ]

    if required:
        schema['required'] = required

    return schema


SCALARS = {
    int: 'integer',
    str: 'string',
    float: 'number',
    bool: 'boolean',
}
