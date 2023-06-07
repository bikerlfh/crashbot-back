#!/usr/bin/env bash
#!/bin/bash

sudo chmod 777 /var/app/current/models_created

if ls /tmp/models_created/*.h5 1> /dev/null 2>&1; then
    sudo mv /tmp/models_created/*.h5 /var/app/current/models_created/
    echo "files .h5 moved successfully"
else
    echo "no files .h5 to move"
fi
