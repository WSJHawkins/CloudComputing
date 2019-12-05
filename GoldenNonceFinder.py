# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 15:48:10 2019

@author: wsjha
"""

import boto3
import sys
import hashlib
import time


string = "COMSM0010cloud"
nonceFound = False
nonce = 0
start = 0
end = 0
    
#if len(sys.argv) == 4:
#    script, var1, var2, var3 = sys.argv
#
#
#    session = boto3.Session(region_name='us-east-1',
#        aws_access_key_id=var1,
#        aws_secret_access_key=var2,
#        aws_session_token=var3,
#    )
    
    
session = boto3.Session(region_name='us-east-1' )
    
sqs = session.resource('sqs')

# Get the queues
receiveQueue = sqs.get_queue_by_name(QueueName='JobSubmit')
sendQueue = sqs.get_queue_by_name(QueueName='Response')

running = True

onMessage=str(time.time())
response = sendQueue.send_message(MessageBody=onMessage)
while (running):
    # Process messages
    message = receiveQueue.receive_messages(MaxNumberOfMessages=1)
    if(len(message) > 0):
        message = message[0]
        if(message.body == "end"):
            running = False
            returnMessage = "VM Shutting Down"
            response = sendQueue.send_message(MessageBody=returnMessage)
            # Let the queue know that the message is processed
            message.delete()
        else:
            nonceFound = False
            arr = message.body.split()
            start = int(arr[0])
            end = int(arr[1])
            difficulty = int(arr[2])
            string = arr[3]
            #print ("New Job: "+message.body)
            # Let the queue know that the message is processed
            message.delete()
            
            nonce = start
            goldenNonce = 0
            for nonce in range(start,end):
                binaryString = str(bin(int(hashlib.sha256((string+str(nonce)).encode('utf8')).hexdigest(),16)))[2:]
                if(256-len(binaryString) >= difficulty):
                    nonceFound = True
                    goldenNonce = nonce
                    break
            
            # Create a new message
            if (nonceFound):  
                returnMessage = "Found Golden Nonce:"+ str(goldenNonce)
            else:
                returnMessage = "Not found in range: " +  str(start) +" - " + str(end)
            #send message
            #print (returnMessage)
            response = sendQueue.send_message(MessageBody=returnMessage)
    time.sleep(1)
    
    
        

            

    