"""
API data models for the grab-a-time app.
"""

import base64
import datetime
import random
import re
import typing as T

import pydantic as P

# Generic API response model.
PayloadT = T.TypeVar("PayloadT")


class APIResponseOK(P.BaseModel, T.Generic[PayloadT]):
    status: T.Literal["OK"]
    data: PayloadT


class APIResponseError(P.BaseModel, T.Generic[PayloadT]):
    status: T.Literal["error"]
    message: str


# NOTE: Sadly, we can't have a nice APIResponse = APIResponseOK | APIResponseError,
# because it loses the generic type parameter.


def api_success(payload: PayloadT) -> APIResponseOK[PayloadT]:
    return APIResponseOK[PayloadT](status="OK", data=payload)


def api_error(message: str):
    return APIResponseError(status="error", message=message)


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

DateTimeParsed = T.Annotated[  # Actually a datetime object.
    DateTimeStr,
    P.AfterValidator(datetime.datetime.fromisoformat)
]

def new_meeting_id() -> MeetingID:
    return int_to_b64s(random.randint(100, 1 << 63))

class MeetingInfo(P.BaseModel):
    "Describes a scheduled meeting."
    id: T.Annotated[MeetingID, P.AfterValidator(looks_valid_b64s)]
    guest_name: str
    guest_email: Email
    note: str
    start_time: DateTimeParsed  #
    duration: Minutes
    last_updated: DateTimeParsed
    # TODO: Meeting type. ID or flattened data?
