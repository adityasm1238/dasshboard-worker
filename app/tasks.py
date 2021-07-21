from datetime import datetime
from functools import partial

from app import celery,fernet
from app.scraper import Scraper
from app.models import UsnData,UsnTasks,FailedUsn


@celery.task(bind=True)
def bruteforce(self,usn):
    newTask = UsnTasks(usn=usn,task_id=str(self.request.id),created=datetime.utcnow())
    newTask.save()
    cb = partial(callBack,instance=self)
    dob = Scraper.findDob(usn,publishProgres=cb)
    if not dob:
        failed = FailedUsn(usn=usn)
        failed.save()
        UsnTasks.objects(usn=usn).delete()
        return {'current': (367*3), 'total': (367*3), 'status': 'failed'}
    encrypted = fernet.encrypt(dob.encode())
    usnData = UsnData(usn=usn,dob=encrypted)
    usnData.save()
    UsnTasks.objects(usn=usn).delete()
    return {'current': (367*3), 'total': (367*3), 'status': 'success'}

def callBack(instance,cur,msg):
    instance.update_state(state='PROGRESS',
                          meta={'current': cur, 'total': (367*3),
                                'status': msg})