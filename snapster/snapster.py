import boto3
import botocore
import click

session = boto3.Session(profile_name='vamos')
ec2 = session.resource('ec2')

def filter_instances(project):
    instances = []

    if project:
        filters = [{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    return instances

def snapshot_in_progress(volume):
    snapshots = list(volume.snapshots.all())
    return snapshots and snapshots[0].state == 'pending'

@click.group()
def cli():
    """Snapster manages the EC2 instances' snapshots"""

@cli.group('snapshots')
def snapshots():
    """Commands for snapshots"""

@snapshots.command('list')
@click.option('--project', default=None,
    help="Only snapshots for project (tag Project:<name>)")
@click.option('--all', 'list_all', default=False, is_flag=True,
    help="List all snapshots for each volume, not just the most recent")
def list_snapshots(project, list_all):
    "List EC2 snapshots"

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

                if s.state == 'completed' and not list_all: break

    return

@cli.group('volumes')
def volumes():
    """Commands for volumes"""

@volumes.command('list')
@click.option('--project', default=None,
    help="Only volumes for project (tag Project:<name>)")
def list_volumes(project):
    "List EC2 volumes"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            print(", ".join((
                v.id,
                i.id,
                v.state,
                str(v.iops),
                str(v.size) + "GiB",
                v.encrypted and "Encrypted" or "Not Encrypted"
            )))

    return

@cli.group('instances')
def instances():
    """Commands for instances"""

@instances.command('snapshot',
    help="Create snapshots of all volumes")
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
def create_snapshots(project):
    "Create snapshots for EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print("Stopping the instance {0}...".format(i.id))

        i.stop()
        i.wait_until_stopped()

        for v in i.volumes.all():
            if snapshot_in_progress(v):
                print("  Skipping {0}, snapshot already in progress".format(v.id))
                continue

            print("  Creating snapshot of {0}".format(v.id))
            v.create_snapshot(Description="Created by Snapster-007")

        print("Starting the instance {0}...".format(i.id))

        i.start()
        i.wait_until_running()

    print("Process Completion Successful!")

    return

@instances.command('list')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
def list_instances(project):
    "List all EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        tags = { t['Key']: t['Value'] for t in i.tags or [] }
        print(', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
            i.hypervisor,
            i.architecture,
            i.public_ip_address,
            tags.get('Project', '<no project>')
            )))

    return

@instances.command('stop')
@click.option('--project', default=None,
  help='Only instances for project')
def stop_instances(project):
    "Stop EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print("Stopping the instance {0}...".format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print(" Could not stop the instance {0}. ".format(i.id) + str(e))
            continue

    return


@instances.command('start')
@click.option('--project', default=None,
  help='Only instances for project')
def start_instances(project):
    "Start EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print("Starting the instance {0}...".format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print(" Could not start the instance {0}. ".format(i.id) + str(e))
            continue

    return

@instances.command('terminate')
@click.option('--project', default=None,
  help='Only instances for project')
def terminate_instances(project):
    "Terminate EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print("Terminating the instance {0}...".format(i.id))
        try:
            i.terminate()
        except botocore.exceptions.ClientError as e:
            print(" Could not terminate the instance {0}. ".format(i.id) + str(e))
            continue

    return


if __name__ == '__main__':
    cli()
