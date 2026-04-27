"""Meeting actions."""

import sqlalchemy as SA

from .. import database as D
from .. import models as M

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



def get_list()-> M.APIResponseOK[list[M.MeetingInfo]] | M.APIResponseError:
    return M.wrap(mock_get_meeting_list)


def create(data: M.MeetingInfo_Core):
    pass # with D.transaction() as tx:
