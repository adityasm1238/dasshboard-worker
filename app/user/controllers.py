from os import name
from flask import Blueprint,request,jsonify
from flask_jwt_extended import get_jwt_identity,jwt_required
from datetime import datetime,timedelta

from app.error import handleErrors
from app.models import UserTasks,UsnData,UsnTasks,FailedUsn
from app.tasks import bruteforce
from app.constants import Constants

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

@user.route('/status',methods=['GET'])
@jwt_required()
@handleErrors()
def status():
    data = request.get_json()
    task = bruteforce.AsyncResult(data['task_id'])
    usnTask = UsnTasks.objects(task_id=data['task_id'])
    if usnTask:
        if usnTask.task_status!=Constants.USER_TASK_RUNNING:
            task.forget()
            if usnTask.task_status==Constants.USER_TASK_FAILED:
                return  {
                    'state': "FAILED",
                    'current': 1,
                    'total': 1,
                    'status': 'Couldn\'t unlock'
                }
            else:
                usnData = UsnData(usn=usnTask.usn).exclude('dob').first()
                if usnData:
                    return {
                        'state': "SUCCESS",
                        'current': 1,
                        'total': 1,
                        'status': 'Done',
                        'result' : usnData.name
                    }

    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)

    