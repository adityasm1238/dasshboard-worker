import mongoengine as db
from app.constants import Constants

class Users(db.Document):
    username = db.StringField(required=True,unique=True)
    email = db.StringField(required=True,unique=True)
    isVerified = db.BooleanField(default=False)
    password = db.StringField(required=True)
    role = db.StringField(default="user")

class RegisterKeys(db.Document):
    by = db.ReferenceField('Users',required=True)

class UserTasks(db.Document):
    by = db.ReferenceField('Users',required=True)
    usn = db.StringField(required=True,unique_with='by')


class UsnTasks(db.Document):
    usn = db.StringField(required=True,unique=True)
    task_id = db.StringField(required=True,unique=True)
    created = db.DateTimeField(required=True)
    task_status = db.IntField(default=Constants.USER_TASK_RUNNING)

class UsnData(db.Document):
    usn = db.StringField(required=True,unique=True)
    dob = db.StringField(required=True)
    name = db.StringField()
    image = db.StringField()

class FailedUsn(db.Document):
    usn = db.StringField(required=True,unique=True)