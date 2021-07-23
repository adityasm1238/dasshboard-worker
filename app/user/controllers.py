from os import name
from flask import Blueprint,request,jsonify
from flask_jwt_extended import get_jwt_identity,jwt_required
from datetime import datetime,timedelta

from app.error import handleErrors
from app.models import UserTasks,UsnData,UsnTasks,FailedUsn
from app.tasks import bruteforce
from app.constants import Constants
from app.scraper import Utils

user = Blueprint('user',__name__,url_prefix='/user')


@user.route('/task',methods=['POST'])
@jwt_required()
@handleErrors()
def task():
    data = request.get_json()
    userTask = UserTasks.objects(by=get_jwt_identity(),usn=data['usn'])
    if not userTask:
        userTask = UserTasks(by=get_jwt_identity(),usn=data['usn'])
        userTask.save()
    usnData = UsnData.objects(usn=data['usn'])
    if not usnData:
        failedData = FailedUsn.objects(usn=data['usn']).first()
        if not failedData:
            runningTask = UsnTasks.objects(usn=data['usn']).first()
            if not runningTask:
                task = bruteforce.delay(data['usn'])
                return {'task_code':2,'task_id':task.id},200
            if runningTask.created - datetime.utcnow()>timedelta(days=1):
                runningTask.delete()
                task = bruteforce.delay(data['usn'])
                return {'task_code':2,'task_id':task.id},200
            return {'task_code':2,'task_id':runningTask.task_id},200
        return {'task_code':1},200
    return {'task_code':0},200

@user.route('/status',methods=['POST'])
@jwt_required()
@handleErrors()
def status():
    data = request.get_json()
    task_ids = data['task_ids']
    res = {}
    usnTasks = UsnTasks.objects(task_id__in=task_ids)
    if len(usnTasks)>0:
        for usnTask in usnTasks:
            task = bruteforce.AsyncResult(str(usnTask.task_id))
            res[str(usnTask.task_id)] = Utils.getStatus(task)
            if usnTask.task_status!=Constants.USER_TASK_RUNNING:
                task.forget()
                try:
                    task_ids.remove(str(usnTask.task_id))
                except:
                    pass
                if usnTask.task_status==Constants.USER_TASK_FAILED:
                    res[str(usnTask.task_id)]= {
                        'state': "FAILED",
                        'per': 100,
                        'status': 'Couldn\'t unlock',
                        'usn':usnTask.usn
                    }
                else:
                    usnData = UsnData.objects(usn=usnTask.usn).exclude('dob').first()
                    if usnData:
                        res[str(usnTask.task_id)]= {
                            'state': "SUCCESS",
                            'per': 100,
                            'status': 'Done',
                            'usn':usnData.usn,
                            'result' : usnData.name
                        }
    for task_id in task_ids:
        task = bruteforce.AsyncResult(task_id)
        res[str(task_id)] = Utils.getStatus(task)
    return jsonify(res)

    