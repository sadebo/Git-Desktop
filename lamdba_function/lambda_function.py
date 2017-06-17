import boto3
import datetime
import pytz

ec2 = boto3.resource('ec2')
# initialization lambda function.
def lambda_handler(event, context):
    print("\n\n Snapshot backups starting at %s" % datetime.datetime.now())
#Creating filter to get instances that are tagged with "Backup" or "backup" and that are also running
    instances = ec2.instances.filter(

        Filters=[{
                'Name': 'instance-state-name', 
                'Values': ['running']
            },
            {
                'Name': 'tag-key', 
                'Values': ['backup', 'Backup']
            }
        ]
    )
#iterate through each instance to instance name and also the devices that will be backed up (e.g /dev/sda)   
    for instance in instances:

        instance_name = filter(lambda tag: tag['Key'] == 'Name', instance.tags)[0]['Value']

        for volume in ec2.volumes.filter(Filters=[{'Name': 'attachment.instance-id', 'Values': [instance.id]}]):

           description = 'sanu-%s.%s-%s' % (instance_name, volume.attachments[0]['Device'],
                datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
#               
        if volume.create_snapshot(VolumeId=volume.volume_id, Description=description):
            print("Snapshot created with description [%s]" % description)
#Delete backup that are older than 30 days
        for snapshot in volume.snapshots.all():
            retention_days = 30
            if snapshot.description.startswith('sanu-') and ( datetime.datetime.now().replace(tzinfo=None) - snapshot.start_time.replace(tzinfo=None) ) > datetime.timedelta(days=retention_days):
                print("\t\tDeleting snapshot [%s - %s]" % ( s.snapshot_id, snapshot.description ))
                snapshot.delete()

    print("\n\nAWS snapshot backups completed at %s" % datetime.datetime.now())
    return True