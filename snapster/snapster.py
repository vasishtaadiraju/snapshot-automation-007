import boto3
import click

session = boto3.Session(profile_name='vamos')
ec2 = session.resource('ec2')

def filter_instances(project):

    instances =[]

    if project:

        filters = [{'Name':'tag:Project','Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:

        instances =ec2.instances.all()

    return instances

@click.group()
def instances():

    """Commands for instances """

@instances.command('list')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
def list_instances(project):
    "List EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        tags = { t['Key']: t['Value'] for t in i.tags or [] }
        print(', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
            i.architecture,
            i.hypervisor,
            i.image_id,
            tags.get('Project', '<No such Project>')
            )))

    return

@instances.command('stop')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
def stop_instances(project):

    """Stopping EC2 instances """

    instances = filter_instances(project)

    for i in instances:
        print("Stopping {0}..".format(i,id))
        i.stop()

    return

@instances.command('start')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
def start_instances(project):

    """Starting EC2 instances """
    instances = filter_instances(project)

    for i in instances:
        print("Starting {0}..".format(i,id))
        i.start()

    return

@instances.command('terminate')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
def terminate_instances(project):

    """Terminating EC2 instances """
    instances = filter_instances(project)

    for i in instances:
        print("Terminating {0}..".format(i,id))
        i.terminate()

    return

if __name__ == '__main__':

    instances()
