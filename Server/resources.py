import uuid
import json

from flask import request, Response
from flask_restful import Resource
from database.db import initialize_db
from database.models import Task, Result, TaskHistory


class Tasks(Resource):
    # list tasks
    def get(self):
        # 将model对象转化为json格式
        tasks = Task.objects().to_json()
        return Response(tasks, mimetype="application/json", status=200)

    # #add tasks
    def post(self):
        body = request.get_json()
        # dump 将obj转化为JSON字符串
        # loads将 包含JSON的转化为py obj
        json_obj = json.loads(json.dumps(body))
        obj_num = len(body)
        for i in range(obj_num):
            json_obj[i]['task_id'] = str(uuid.uuid4())
            # 可以将不定数量的参数传递给一个函数 ,* = tuple , ** = dict
            Task(**json_obj[i]).save()
            task_options = []
            for key in json_obj[i].keys():
                if (key != "task_type" and key != "task_id"):
                    task_options.append(key + ":" + json_obj[i][key])
            TaskHistory(
                task_id=json_obj[i]['task_id'],
                task_type=json_obj[i]['task_type'],
                task_object=json.dumps(json_obj),
                task_options=task_options,
                task_results=""
            ).save()
        # Return the last Task objects that were added
        # skip 应该是忽略其他的？？？？？？？？？？？？？？？
        return Response(Task.objects.skip(Task.objects.count() - obj_num).to_json(),
                        mimetype="application/json",
                        status=200)


class Results(Resource):
    def get(self):
        results = Result.objects().to_json()
        return Response(results, mimetype="application/json", status=200)

    def post(self):
        if str(request.get_json()) != '{}':
            body = request.get_json()
            print("Received implant response: {}".format(body))
            json_obj = json.loads(json.dumps(body))
            json_obj['result_id'] = str(uuid.uuid4())
            Result(**json_obj).save()
            tasks = Task.objects().to_json()
            Task.objects().delete()
            return Response(tasks, mimetype="application/json", status=200)
        else:
            tasks = Task.objects().to_json()
            Task.objects().delete()
            return Response(tasks, mimetype="application/json", status=200)


class History(Resource):
    def get(self):
        task_history = TaskHistory.objects().to_json()
        results = Result.objects().to_json()
        json_obj = json.loads(results)
        result_obj_collection = []
        # Format each result from the implant to be more friendly for consumption/display
        for i in range(len(json_obj)):
            for field in json_obj[i]:
                result_obj = {
                    "task_id": field,
                    "task_results": json_obj[i][field]
                }
                result_obj_collection.append(result_obj)
        for result in result_obj_collection:
            if TaskHistory.objects(task_id=result['task_id']):
                TaskHistory.objects(task_id=result["task_id"]).update_one(
                    set__task_results=result["task_results"]
                )
        return Response(task_history, mimetype="application/json", status=200)
