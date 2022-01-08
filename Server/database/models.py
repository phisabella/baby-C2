from database.db import db


# "dynamic document" means that we don't need to specify every field.
class Task(db.DynamicDocument):
    task_id = db.StringField(require=True)


class Result(db.DynamicDocument):
    result_id = db.StringField(require=True)

class TaskHistory(db.DynamicDocument):
    task_object = db.StringField()