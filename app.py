from flask import Flask, jsonify
import os
from datetime import datetime, timedelta
import time
import redis
from rq import Queue, Worker, Retry
from rq.job import Job
import utils


app = Flask(__name__)
env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)

redis_url = app.config.get("REDISURL", "redis://localhost:6379")
conn = redis.from_url(redis_url)
q = Queue(connection=conn)

@app.route('/')
def index():
    return jsonify({"Your APP_SETTINGS VARIABLE is " + env_config : " Your REDIS url is: " + redis_url + " 🚅"})


@app.route('/tasks', methods=['GET'])
def queue_tasks():
    job = q.enqueue(utils.print_task, 5, retry=Retry(max=2))
    job2 = q.enqueue_in(timedelta(seconds=10), utils.print_numbers, 5)
    # return created job id
    return "Job IDs: " + str(job.get_id()) + ", " + str(job2.get_id())


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
