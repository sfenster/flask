#=========API TASK QUEUE WEB APPLICATION=========
#This web app mimics the Zapier API bridge.
#
#Pre-designed API actions like "register" and "search" are grouped and stored as JSON "workflows"
#together with their required and optional fields. A single workflow can be made up of
#multiple actions that enqueue into separately run tasks.
#
#The system expects incomng GET or POST webhooks matching a given workflow file name
#(e.g. "http://example.com/webhook/register" matches "register.json" workflow file.)
#The requests can carry either ordinary key/value parameters or a JSON payload.
#
#The app.route receives the request and validates that it matches a workflow file, then calls
#"validate_workflow" from handler.py.
#
#The central function "run_workflow" validates the incoming parameters or JSON payload
#against the expected fields, and then enqueues the relevant workflow actions onto an asynchronous Redis queue.
#The workflow tasks enqueue as the JSON argument "actions", and the original webhook parameters
#enqueue as the JSON "webhook_data" argument.
#
#The rest of the functions in "handler.py" parse the action type and platform and call the correct API.
#For example, an action "registration" and platform "swoogo" would feed the correct
#webhook data into Swoogo's registration API. All API information is stored in functions in the
#"actions" folder. The API keys are stored in dotenv environment variables.




from flask import Flask,request,json,jsonify
import os
import requests
from datetime import datetime, timedelta
import time
import redis
from rq import Queue, Worker, Retry
from rq.job import Job
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from pathlib import Path


app = Flask(__name__)
env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

redis_url = app.config.get("REDISURL", "redis://localhost:6379")
postgres_url = app.config.get("SQLALCHEMY_DATABASE_URI", "postgresql:///wordcount_dev")
conn = redis.from_url(redis_url)
q = Queue(connection=conn)
FILE_DIR = Path(__file__).resolve().parent


#============= DELAYED IMPORTS TO AVOID CIRCULARITY ===============
import utils
from handler import validate_workflow


#============= APP ROUTES ===============
@app.route('/')
def index():
    return jsonify({"Your APP_SETTINGS VARIABLE is " + env_config : "REDIS url: " + redis_url + ", Postgres URL = " + postgres_url})


@app.route('/tasks', methods=['GET'])
def queue_tasks():
    job = q.enqueue(utils.print_task, 5, retry=Retry(max=2))
    job2 = q.enqueue_in(timedelta(seconds=10), utils.print_numbers, 5)
    # return created job id
    return "Job IDs: " + str(job.get_id()) + ", " + str(job2.get_id())


@app.route('/db-migrate', methods=['POST'])
def migrate():
    job = q.enqueue(utils.db_migrate)
    # return created job id
    return "Job ID: " + str(job.get_id())


@app.route('/webhook/<path:path>', methods=['GET', 'POST'])
def webhooks_trigger(path):
    config_path = FILE_DIR / f"workflows/{path}.json"
    if config_path.is_file():
        type = request.headers['Content-Type'] if 'Content-Type' in request.headers else ""
        if "json" in type:
            resp = validate_workflow(path, request.json)
            return f"Success! We have found the workflow '{path}' and received the following JSON post: \n{request.json} \n \
                Webhook response = {resp}"
        else:
            resp = validate_workflow(path, request.args)
            return f"Success! We have found the workflow '{path}' and received the following post parameters: \n{request.args} \n \
                Webhook response = {resp}"

    return f"Workflow: {config_path} not found"


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
