# DOMjudge DOMserver AMI Creation
This repository automates the creation of an Amazon AMI that is ready to deploy
DOMjudge DOMserver(the web interface portion) onto. It basically installs
the necessary dependencies into an Ubuntu 14.04 image and configures apache2
in a way that we expect.

TODO: Link to the parent repository that uses this AMI(Currently unpublished)

## Dependencies
This script depends on boto3 to be present on your workstation.

#### Boto3
The python script depends on boto3 to communicate with the AWS API in order to
provision a virtual machine, set it up, and then create an AMI out of it.

##### Install boto3
```bash
pip install boto3
```
You can also install this in a virtual environment if you'd like.

##### Configure Boto3
Follow the steps here: http://boto3.readthedocs.org/en/latest/guide/quickstart.html#configuration

Basically, run `aws configure`, or edit the file `~/.aws/credentials` to contain:
```ini
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```

## Creating the AMI
Once you've set up boto3, you just need to run the `createami.py` script. When
it finishes it will print out the AMI ID. That's it!

You may want to edit the `createami.py` file to specify your AWS region and base
ami to start from. See comments in the file.

## Additional Information
### What's this thing actually do?
This script will launch an EC2 Virtual Machine. It instructs the VM to run
Ansible after booting and to evaluate the `local.yml` playbook from this
repository. After Ansible finishes, the Virtual Machine will power down.

While Ansible is doing it's thing on the VM the python script is simply waiting
in a loop for the virtual machine to power off. Once it does so, the script will
tell AWS to create an AMI based off that machine. The script waits for this process
to complete, then deletes the virtual machine.

Finally it will print out the AMI ID. You'll need this when you set up your
DOMjudge cluster.

You'll probably be charged for less than an hour's worth of EC2 time on a
t2.micro instance. Once the ami is created you'll be charged for storage of
the snapshot backing it. See the pricing page here for details:
https://aws.amazon.com/ebs/pricing/


### Hacking
If you wish to modify this repository, feel free to do so, however note that
you'll want to change the github url in the `createami.py` file to correspond
to your repository instead of mine. If you don't change it when the ami creation
process launches ansible it will continue to use my `local.yml` file.


## License
This repository is made available under the terms of the MIT License. See the
`LICENSE` file for more details.
