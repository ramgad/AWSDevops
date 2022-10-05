# CopyRight Autodesk Inc. All Rights reserved
# Author: Ramesh Gadamsetti

from datetime import datetime, timedelta
from pprint import pprint
from botocore.exceptions import ClientError

import time
import logging
import boto3

# Helper function to get AWS account ID
def getAwsAccountId():
    id = boto3.client('sts').get_caller_identity().get('Account')
    print ("The AWS Account Id for this login is: {}".format(id))
    return id

# Helper function to determine if the AWS account Name contains prd
def isAwsAcctContainsPrd():
    client = boto3.client('iam')
    response = client.list_account_aliases()
    account_aliases = client.list_account_aliases()
    AcctName = account_aliases['AccountAliases'][0]
    if ('prd' in AcctName.lower()):
        print ('This is prod account and the AWS Account Name for this login is: {}'.format(AcctName))
        return True
    else:
        print ('This is nonprod account and the AWS Account Name for this login is: {}'.format(AcctName))
    return False

def extractLogGroupsFromAllPages():
    print ('')
    print('-'*88)
    print('Running -- extractLogGroupsFromAllPages method...')
    client = boto3.client('logs', region_name='us-west-2')
    response = client.describe_log_groups()
    newlist=[]
    paginator = client.get_paginator('describe_log_groups')
    for page in paginator.paginate():
        print('extractLogGroupsFromAllPages - Page change')
        for group in page['logGroups']:
            newlist.append(group['logGroupName'])
    print('-'*88)        
    return newlist;


def printLogGroupsRetention(inputList):
    print ('')
    print('-'*88)
    client = boto3.client('logs', region_name='us-west-2')
    for lgName in inputList:
        response = client.describe_log_groups(logGroupNamePrefix=lgName)
        retentionInDays = response['logGroups'][0].get('retentionInDays', 'Never Expire')
        print("{} : {}".format(lgName, retentionInDays))
    print('-'*88)
    #{'logGroups': [{'logGroupName': 'stage-dynamodb-pitr', 'creationTime': 1626816910297, 'metricFilterCount': 0, 'arn': 'arn:aws:logs:us-west-2:156067768658:log-group:stage-dynamodb-pitr:*', 'storedBytes': 9397}], 'ResponseMetadata': {'RequestId': '7438998f-05b7-48c3-bf32-dc43991d7e86', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '7438998f-05b7-48c3-bf32-dc43991d7e86', 'content-type': 'application/x-amz-json-1.1', 'content-length': '200', 'date': 'Wed, 05 Oct 2022 04:00:26 GMT'}, 'RetryAttempts': 0}}


# Driver Code

print('-'*88)
print (''' 
    This program utilizes the current AWS credentails/profile and dynamically sets Number of Days based on AccountName containing 'prd'
    For PROD accounts, iteratively modifies all log groups and sets the retention policy to 90 days
    For non-PROD accounts, iteratively modifies all log groups and sets the retention policy to 30 days
    
    ''')
print('-'*88)

listOfLogGroups = extractLogGroupsFromAllPages()
printLogGroupsRetention(listOfLogGroups)

setDays = 30 # default set to 30 days for nonprd
if isAwsAcctContainsPrd():
    setDays = 90

print('-'*88)
print ('    Updating all LogGroups iteratively with {} days'.format(setDays))

client = boto3.client('logs', region_name='us-west-2')

for i in listOfLogGroups:
    log=client.put_retention_policy(
        logGroupName=i,
        retentionInDays=setDays
    )
    print(log)

print('-'*88)
print('    COMPLETED SUCCESSFULLY')
print('-'*88)

# if __name__ == '__main__':
#     cwInstance = AdskLogsGroupRetentionPolicyWrapper()
#     print ("calling Driver Main")
#     cwInstance.driver_main()


