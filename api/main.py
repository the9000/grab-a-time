"""
API endpoints for grab-a-time.
"""

# TODO: Split into guest.py and owner.py.

import os

from fastapi import FastAPI

import models as M


app = FastAPI(debug=(os.getenvb(b"GRAB_A_TIME_DEBUG") == b"1"))

@app.get("/my/meeting/")
def meeting_list() -> M.APIResponse[list[M.MeetingInfo]]:
    return M.api_success([M.MeetingInfo(
        guest_name="Joe Random",
        guest_email="joe@ran.dom",
        note="Hard-coded.",
        start_time="2025-12-19 12:34:00-05",
        duration=30,
        last_updated="2025-12-18 23:45:12-05",
        handle="094093840293",
    )])

# No main, intended for `fastapi run`.
