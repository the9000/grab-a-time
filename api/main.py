"""
API endpoints for grab-a-time.
"""

# TODO: Split into guest.py and owner.py.

import os

from fastapi import FastAPI
import sqlalchemy as SA

import database as D
import models as M

app = FastAPI(
    debug=(os.getenvb(b"GRAB_A_TIME_DEBUG") == b"1"),
    on_startup=(D.create_schema,),
    title="Grab-A-Time",
)

# TODO: set up the schema on startup if absent.

def mock_get_meeting_list():
    return [
        M.MeetingInfo(
            id=M.new_meeting_id(),
            guest_name="Joe Random",
            guest_email="joe@ran.dom",
            note="Hard-coded.",
            start_time="2025-12-19 12:45:00-05",
            last_updated="2025-12-18 23:45:12-05",
            meeting_type=M.MeetingType(
                name="Short Zoom",
                connection_type="Zoom",
                duration=15,
                id=1,
                last_updated="2025-12-01 23:45:12-05",
            )
        ),
    ]

@app.get("/my/meeting/")
def meeting_list(): # -> M.APIResponseOK[list[M.MeetingInfo]] | M.APIResponseError:
    return M.api_success(mock_get_meeting_list())


@app.post("/my/meeting/")
def meeting_create(data: M.MeetingInfo_Core):
    pass


@app.get("/my/meeting-type/")
def meeting_type_list():
    with D.ro_transaction() as tx:
        data = tx.connection.execute(
            SA.select(D.MeetingType).order_by(D.MeetingType.c.name)
        ).all()
        return [
            M.MeetingType(
                id=x.id,
                name=x.name,
                duration=x.duration,
                connection_type=x.connection_type,
                last_updated=x.last_updated)
            for x in data
        ]



# No main, intended for `fastapi run`.
