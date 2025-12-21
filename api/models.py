"""
API data models for the grab-a-time app.
"""

import typing as T

import pydantic as P

# Generic API response model.
PayloadT = T.TypeVar("PayloadT")

class APIResponseSuccess(P.BaseModel, T.Generic[PayloadT]):
    status: T.Literal["ok"]
    data: PayloadT

class APIResponseError(P.BaseModel):
    status: T.Literal["error"]
    message: str

APIResponse = T.Annotated[
    APIResponseSuccess[PayloadT] | APIResponseError,
    P.Field(discriminator="status")
]

def api_success(payload: PayloadT) -> APIResponseSuccess[PayloadT]:
    return APIResponseSuccess[PayloadT](status="ok", data=payload)

def api_error(message: str):
    return APIResponseError(status="error", message=message)

# Name certain types to make things self-documented.
Email = str
DateTimeStr = str  # We pass date/tme in ISO 8601 format.
Minutes = int
MeetingHandle = str  # The ID string to edit / delete a meeting.


class MeetingInfo(P.BaseModel):
    "Descrives a scheduled meeting."
    guest_name: str
    guest_email: Email
    note: str
    start_time: DateTimeStr
    duration: Minutes
    last_updated: DateTimeStr
    handle: MeetingHandle
    # TODO: Meeting type. ID or flattened data?
