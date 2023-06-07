if [ ! -d /tmp/models_created ]; then
    mkdir /tmp/models_created
    sudo chmod 777 /tmp/models_created
    echo "create temporal models_created directory"
fi

sudo cp /var/app/current/models_created/*.h5 /tmp/models_created/