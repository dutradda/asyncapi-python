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


class UrlOrModuleRequiredError(AsyncApiError):
    ...


class InvalidJsonSchemaTypeError(AsyncApiError):
    ...


class InvalidMessageError(AsyncApiError):
    ...
