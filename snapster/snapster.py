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
def cli():

    """ Snapster manages the snapshots process of EC2 instances"""

@cli.group('snapshots')
def snapshots():
    """Commands for Snaphsots"""

@snapshots.command('list')
@click.option('--project', default=None,
    help="Only Snapshots for project (tag Project:<name>)")
def list_snapshots(project):
    "List EC2 Snapshots"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(", ".join((
                    i.id,
                    v.id,
                    s.id,
                    s.state,
                    s.progress,
                    s.encrypted and "Encrypted" or "Not Encrypted",
                    s.start_time.strftime("%c")
                )))

    return

@cli.group('volumes')
def volumes():
    """Commands for volumes"""
@volumes.command('list')
@click.option('--project', default=None,
    help="Only volumes for project (tag Project:<name>)")
def list_volumes(project):
    "List EC2 Volumes"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            print(", ".join((
            i.id,
            v.id,
            v.state,
            str(v.size) + "GiB",
            v.encrypted and "Encrypted" or "Not Encrypted"
            )))
    return

@cli.group('instances')

def instances():

    """Commands for instances """
@instances.command('snapshot', help="Create snapshots of EC2 instances' volumes")
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")

def create_snapshots(project):
    """Create Snapshots for EC2 instances"""

    instances = filter_instances(project)

    for i in instances:

        print("Stopping Instance {0}..".format(i.id))

        i.stop()
        i.wait_until_stopped()

        for v in i.volumes.all():

            print("Creating Snapshot of {0}".format(v.id))
            v.create_snapshot(Description="Created by Snapster 007")

        print("Starting Instance {0}..".format(i.id))

        i.start()
        i.wait_until_running()

    print("Process Successfully Completed")
    return

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

    cli()
