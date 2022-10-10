#!/bin/bash
gunicorn app:app --daemon
rq worker --with-scheduler
