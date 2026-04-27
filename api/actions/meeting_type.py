"""Actions on meeting types."""
import arrow
import sqlalchemy as SA

from .. import database as D
from .. import models as M

def get_list() ->  (M.APIResponseOK[list[M.MeetingType]] | M.APIResponseError):
    def run():
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
    return M.wrap(run)


def create(data: M.MeetingType_Core):
    def run():
       with D.transaction() as tx:
           result = tx.connection.execute(
               D.MeetingType.insert().values(
                   name=data.name,
                   duration=data.duration,
                   connection_type=data.connection_type,
                   last_updated=arrow.now().datetime,
               )
               .returning(D.MeetingType.c.id)
           )
           return M.IDResult[M.MeetingTypeID](id=result.all()[0][0])
    return M.wrap(run)


def update(record_id: int, data: M.MeetingType_Core):
    def run():
       with D.transaction() as tx:
           # TODO: DA a select for update first.
           result = tx.connection.execute(
               D.MeetingType.update()
               .where(D.MeetingType.c.id == record_id)
               .values(
                   name=data.name,
                   duration=data.duration,
                   connection_type=data.connection_type,
                   last_updated=arrow.now().datetime,
               )
           )
           D.assume_single_row_result(result, record_id)
    return M.wrap(run)

def delete(record_id: int):
    def run():
       with D.transaction() as tx:
           # TODO: check which meetings still have this meeting type!
           # We could allow cascading for meetings in the past.
           result = tx.connection.execute(
               D.MeetingType.delete().where(D.MeetingType.c.id == record_id)
           )
           # TODO: Factor out this logic.
           D.assume_single_row_result(result, record_id)
    return M.wrap(run)
