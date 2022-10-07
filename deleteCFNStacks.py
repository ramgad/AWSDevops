#!/usr/bin/env python
# coding: utf-8
# Author: Ramesh Gadamsetti

import os
import json
import logging
import argparse
import boto3
import sys
import time
import signal
from botocore.exceptions import ClientError

FORMAT = '%(asctime)s : %(levelname)s : %(message)s'
#logging.basicConfig(filename='deleteCFNstacks.log', level=logging.DEBUG, format=FORMAT)
logging.basicConfig(filename='pcs-decommission-stg-run1.log', level=logging.INFO, format=FORMAT)


retained_resources = ['LambdaSecurityGroup', ' PCSIACServicesCore-VPCID', 'PCSIACServicesCore-AppSubnetAZ2']

def deleteStack(stackToDelete):
    #load the client using app config or default
    client = boto3.client('cloudformation', region_name='us-west-2')

    try:

        # if args.retain and len(args.retain)>0:
        #     retained_respources = args.retain.split(",")
        
        logging.info (">>>>>>       Executing client.describe_stack(StackName=\"{}\")".format(stackToDelete))
        resp = client.describe_stacks(StackName=stackToDelete)

        if resp:
            logging.info (">>>>>>       Describe successful>>> Executing client.delete_stack(StackName=\"{}\", RetainResources={})".format(stackToDelete, retained_resources))
            response = client.delete_stack(StackName=stackToDelete)

        t_end = time.time() + (60 * 60) # Adding 90 minutes
        logging.info (">>>>>>       sleep till the '{}' is deleted or exit out after 900 seconds..  t_end is:{}".format(stackToDelete, t_end))
        time_elapsed =0
        while time.time() < t_end:
            resp1 = None
            resp1 = client.describe_stacks(StackName=stackToDelete)

            if resp1:
                if time_elapsed > 0:
                    logging.info (">>>>>>       In while loop.. Elapsed seconds are {}".format(time_elapsed))
                time.sleep(15)
                time_elapsed+=15
            else:
                logging.info (">>>>>>       Stack {} is not found now.. coming out of while loop now.. time now is {}".format(stackToDelete, time.time()))
                break


        # we expect a response, if its missing on non 200 then show response
        if 'ResponseMetadata' in response and \
            response['ResponseMetadata']['HTTPStatusCode'] < 300:
            logging.info("succeed. response: {0}".format(json.dumps(response)))
        else:
            logging.critical(">>>>>>       There was an Unexpected error. response: {0}".format(json.dumps(response)))

    except ClientError as e:
        if e.response["Error"]["Code"] == "ValidationError":
            # ignore the target exception
            logging.info(">>>>>>        The stack {} does not exists, continuing to the next one".format(stackToDelete))
            pass
            
    except ValueError as e:
        logging.critical(">>>>>>       Value error caught: {0}".format(e))
        sys.exit()

    except AttributeError as a:
        logging.warning(">>>>>>       The stack {} does not exists, continuing to the next one".format(stackToDelete))
        pass


    except BaseException as err:
        logging.critical(">>>>>>       Unexpected err=, {}".format(type(err)))
        sys.exit()


def main():
    seq = 1
    listOfStacksToDelete = [
                        'PCS-MultiRegionHealthStack-uw2', 
                        'PCSIACApigatewayRoute53',
                        'PCS-ForgeAuth-Alias-live',
                        'PCS-PCS-ForgeAuth-Permi',
                        'PCS-ForgeAuth-Alias-test',
                        'PCSForgeAuthIACLambda',
                        'PCS-ForgeAuth-IACRole',
                        'PCS-PCS-PriceCalculatorLambda-Permi-live',
                        'PCS-PriceCalculatorLambda-Alias-live',
                        'PCS-PCS-PriceCalculatorLambda-Permi-test',
                        'PCSIACAPIGateway',
                        'PCSIACApigatewayRole',
                        'PCS-PriceCalculatorLambda-Alias-test',
                        'PCSPriceCalculatorLambdaIACLambda',
                        'PCS-PriceCalculatorLambda-IACRole',
                        'PCSIACKMS',
                        'PCSIACEventBridgePolicies',
                        'PCSIACDynamoDBPolicies',
                        'PCSIACLambdaSG',
                        'PCSIACServicesCore'
                        ]

    logging.info('-'*88)
    logging.info(' Invoking deleteStacks for the given AWS profile/credentials, the input has {} stacks to delete'.format(len(listOfStacksToDelete)))
    logging.info('-'*88)

    for stack in listOfStacksToDelete:
        logging.info ("        Calling deleteStack for {}. {}".format(seq, stack))
        deleteStack(stack)
        seq += 1
        time.sleep(1)

    logging.info('-'*88)
    logging.info('        Completed the execution of the deleteStacks Script')
    logging.info('-'*88)

if __name__ == '__main__':
    main()
