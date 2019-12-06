# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 14:08:39 2019

@author: Will
"""

import math
import boto3
import json
from pkg_resources import resource_filename
import time
import keyboard

def isANum(a,min,max):
    try:
        int(a)
        bool_a = True
    except:
        bool_a = False
        
    if(bool_a):
        if(int(a) < min or int(a) > max):
            bool_a = False
    return bool_a

def isAFloat(a,min,max):
    try:
        float(a)
        bool_a = True
    except:
        bool_a = False
        
    if(bool_a):
        if(float(a) < min or float(a) > max):
            bool_a = False
    return bool_a

# Search product filter
FLT = '[{{"Field": "tenancy", "Value": "shared", "Type": "TERM_MATCH"}},'\
      '{{"Field": "operatingSystem", "Value": "{o}", "Type": "TERM_MATCH"}},'\
      '{{"Field": "preInstalledSw", "Value": "NA", "Type": "TERM_MATCH"}},'\
      '{{"Field": "instanceType", "Value": "{t}", "Type": "TERM_MATCH"}},'\
      '{{"Field": "location", "Value": "{r}", "Type": "TERM_MATCH"}}]'

# Get current AWS price for an on-demand instance
def get_price(region, instance, os):
    f = FLT.format(r=region, t=instance, o=os)
    data = client.get_products(ServiceCode='AmazonEC2', Filters=json.loads(f))
    od = json.loads(data['PriceList'][0])['terms']['OnDemand']
    id1 = list(od)[0]
    id2 = list(od[id1]['priceDimensions'])[0]
    return od[id1]['priceDimensions'][id2]['pricePerUnit']['USD']

# Translate region code to region name
def get_region_name(region_code):
    default_region = 'EU (Ireland)'
    endpoint_file = resource_filename('botocore', 'data/endpoints.json')
    try:
        with open(endpoint_file, 'r') as f:
            data = json.load(f)
        return data['partitions'][0]['regions'][region_code]['description']
    except IOError:
        return default_region
    

#Fixed
OpsPerSec = 277813
client = boto3.client('pricing', region_name='us-east-1')
costPerHour = float(get_price(get_region_name('us-east-1'), 't2.micro' , 'Linux'))
print("Welcome To Golden Nonce Discovery!")

difficulty = input ("What difficulty would you like: ")
while (not isANum(difficulty,1,99)):
    print("Invalid Input - It should be a postive integer")
    difficulty = input ("What difficulty would you like: ")
difficulty = int(difficulty)
    
print("Which Mode would you like: ")
print("    1. Specify how many VMs to use")
print("    2. Specify desired time and confidence level")
print("    3. Specify maximum hourly rate of expenditure")
mode = input("Enter Number Of Mode: ")
while (not isANum(mode,1,3)):
    print("Invalid Input - Please enter 1, 2 or 3")
    mode = input("Enter Number Of Mode: ")
mode = int(mode)

if mode == 1:
    numberOfVMs = input("Enter Number of VMs to use: ")
    while (not isANum(numberOfVMs,1,99)):
        print("Invalid Input - Please enter a postive integer")
        numberOfVMs = input("Enter Number of VMs to use: ")
    numberOfVMs = int(numberOfVMs)
    
elif mode == 2:
    desiredTime = input("Enter desired time (in seconds): ")
    while (not isAFloat(desiredTime,60,999999)):
        print("Invalid Input - Please enter a number greater than 60 (59 Seconds needed to start up VM)")
        desiredTime = input("Enter desired time (in seconds): ")
    desiredTime = float(desiredTime)
    desiredTime = desiredTime - 59
    confidence = input("Enter Confidence Level (in percent) - e.g. 95.0: ")
    while (not isAFloat(confidence,0,99.999)):
        print("Invalid Input - Please enter a postive number from 1 - 99.999")
        confidence = input("Enter Confidence Level (in percent) - e.g. 95.0: ")
    confidence = float(confidence)
    confidence = confidence/100
    
    #N = ln(1-C) / -TZ(1/2)^D
    numberOfVMs = math.ceil((   -math.log(1-confidence) / (desiredTime*OpsPerSec*pow((1/2),difficulty))    ))
    print("Number of VMs: "+str(numberOfVMs))
    
elif mode == 3:

    expenditure = input("Enter max hourly rate of expenditure (in cents). One VM is "+str(costPerHour) +" cents per hour : ")
    while (not isAFloat(expenditure,0,9999)):
        print("Invalid Input - Please enter a postive integer")
        expenditure = input("Enter max hourly rate of expenditure (in cents):")
    expenditure = float(expenditure)
    numberOfVMs = math.floor(expenditure / costPerHour)
    print("Number of VMs: "+str(numberOfVMs))
    #could include SQS Pricing too


limits = input("Do you wish to set any limits. Enter 0 for no limits, 1 for a time limit, 2 for a spend limit: ")
while (not isANum(limits,0,2)):
    limits = input("Invalid Input - Please enter either 0, 1 or 2: ")
limits = int(limits)
timeLimit = -1 #stands for no limit
if(limits == 1):
    timeLimit = input("Enter a time limit (in seconds): ")
    while (not isAFloat(timeLimit,0.01,999999)):
        print("Invalid Input - Please enter a number greater than 0.01")
        timeLimit = input("Enter a time limit  (in seconds): ")
    timeLimit = float(timeLimit)
elif(limits == 2):
    costLimit = input("Enter max spend limit (in cents): ")
    while (not isAFloat(costLimit,0,9999)):
        print("Invalid Input - Please enter a postive integer")
        costLimit = input("Enter max spend limit (in cents): ")
    costLimit = float(costLimit)
    timeLimit = costLimit/(costPerHour*numberOfVMs) * 60 * 60


##START ACTUAL CND SYSTEM
print("Starting Up Now with difficulty " + str(difficulty) + ", and " +str(numberOfVMs)+" VMS")
print("Press 'Esc' at any point to initate a scram and shut the program down")
# Get the service resource
sqs = boto3.resource('sqs')
ec2 = boto3.resource('ec2')

user_data = "#!/bin/bash \n source /home/ec2-user/venv/python3/bin/activate \n python /home/ec2-user/GoldenNonceFinder.py"
            
searchSpace = pow(2,32) 
dataBlock = "COMSM0010cloud"
start = time.time()
startLocation = 0
nonceFound = False


#Create Queues
print("Creating Queues")
sendQueue = sqs.create_queue(QueueName='JobSubmit', Attributes={'DelaySeconds': '0'})
receiveQueue = sqs.create_queue(QueueName='Response', Attributes={'DelaySeconds': '0'})

#Start up EC2
print("Starting Up Instances")
instances = ec2.create_instances(ImageId='ami-038940a82ab03354b', MinCount=1, MaxCount=numberOfVMs, UserData=user_data, InstanceType='t2.micro',IamInstanceProfile={'Name': 'SQSRole'},SecurityGroups=['NoOutsideCOnnections',])

####Send Jobs To Queue and monitor responses
print("Sending Jobs")

startLocation = 0
for j in range(0,numberOfVMs):
    end = startLocation + math.floor(searchSpace/numberOfVMs)
    if (j == 0):
        end = end + searchSpace%numberOfVMs
        x = str(startLocation) + " " + str(end) + " " + str(difficulty) + " " + dataBlock
        startLocation = end
        response = sendQueue.send_message(MessageBody=x)


scramInitiate = False
while (nonceFound == False and scramInitiate == False):
    
    if(keyboard.is_pressed('Esc')):
        answer = input ("Are you sure you want to intiate a Scram? Enter 'Y' to confirm: ")
        if(answer == 'Y' or answer == 'y'):
            print("Starting Scram")
            scramInitiate = True
    
    if((time.time()-start) > timeLimit and timeLimit != -1):
        print("Time/Cost Limit reached - Initiating Scram")
        scramInitiate = True #init
            
    ####Check Responses
    message = receiveQueue.receive_messages(MaxNumberOfMessages=1)
    if(len(message) > 0):
        message = message[0]                   
        if(message.body[0] == "F"):
            nonceFound = True
            print(message.body)            
        message.delete()
    
    time.sleep(1)
        
##SHUTDOWN ALL INSTANCES
print("Shutting Down All EC2 Instances")
instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
instances = ec2.instances.all()
for instance in instances:
    instance2 = ec2.Instance(instance.id)
    response = instance2.terminate()
    #print (response)

##Delete Queues
print("Deleting Queues")
sendQueue.delete()
receiveQueue.delete()
end = time.time()
print("All Finished and Shutdown")
print("Time Taken: "+str(end - start))
