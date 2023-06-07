#!/usr/bin/env bash
#!/bin/bash

if [ ! -d /tmp/models_created ]; then
    mkdir /tmp/models_created
    sudo chmod 777 /tmp/models_created
    echo "create temporal models_created directory"
fi

if ls /var/app/current/models_created/*.h5 1> /dev/null 2>&1; then
    sudo cp /var/app/current/models_created/*.h5 /tmp/models_created/
    echo "files .h5 copied successfully"
else
    echo "no files .h5 to copy"
fi
