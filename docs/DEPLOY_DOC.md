# INSTALLATION


## install nvidia drivers

https://www.linuxcapable.com/install-nvidia-drivers-on-ubuntu-linux/


# ENVIRONMENT VARIABLES

## PREDICTION

* MIN_PROBABILITY_TO_EVALUATE_MODEL: (float) minimum probability to evaluate model. The prediction's probability must be greater than this value to be considered. Default: 0.5



# DEPLOY IN AWS ELASTIC BEANSTALK

## init eb

Use the virginia region and python 3.11

```
eb init -v
```

## Create environment

Use the ec2 t3a.small instance minimum

```
eb create -i t3a.small -v
```

## Deploy

```
eb deploy -v
```

## create a ElastiCache Redis

Create a elasticache redis in the same VPC of the elastic beanstalk environment
Copy the endpoint of the redis and add it to the environment variables REDIS_HOSTNAME

## Create a S3 bucket

Create a S3 bucket and add the name to the environment variables AWS_STORAGE_BUCKET_NAME

## Create a RDS Postgres

Create a RDS Postgres from the AWS elasticbeanstalk configuration

## Update environment variables
add the elastic beanstalk domain

usage: eb setenv [VAR_NAME=KEY ...]

```
REDIS_HOSTNAME=redis
ALLOWED_HOSTS=["your-domain.com", "ebsdomain.com"]
DOMAIN_NAME=your-domain.com  # this is the domain of the elastic beanstalk or your custom domain (necessary for the websocket)
SECRET_KEY=secret_key
AWS_ACCESS_KEY_ID=aws_access_key_id
AWS_SECRET_ACCESS_KEY=aws_secret_access_key
AWS_STORAGE_BUCKET_NAME=aws_storage_bucket_name
```

## create a superuser

The hook 99_create_superuser.sh will create a superuser with the credentials. You need change the password of the superuser.
With ssh access to the ec2 instance
In this file you get all environment variables /opt/elasticbeanstalk/deployment/env copy and export all variables

execute the following command

```
source /var/app/venv/*/bin/activate && python /var/app/current/manage.py changepassword
```

## Open 5000 port in balancer

Open the 5000 port in the balancer to access the websocket. You can do this in the aws elasticbeanstalk configuration