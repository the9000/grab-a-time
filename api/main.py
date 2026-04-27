"""
API endpoints for grab-a-time.
"""

# TODO: Maybe Split into guest.py and owner.py.

import contextlib
import logging
import os

from fastapi import FastAPI

from . import database as D
from . import actions

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    log = logging.getLogger("lifespan")
    log.info("Running app startup.")
    D.create_schema()
    yield
    log.info("Running app shutdown.")

app = FastAPI(
    debug=(os.getenvb(b"GRAB_A_TIME_DEBUG") == b"1"),
    lifespan=lifespan,
    title="Grab-A-Time",
)

# All routing in one place.
app.get("/my/meeting/")(actions.meeting.get_list)
app.post("/my/meeting/")(actions.meeting.create)

app.get("/my/meeting-type/")(actions.meeting_type.get_list)
app.post("/my/meeting-type/")(actions.meeting_type.create)
app.delete("/my/meeting-type/{record_id}")(actions.meeting_type.delete)
app.put("/my/meeting-type/{record_id}")(actions.meeting_type.update)

# No main(), intended for `fastapi run`.
