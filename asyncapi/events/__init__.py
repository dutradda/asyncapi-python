from typing import Any, Dict, Optional

from broadcaster import Event as BroadcasterEvent


class Event(BroadcasterEvent):
    def __init__(
        self,
        channel: str,
        message: Any,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(channel, message)

        if context is None:
            context = {}

        self.context = context
