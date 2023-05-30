#!/usr/bin/env bash
# ref: https://hackernoon.com/setting-up-django-channels-on-aws-elastic-beanstalk-716fd5a49c4a
#!/bin/bash

# If you want to have more than one application, and in just one of them to run the supervisor, uncomment the lines below, 
# and add the env variable IS_WORKER as true in the EBS application you want the supervisor

#if [ "${IS_WORKER}" != "true" ]; then
#    echo "Not a worker. Set variable IS_WORKER=true to run supervisor on this instance"
#    exit 0
#fi

echo "Supervisor - starting setup"
. /opt/elasticbeanstalk/deployment/env


if [ ! -f /usr/local/bin/supervisord ]; then
    echo "installing supervisor"
    sudo yum install pip
    sudo pip install supervisor
else
    echo "supervisor already installed"
fi

if [ ! -d /etc/supervisor ]; then
    mkdir /etc/supervisor
    echo "create supervisor directory"
fi

if [ ! -d /etc/supervisor/conf.d ]; then
    mkdir /etc/supervisor/conf.d
    echo "create supervisor configs directory"
fi

config_file="/etc/supervisor/supervisord.conf"

# Verificar si el archivo existe
if [ -f "$config_file" ]; then
    echo "Config file already exists"
else
    echo "Config file created."
    touch "$config_file"
fi

#. /opt/elasticbeanstalk/deployment/env && cat .ebextensions/supervisor/supervisord.conf > /etc/supervisor/supervisord.conf
#. /opt/elasticbeanstalk/deployment/env && cat .ebextensions/supervisor/supervisord.conf > /etc/supervisord.conf
#. /opt/elasticbeanstalk/deployment/env && cat .ebextensions/supervisor/supervisor_laravel.conf > /etc/supervisor/conf.d/supervisor_laravel.conf

#if ps aux | grep "[/]usr/local/bin/supervisord"; then
#    echo "supervisor is running"
#else
#    echo "starting supervisor"
#    /usr/local/bin/supervisord
#fi

# /usr/local/bin/supervisorctl reread
# /usr/local/bin/supervisorctl update

#echo "Supervisor Running!"

# Get django environment variables
djangoenv=`export | tr '\n' ',' | sed 's/declare -x //g'  | sed 's/%/%%/g' | sed 's/export //g' | sed 's/$PATH/%(ENV_PATH)s/g' | sed 's/$PYTHONPATH//g' | sed 's/$LD_LIBRARY_PATH//g'`
djangoenv=${djangoenv%?}

# Create daemon configuraiton script
daemonconf="[program:worker]
; Set full path to program if using virtualenv
command=/bin/bash -c 'source /var/app/venv/*/bin/activate && python /var/app/current/manage.py runworker channels default --settings=$DJANGO_SETTINGS_MODULE'
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

; environment=$djangoenv

[program:daphne]
; Set full path to channels program if using virtualenv
command=/bin/bash -c 'source /var/app/venv/*/bin/activate && daphne -b 0.0.0.0 -p 5000 aviator_bot_backend.asgi:application'
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

; environment=$djangoenv
"

# Create the supervisord conf script
echo "$daemonconf" | sudo tee /etc/supervisor/conf.d/daemon.conf

# Add configuration script to supervisord conf (if not there already)
if ! grep -Fxq "[include]" $config_file
    then
    echo "" | sudo tee -a $config_file
    echo "[include]" | sudo tee -a $config_file
    echo "files: /etc/supervisor/conf.d/*.conf" | sudo tee -a $config_file
fi

# if ! grep -Fxq "[unix_http_server]" $config_file
#    then
#    echo "" | sudo tee -a $config_file
#    echo "[unix_http_server]" | sudo tee -a $config_file
#    echo "file=/var/run/supervisor.sock" | sudo tee -a $config_file
#    echo "chmod=0700" | sudo tee -a $config_file
#fi

if ! grep -Fxq "[supervisord]" $config_file
    then
    # validate if path exists
    if [ ! -d /var/log/supervisor ]; then
        mkdir /var/log/supervisor
    fi
    echo "" | sudo tee -a $config_file
    echo "[supervisord]" | sudo tee -a $config_file
    echo "logfile=/var/log/supervisor/supervisord.log" | sudo tee -a $config_file
    echo "pidfile=/var/run/supervisord.pid" | sudo tee -a $config_file
    echo "childlogdir=/var/log/supervisor" | sudo tee -a $config_file
fi

if ! grep -Fxq "[inet_http_server]" $config_file
    then
    echo "" | sudo tee -a $config_file
    echo "[inet_http_server]" | sudo tee -a $config_file
    echo "port=127.0.0.1:9001" | sudo tee -a $config_file
fi

if ! grep -Fxq "[supervisorctl]" $config_file
    then
    echo "" | sudo tee -a $config_file
    echo "[supervisorctl]" | sudo tee -a $config_file
    # echo "serverurl=unix:///var/run/supervisor.sock" | sudo tee -a $config_file
    echo "serverurl=http://127.0.0.1:9001" | sudo tee -a $config_file
fi

if ! grep -Fxq "[rpcinterface:supervisor]" $config_file
    then
    echo "" | sudo tee -a $config_file
    echo "[rpcinterface:supervisor]" | sudo tee -a $config_file
    echo "supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface" | sudo tee -a $config_file
fi

# add alias to supervisord and supervisorctl
if ! grep -Fxq "alias supervisord" $config_file
    then
    echo "" | sudo tee -a ~/.bashrc
    echo alias supervisord=/usr/local/bin/supervisord | sudo tee -a ~/.bashrc
fi

if ! grep -Fxq "alias supervisord" $config_file
    then
    echo alias supervisorctl=/usr/local/bin/supervisorctl | sudo tee -a ~/.bashrc
fi

# sudo supervisorctl -c /etc/supervisor/supervisord.conf stop all
sudo supervisord -c $config_file
# Reread the supervisord config
sudo supervisorctl -c $config_file reread

# Update supervisord in cache without restarting all services
sudo supervisorctl -c $config_file update

# Start/Restart processes through supervisord
sudo supervisorctl -c $config_file restart daphne
sudo supervisorctl -c $config_file restart worker
# sudo /usr/local/bin/supervisorctl -c /etc/supervisor/conf.d/supervisord.conf restart celeryworker &
# sudo /usr/local/bin/supervisorctl -c /etc/supervisor/conf.d/supervisord.conf restart celeryheartbeat &