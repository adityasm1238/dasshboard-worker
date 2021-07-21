from datetime import datetime
from functools import partial

from app import celery,fernet
from app.scraper import Scraper
from app.models import UsnData,UsnTasks,FailedUsn
from app.constants import Constants


@celery.task(bind=True)
def bruteforce(self,usn):
    newTask = UsnTasks(usn=usn,task_id=str(self.request.id),created=datetime.utcnow())
    newTask.save()
    cb = partial(callBack,instance=self)
    details = Scraper.findDob(usn,publishProgres=cb)
    if not details:
        failed = FailedUsn(usn=usn)
        failed.save()
        UsnTasks.objects(usn=usn).update(set__task_status=Constants.USER_TASK_FAILED)
        return {'current': (367*3), 'total': (367*3), 'status': 'failed'}
    details['dob'] = fernet.encrypt(details['dob'].encode())
    details['usn'] = usn
    usnData = UsnData(**details)
    usnData.save()
    UsnTasks.objects(usn=usn).update(set__task_status=Constants.USER_TASK_SUCCESS)
    return {'current': (367*3), 'total': (367*3), 'status': 'success'}

def callBack(instance,cur,msg):
    instance.update_state(state='PROGRESS',
                          meta={'current': cur, 'total': (367*3),
                                'status': msg})