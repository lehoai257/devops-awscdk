import boto3
import botocore
import time
 
def lambda_handler(event, context):
    try:
        ssm = boto3.client('ssm')
        def getInstanceSSMList():
            ssmResponse = ssm.describe_instance_information()
            instanceInformationList = ssmResponse['InstanceInformationList']
            while 'NextToken' in ssmResponse:
                ssmResponse = ssm.describe_instance_information(
                    NextToken=ssmResponse['NextToken']
                )
                instanceInformationList.extend(ssmResponse['InstanceInformationList'])
                
            instanceSSMList = []
            for InstanceInformation in instanceInformationList:
                serverDict = {}
                serverDict['Instance ID'] = InstanceInformation['InstanceId']
                instanceSSMList.append(serverDict)
            return instanceSSMList

        def sendCommand(instanceId):
            response = ssm.send_command(
                DocumentName='AWS-RunShellScript',
                InstanceIds=[instanceId],
                Parameters={"commands": ["sudo yum install unzip", "cd /tmp", "aws s3 cp s3://tomcat-simple-web/index.zip .","unzip -o index.zip"]},
            )
            return response    

        def zipFileHandle(instanceList):
            for instance  in instanceList:
                response= sendCommand(instance['Instance ID'])    
                commandId = response['Command']['CommandId']
                keepWaiting = None    
                while keepWaiting is None:
                    commandResponse = ssm.list_commands(CommandId=commandId)
                    if(commandResponse['Commands'][0]['Status'] == 'InProgress' or commandResponse['Commands'][0]['Status'] == 'Pending'):
                        time.sleep(2)
                    else:
                        keepWaiting = 1
        
        instanceList = getInstanceSSMList()
        zipFileHandle(instanceList)                

    except botocore.exceptions.ClientError as e:
        print("unexpected error: %s" % (e.response))
