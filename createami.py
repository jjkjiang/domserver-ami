#!/usr/bin/env python
from __future__ import print_function
import boto.ec2
import sys

import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# From http://cloud-images.ubuntu.com/locator/ec2/
# Choose the hvm:ebs-ssd "Instance Type" for say trusty us-east
#baseami = 'ami-fdb9fc98'  # Trusty 14.04 amd64 hvm:ebs-ssd 2015-09-28
baseami = 'ami-5c207736'  # Trusty 14.04 amd64 hvm:ebs-ssd 2015-12-18
region = 'us-east-1'
#ssh_keypair = 'domjudge-aws'
#ssh_securitygroup = 'open-ssh'

cconfig = """#cloud-config
power_state:
  mode: poweroff
  timeout: 900
  condition: True
"""

udscript = """#!/bin/bash -ex

# install needed packages for ansible
apt-get install -y -q software-properties-common git-core
apt-add-repository -y ppa:ansible/ansible
apt-get update
apt-get install -y -q ansible

ansible-pull -U http://github.com/ubergeek42/domserver-ami.git -d /mnt/playbooks -i "localhost,"

exit 0
"""
combined_message = MIMEMultipart()
sub_message = MIMEText(cconfig, "cloud-config", sys.getdefaultencoding())
sub_message.add_header('Content-Disposition', 'attachment; filename="00cloudconfig.txt"')
combined_message.attach(sub_message)

sub_message = MIMEText(udscript, "x-shellscript", sys.getdefaultencoding())
sub_message.add_header('Content-Disposition', 'attachment; filename="01bootstrap.txt"')
combined_message.attach(sub_message)

conn = boto.ec2.connect_to_region(region)
reservation = conn.run_instances(
    baseami,
    #key_name=ssh-keypair,
    #security_groups=[ssh_securitygroup],
    instance_type='t2.micro',
    user_data=combined_message.as_string()
)
instance = reservation.instances[0]

print("Waiting for instance to boot")
while instance.state != 'running':
    print(".", end='')
    sys.stdout.flush()
    time.sleep(5)
    instance.update()
print()

print("Instance provisioning...")
print("Waiting for instance to stop")
while instance.state != 'stopped':
    print(".", end='')
    sys.stdout.flush()
    time.sleep(5)
    instance.update()
print()

ts = int(time.time())
newami_id = conn.create_image(instance.id, "DOMjudge-domserver-{0}".format(ts), description="DOMjudge DOMserver {0}".format(ts))
instance.terminate()

print("DOMjudge DOMserver Created")
print("AMI ID: " + newami_id)

print("Waiting for image creation to finish")
image = conn.get_all_images(image_ids=[newami_id])[0]
while image.state == 'pending':
    print(".", end='')
    sys.stdout.flush()
    time.sleep(5)
    image.update()
if image.state == 'available':
    print("Image created successfully!")
    print("AMI ID: " + newami_id)
else:
    print("Error creating image. Check AWS console for details")
