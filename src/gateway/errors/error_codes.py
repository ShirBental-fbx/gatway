from .types import ErrorStruct


class ErrorHandling:
    UNKNOWN_PLATFORM_ID = ErrorStruct(
        http_status_code=404,
        error_code=1100,
        message_format="Could not find business with id '{}' connected to '{}'",
        quiet=True,
    )

    UNKNOWN_TARGET_PLATFORM_ID = ErrorStruct(
        http_status_code=404,
        error_code=1150,
        message_format="Could not find business with id '{}' connected to '{}'",
        quiet=True,
    )

    INCONCLUSIVE_BUSINESS = ErrorStruct(
        http_status_code=500,
        error_code=1101,
        message_format="Could not determine which business is with id '{}' and connected to '{}'. Contact Fundbox support",
        quiet=False,
    )

    DISCONNECTED_BUSINESS = ErrorStruct(
        http_status_code=500,
        error_code=1102,
        message_format="The business is disconnected from its platform",
        quiet=True,
    )

    EMAIL_NOT_VERIFIED_FOR_BUSINESS = ErrorStruct(
        http_status_code=500,
        error_code=1103,
        message_format="The business' email account is not verified",
        quiet=True,
    )

    BUSINESS_NOT_APPROVED = ErrorStruct(
        http_status_code=500,
        error_code=1104,
        message_format="The business is not approved",
        quiet=True,
    )

    INTERNAL_SERVER_ERROR = ErrorStruct(
        http_status_code=500,
        error_code=1105,
        message_format="Internal server error",
        quiet=True,
    )

    UNKNOWN_PLATFORM_INVOICE_ID = ErrorStruct(
        http_status_code=404,
        error_code=1200,
        message_format="Could not find invoice with id '{}'",
        quiet=True,
    )

    UNKNOWN_PLATFORM = ErrorStruct(
        http_status_code=404,
        error_code=1000,
        message_format="Unknown platform '{}'",
        quiet=False,
    )

    MISSING_PERMISSIONS_FOR_PLATFORM = ErrorStruct(
        http_status_code=401,
        error_code=1001,
        message_format="Missing permissions for platform '{}'",
        quiet=False,
    )

    MISSING_REQUEST_KEYS_PARTNER = ErrorStruct(
        http_status_code=400,
        error_code=1002,
        message_format="Some of the mandatory request keys are missing: {}",
        quiet=False,
    )

    MISSING_PERMISSIONS_FOR_FUSE_PARTNER = ErrorStruct(
        http_status_code=401,
        error_code=1003,
        message_format="Missing permissions for fuse partner '{}'",
        quiet=False,
    )

    MISSING_REQUEST_KEYS = ErrorStruct(
        http_status_code=400,
        error_code=1300,
        message_format="Some of the mandatory request keys are missing, object_type: '{}' object_id: '{}'",
        quiet=False,
    )

    MISSING_HEADERS = ErrorStruct(
        http_status_code=400,
        error_code=400,
        message_format="Missing required header '{}'",
        quiet=False,
    )

    ILLEGAL_FIELDS_FOUND = ErrorStruct(
        http_status_code=400,
        error_code=1301,
        message_format="Only the specified fields can be updated, object_type: '{}' object_id: '{}'",
        quiet=False,
    )

    ILLEGAL_ACTION = ErrorStruct(
        http_status_code=400,
        error_code=1302,
        message_format="Only the specified object types can be updated, object_type: '{}' object_id: '{}'",
        quiet=False,
    )

    UNAUTHORIZED = ErrorStruct(
        http_status_code=401,
        error_code=0,
        message_format="Request is not authorized",
        quiet=False,
    )

    LENDIO_CANNOT_CONTINUE = ErrorStruct(
        http_status_code=500,
        error_code=1190,
        message_format="Can't continue - couldn't retrieve data from Lendio API",
        quiet=False,
    )

    BAD_REQUEST = ErrorStruct(
        http_status_code=400,
        error_code=400,
        message_format="Bad request: {}",
        quiet=False,
    )

    MISSING_PARAMETERS = ErrorStruct(
        http_status_code=422,
        error_code=422,
        message_format="The request sent is syntactically valid JSON, but is missing expected parameters: {}",
        quiet=False,
    )

    TOO_MANY_REQUESTS = ErrorStruct(
        http_status_code=429,
        error_code=429,
        message_format="Rate limit exceeded: {}",
        quiet=False,
    )
