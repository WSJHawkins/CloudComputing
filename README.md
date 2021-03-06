## CloudComputing - WH16862

A repository for comsm0010_cw coursework containing all the relevant source code.

LocalScript.py is the script to be run locally. GoldenNonceFinder.py is the python script that runs on an EC2 instance in the cloud. The GoldenNonceFinder.py is already loaded into a public AMI which the local script calls.

# How to use
To run LocalScript.py the following libraries are needed: math, boto3, json, pkg_resources, time, keyboard. 

For Boto3 to work you need to make sure your AWS credentials are in the below format and placed in  `~/.aws/credentials`
```shell
aws_access_key_id= Yourawsaccesskeyid    
aws_secret_access_key= Yourawssecretaccesskey 
 ```
 
You need to create an IAM role with AWS that has permissions to create, read, write and delete queues in SQS. If possible name the role 'SQSRole', if not update the LocalScript.py with the name of the role.

Set up a security group which allows no outside connects and call it 'NoOutsideCOnnections', if the name is not possible update the LocalScript.py with the name of the group.

To start the program run `python LocalScript.py` and enter the parameters it asks for.
```shell
Welcome To Golden Nonce Discovery!

What difficulty would you like: 26
Which Mode would you like: 
    1. Specify how many VMs to use
    2. Specify desired time and confidence level
    3. Specify maximum hourly rate of expenditure

Enter Number Of Mode: 1

Enter Number of VMs to use: 5

Do you wish to set any limits. Enter 0 for no limits, 1 for a time limit, 2 for a spend limit: 0
Starting Up Now with difficulty 26, and 5 VMS
Press 'Esc' at any point to initate a scram and shut the program down
 ```
## Troubleshooting
The ami used is public but if needed, you can recreate the ami by:
  1. Launching a 't2.micro' instance with the 'Amazon Linux 2' Image using your own SSH keys.
  2. SSH into the instance once it has started.
  3. Run the following commands:
```shell
sudo yum update
sudo yum install python3 -y
pip3 install --user virtualenv
mkdir venv
cd venv
virtualenv -p /usr/bin/python3 python3
source /home/ec2-user/venv/python3/bin/activate
pip3 install boto
 ```
  4. Close the SSH connections.
  5. Using SFTP transfer GoldenNonceFinder.py onto the instance
  6. Create the image from this instance.
  7. Insert this new AMI identifier into the LocalScript.py code
