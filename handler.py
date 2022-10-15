import json
import requests
from flask import jsonify
from pathlib import Path
import redis
from rq import Queue, Worker, Retry
from actions import swoogo_api
from app import app


redis_url = app.config.get("REDISURL", "redis://localhost:6379")
FILE_DIR = Path(__file__).resolve().parent
conn = redis.from_url(redis_url)
q = Queue(connection=conn)



def validate_workflow(name, webhook_data):
    #Get path of json workflow file matching webhook path, load file, get actions, validate, call enqueue_action() to run
    workflow_path = FILE_DIR / f"workflows/{name}.json"
    with open(workflow_path) as f:
        config = json.load(f)

    actions = config["actions"]
    enqueued_jobs = []
    errors = []
    for action in actions:
        rf = action['action_data']['required_fields'] if 'required_fields' in action['action_data'] else {}
        of = action['action_data']['optional_fields'] if 'optional_fields' in action['action_data'] else {}
        error = False
        for f in rf:
            if f not in webhook_data:
                print(f"ERROR: missing required field {f}; {action['type']} action not enqueued.")
                errors.append({action['type']: f"ERROR: missing required field '{f}'; '{action['type']}' action not enqueued."})
                error=True
                break

        for d in webhook_data:
            if d not in of and d not in rf:
                print(f"ERROR: {d} is not an allowed field; {action['type']} action not enqueued.")
                errors.append({action['type']: f"ERROR: '{d}' is not an allowed field; '{action['type']}' action not enqueued."})
                error = True
                break

        if error == False:
            job = q.enqueue_call(
                func=run_actions, args=(action, webhook_data,), result_ttl=5000
            )
            enqueued_jobs.append({action['type']:job.get_id()})
    for job in enqueued_jobs: print(f"JOB: {job}")
    return {"enqueued_jobs": enqueued_jobs, "errors": errors}



#HANDLER.RUN_ACTIONS will be the job enqueued in all cases.
#RUN_ACTIONS will be passed both the webhook info and action step info, and determine which APIs to call

def run_actions(action, webhook_data):
    #Parse the json passed in the parameter for the action and the webhook data, call appropriate function below
    #e.g., run_add_registrant_action()

    if action['type'] == "registration":
        resp = run_add_registrant_action(action['action_data'], webhook_data)
        return {
            #"statusCode": resp['status'],
            "headers": {
                "Content-Type": "application/json",
            },
            "body": {"action" : action, "webhook_data": webhook_data, "response": resp},
        }

def run_add_registrant_action(action_data, webhook_data):
    #Use passed data to determine whose APIs to call, ensure required fields exist, then add registrant.
    if webhook_data['platform']=='swoogo':
        resp = swoogo_api.add_registrant(action_data, webhook_data)
    else:
        resp = "No add registrant action found"
    return resp
