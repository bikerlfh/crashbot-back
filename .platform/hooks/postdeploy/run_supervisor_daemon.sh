#!/usr/bin/env bash
# ref: https://hackernoon.com/setting-up-django-channels-on-aws-elastic-beanstalk-716fd5a49c4a

# Get django environment variables
djangoenv=`export | tr '\n' ',' | sed 's/%/%%/g' | sed 's/export //g' | sed 's/$PATH/%(ENV_PATH)s/g' | sed 's/$PYTHONPATH//g' | sed 's/$LD_LIBRARY_PATH//g'`
djangoenv=${djangoenv%?}

# Create daemon configuraiton script
daemonconf="[program:worker]
; Set full path to program if using virtualenv
command=/var/app/venv/*/bin/python /var/app/current/manage.py runworker channels default
directory=/var/app/current
user=ec2-user
numprocs=1
stdout_logfile=/var/log/stdout_worker.log
stderr_logfile=/var/log/stderr_worker.log
autostart=true
autorestart=true
startsecs=10

; Need to wait for currently executing tasks to finish at shutdown.
; Increase this if you have very long running tasks.
stopwaitsecs = 600

; When resorting to send SIGKILL to the program to terminate it
; send SIGKILL to its whole process group instead,
; taking care of its children as well.
killasgroup=true

; if rabbitmq is supervised, set its priority higher
; so it starts first
priority=998

environment=$djangoenv

[program:daphne]
; Set full path to channels program if using virtualenv
command=/var/app/venv/*/bin/daphne -b 0.0.0.0 -p 5000 aviator_bot_backend.asgi:application
directory=/var/app/current
user=ec2-user
numprocs=1
stdout_logfile=/var/log/stdout_daphne.log
stderr_logfile=/var/log/stderr_daphne.log
autostart=true
autorestart=true
startsecs=10

; Need to wait for currently executing tasks to finish at shutdown.
; Increase this if you have very long running tasks.
stopwaitsecs = 600

; When resorting to send SIGKILL to the program to terminate it
; send SIGKILL to its whole process group instead,
; taking care of its children as well.
killasgroup=true

; if rabbitmq is supervised, set its priority higher
; so it starts first
priority=998

environment=$djangoenv

[supervisorctl]
"

# Create the supervisord conf script
echo "$daemonconf" | sudo tee /etc/supervisor/conf.d/daemon.conf

# Add configuration script to supervisord conf (if not there already)
if ! grep -Fxq "[include]" /etc/supervisor/conf.d/supervisord.conf
    then
    echo "" | sudo tee -a /etc/supervisor/conf.d/supervisord.conf
    echo "[include]" | sudo tee -a /etc/supervisor/conf.d/supervisord.conf
    echo "files: daemon.conf" | sudo tee -a /etc/supervisor/conf.d/supervisord.conf
fi
if ! grep -Fxq "[inet_http_server]" /etc/supervisor/conf.d/supervisord.conf
    then
    echo "" | sudo tee -a /etc/supervisor/conf.d/supervisord.conf
    echo "[inet_http_server]" | sudo tee -a /etc/supervisor/conf.d/supervisord.conf
    echo "port = 127.0.0.1:9001" | sudo tee -a /etc/supervisor/conf.d/supervisord.conf
fi

# Reread the supervisord config
sudo /usr/local/bin/supervisorctl -c /etc/supervisor/conf.d/supervisord.conf reread

# Update supervisord in cache without restarting all services
sudo /usr/local/bin/supervisorctl -c /etc/supervisor/conf.d/supervisord.conf update

# Start/Restart processes through supervisord
sudo /usr/local/bin/supervisorctl -c /etc/supervisor/conf.d/supervisord.conf restart daphne
sudo /usr/local/bin/supervisorctl -c /etc/supervisor/conf.d/supervisord.conf restart worker
# sudo //usr/local/bin/supervisorctl -c /etc/supervisor/conf.d/supervisord.conf restart celeryworker &
# sudo //usr/local/bin/supervisorctl -c /etc/supervisor/conf.d/supervisord.conf restart celeryheartbeat &