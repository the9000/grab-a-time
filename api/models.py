"""
API data models for the grab-a-time app.
"""

import base64
import datetime
import random
import re
import typing as T

import pydantic as P
import sqlalchemy.exc as SAExc

# Generic API response model.
PayloadT = T.TypeVar("PayloadT")


class APIResponseOK(P.BaseModel, T.Generic[PayloadT]):
    status: T.Literal["OK"]
    data: PayloadT


class APIResponseError(P.BaseModel):
    status: T.Literal["error"]
    message: str


def api_error(message: str):
    return APIResponseError(status="error", message=message)


# NOTE: We're using this instead of a decorator, because:
# * Having a single decorator return the right signature is tricky.
# * Even then Pydantic is unhappy with the signature, says parameters must be Models.
# * ParamSpec has no way to give a bound to parameters.
# * Workarounds that typecheck in Pyrignat )and_ Pydantic lead to code duplication.
def wrap[R](func: T.Callable[[], R]) -> APIResponseOK[R] | APIResponseError:
    """Calls `func`, wraps the result in OK response, errors in Error response."""
    try:
        return APIResponseOK[R](status="OK", data=func())
    except SAExc.SQLAlchemyError as ex:
        # NOTE: This accesses a private fields to prevent sending too many details in the response.
        return api_error(f"{ex._message()}")
    except Exception as ex:
        return api_error(str(ex))


def b64s_to_int(b64s: str) -> int:
    """Convert a base64 string with stripped padding to int."""
    pad_size = 3 - len(b64s) % 3
    # I could not find a concise way to transform this without going through hex.
    bytes_form = base64.urlsafe_b64decode(b64s + "=" * pad_size)
    return int(bytes_form.hex(), 16)


def int_to_b64s(value: int) -> str:
    """Convert an int (presumable u64) to a base64 string with padding stripped."""
    bytes_form = bytes.fromhex("%016x" % value)
    b64_form = base64.urlsafe_b64encode(bytes_form).decode("ascii")
    return b64_form.rstrip("=")


b64_rx = re.compile(r"^[0-9a-zA-Z_-]+$")


def looks_valid_b64s(s: str) -> str:
    if b64_rx.match(s):
        return s
    raise ValueError(f"{s!r} is not a valid b64s.")


# Name certain types to make things self-documented.
MeetingID = str
Email = str
Minutes = int
DateTimeStr = str  # We pass date/tme in ISO 8601 format.

MeetingTypeID = int

ConnectionType = T.Literal["Phone", "Zoom", "Google Meet", "In person"]

DateTimeParsed = T.Annotated[  # Actually a datetime object.
    DateTimeStr, P.AfterValidator(datetime.datetime.fromisoformat)
]


# Python's way to combine record parts is mixins and inheritance :(
# All mixins are also Pydantic models, even though they don't make sense as
# standalone models.


class MeetingType_Core(P.BaseModel):
    model_config = P.ConfigDict(from_attributes=True)
    name: str
    duration: Minutes
    connection_type: ConnectionType


class MeetingType(MeetingType_Core):
    id: MeetingTypeID
    last_updated: DateTimeParsed


class MeetingInfo_Core(P.BaseModel):
    "Data sufficient to create a meeting."
    model_config = P.ConfigDict(from_attributes=True)
    guest_name: str
    guest_email: Email
    note: str
    start_time: DateTimeParsed


class MeetingInfo_New(P.BaseModel):
    meeting_type_id: MeetingTypeID


def new_meeting_id() -> MeetingID:
    """Returns a new random meeting ID."""
    return int_to_b64s(random.randint(100, 1 << 63))


class MeetingInfo(MeetingInfo_Core):
    "Describes a scheduled meeting."
    id: T.Annotated[MeetingID, P.AfterValidator(looks_valid_b64s)]
    meeting_type: MeetingType
    last_updated: DateTimeParsed
