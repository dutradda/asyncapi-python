class AsyncApiError(Exception):
    ...


class ReferenceNotFoundError(AsyncApiError):
    ...


class InvalidChannelError(AsyncApiError):
    ...


class OperationIdNotFoundError(AsyncApiError):
    ...


class ChannelOperationNotFoundError(AsyncApiError):
    ...


class UrlRequiredError(AsyncApiError):
    ...


class ChannelRequiredError(AsyncApiError):
    ...
