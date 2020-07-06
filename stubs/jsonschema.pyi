from typing import Any, Dict


def validate(instance: Dict[str, Any], schema: Dict[str, Any]) -> None:
    ...


class ValidationError(Exception):
    ...
