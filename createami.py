from __future__ import print_function
import boto3
import sys

import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# From http://cloud-images.ubuntu.com/locator/ec2/
# Choose the hvm:ebs-ssd "Instance Type" for say trusty us-east
#baseami = 'ami-5c207736'  # Trusty 14.04 amd64 hvm:ebs-ssd 2015-12-18
baseami = 'ami-43a15f3e' # 16.04, updated 2018-03-28
region = 'us-east-1'
ssh_keypair = 'domjudge-aws'
ssh_securitygroup = 'open-ssh'

cconfig = """#cloud-config
"""


cconfig_old = """#cloud-config
power_state:
  mode: poweroff
  timeout: 900
  condition: True
"""

udscript = """#!/bin/bash -ex

# cloudinit specifically does not define this, making the original script fail
# credit to https://github.com/ansible/ansible/issues/31617
export HOME=/root

# updating first
apt-get update

# install needed packages for ansible
apt-get install -y -q software-properties-common git-core
apt-add-repository -y ppa:ansible/ansible
apt-get update
apt-get install -y -q ansible

ansible-pull -U http://github.com/jjkjiang/domserver-ami.git -v -d /mnt/playbooks -i "localhost,"
# ansible-playbook -v -i "localhost," -c local local.yml

poweroff
"""

combined_message = MIMEMultipart()
sub_message = MIMEText(cconfig, "cloud-config", sys.getdefaultencoding())
sub_message.add_header('Content-Disposition', 'attachment; filename="00cloudconfig.txt"')
combined_message.attach(sub_message)

sub_message = MIMEText(udscript, "x-shellscript", sys.getdefaultencoding())
sub_message.add_header('Content-Disposition', 'attachment; filename="01bootstrap.txt"')
combined_message.attach(sub_message)

ec2 = boto3.resource('ec2', region_name=region)
instances = ec2.create_instances(
    ImageId=baseami,
    InstanceType='t2.micro',
    UserData=combined_message.as_string(),
    MinCount=1,
    MaxCount=1,
    KeyName=ssh_keypair,
    SecurityGroups=[ssh_securitygroup],
)
instance = instances[0]

print("Waiting for instance to boot")
while instance.state['Name'] != 'running':
    print(".", end='')
    sys.stdout.flush()
    time.sleep(5)
    instance.reload()
print()

print("Instance provisioning...")
print("Waiting for instance to stop")
while instance.state['Name'] != 'stopped':
    print(".", end='')
    sys.stdout.flush()
    time.sleep(5)
    instance.reload()
print()

exit()

ts = int(time.time())
image = instance.create_image(
    Name="DOMjudge-domserver-{0}".format(ts),
    Description="DOMjudge DOMServer {0}".format(ts)
)
instance.terminate()


print("Creating AMI {}".format(image.image_id))
print("Waiting for image creation to finish")
while image.state == 'pending':
    print(".", end='')
    sys.stdout.flush()
    time.sleep(5)
    image.reload()
if image.state == 'available':
    print("Image created successfully!")
    print("AMI ID: " + image.image_id)
else:
    print("Error creating image. Check AWS console for details")