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
# . /opt/elasticbeanstalk/deployment/env


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

#. /opt/elasticbeanstalk/deployment/env && cat .ebextensions/supervisor/supervisord.conf > /etc/supervisor/supervisord.conf
#. /opt/elasticbeanstalk/deployment/env && cat .ebextensions/supervisor/supervisord.conf > /etc/supervisord.conf
#. /opt/elasticbeanstalk/deployment/env && cat .ebextensions/supervisor/supervisor_laravel.conf > /etc/supervisor/conf.d/supervisor_laravel.conf

if ps aux | grep "[/]usr/local/bin/supervisord"; then
    echo "supervisor is running"
    sudo supervisorctl -c $config_file stop all
    echo "supervisor stopped"
else
    echo "starting supervisor"
    # sudo supervisord -c $config_file
fi

# /usr/local/bin/supervisorctl reread
# /usr/local/bin/supervisorctl update

echo "Supervisor Running!"