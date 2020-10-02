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


class EmptyServersError(AsyncApiError):
    ...


class ServerNotFoundError(AsyncApiError):
    ...


class InvalidContentTypeError(AsyncApiError):
    ...


class InvalidAsyncApiVersionError(AsyncApiError):
    ...


class InvalidServerBindingError(AsyncApiError):
    ...


class InvalidServerBindingProtocolError(AsyncApiError):
    ...


class InvalidChannelsSubscribersError(AsyncApiError):
    ...


class ChannelPublishNotFoundError(AsyncApiError):
    ...


class GCloudPubSubPublishTimeoutError(AsyncApiError):
    ...


class GCloudPubSubConsumerDisconnectError(AsyncApiError):
    ...
