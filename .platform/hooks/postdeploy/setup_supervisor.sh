# declare supervisord config file
config_file="/etc/supervisor/supervisord.conf"
# Get django environment variables
# djangoenv=`export | tr '\n' ',' | sed 's/declare -x //g'  | sed 's/%/%%/g' | sed 's/export //g' | sed 's/$PATH/%(ENV_PATH)s/g' | sed 's/$PYTHONPATH//g' | sed 's/$LD_LIBRARY_PATH//g'`
djangoenv="DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE,RDS_DB_NAME=$RDS_DB_NAME,RDS_HOSTNAME=$RDS_HOSTNAME,RDS_PASSWORD=$RDS_PASSWORD,RDS_PORT=$RDS_PORT,RDS_USERNAME=$RDS_USERNAME,REDIS_HOSTNAME=$REDIS_HOSTNAME,REDIS_PORT=$REDIS_PORT,DEFAULT_SEQ_LEN=$DEFAULT_SEQ_LEN,GENERATE_AUTOMATIC_MODEL_TYPES=$GENERATE_AUTOMATIC_MODEL_TYPES,EPOCHS_SEQUENTIAL_LSTM=$EPOCHS_SEQUENTIAL_LSTM,PERCENTAGE_ACCEPTABLE=$PERCENTAGE_ACCEPTABLE,PERCENTAGE_MODEL_TO_INACTIVE=$PERCENTAGE_MODEL_TO_INACTIVE,DIFF_MULTIPLIERS_TO_GENERATE_NEW_MODEL=$DIFF_MULTIPLIERS_TO_GENERATE_NEW_MODEL,NUMBER_OF_MODELS_TO_PREDICT=$NUMBER_OF_MODELS_TO_PREDICT,NUMBER_OF_MULTIPLIERS_TO_EVALUATE_MODEL=$NUMBER_OF_MULTIPLIERS_TO_EVALUATE_MODEL"
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

environment=$djangoenv

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

environment=$djangoenv
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


# Reread the supervisord config
sudo supervisorctl -c $config_file reread

# Update supervisord in cache without restarting all services
sudo supervisorctl -c $config_file update

# Start/Restart processes through supervisord
sudo supervisorctl -c $config_file restart daphne
sudo supervisorctl -c $config_file restart worker
# sudo /usr/local/bin/supervisorctl -c /etc/supervisor/conf.d/supervisord.conf restart celeryworker &
# sudo /usr/local/bin/supervisorctl -c /etc/supervisor/conf.d/supervisord.conf restart celeryheartbeat &