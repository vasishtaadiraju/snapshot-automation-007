# snapshot-automation-007
A demo project to manage AWS EC2 instances' snapshots


## About

This project is a demo and uses boto3 a python library compatible with AWS to manage EC2 instances' snapshots

# Configuring

Snapster uses the configuration file created by the AWS CLI

eg: `aws configure --profile jeff`


#Running

`pipenv run python snapster/snapster.py <command> <subcommand>
<--project=PROJECT>`

#Help Command

`pipenv run python snapster/snapster.py --help`

*commands* are instances, volumes, snapshots
*subcommand* - depends on the command
*project is optional
