from typing import Callable, Any, Optional, List, Union


def run(function: Callable[..., None]) -> None: ...


def echo(message: str) -> None: ...


def Option(
    # Parameter
    default: Optional[Any],
    *,
    envvar: Optional[Union[str, List[str]]] = None,
) -> Any: ...
